#!/usr/bin/env python3
"""
Vera AI Bot Server — Challenge submission

Endpoints:
  POST /v1/context      — Receive context updates (category, merchant, customer, trigger)
  POST /v1/tick         — Periodic wake-up; compose and send proactive messages
  POST /v1/reply        — Handle merchant/customer replies to previous messages
  GET /v1/healthz       — Liveness probe
  GET /v1/metadata      — Bot identity and approach
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal, Any, Dict
import json
from datetime import datetime
import uuid
import os
from pathlib import Path
from vera_composer import compose, compose_to_dict

app = FastAPI(title="Vera AI Bot", version="1.0.0")

# Global state
contexts_store = {
    "category": {},      # {context_id: (version, payload)}
    "merchant": {},      # {context_id: (version, payload)}
    "customer": {},      # {context_id: (version, payload)}
    "trigger": {},       # {context_id: (version, payload)}
}

conversations_store = {}  # {conversation_id: {...}}
start_time = datetime.now()

# ===== Request/Response Models =====

class ContextPush(BaseModel):
    scope: Literal["category", "merchant", "customer", "trigger"]
    context_id: str
    version: int
    payload: dict
    delivered_at: str

class ContextResponse(BaseModel):
    accepted: bool
    ack_id: Optional[str] = None
    reason: Optional[str] = None
    current_version: Optional[int] = None
    stored_at: Optional[str] = None

class TickRequest(BaseModel):
    now: str
    available_triggers: list[str]

class TickAction(BaseModel):
    conversation_id: str
    merchant_id: str
    customer_id: Optional[str]
    send_as: Literal["vera", "merchant_on_behalf"]
    trigger_id: str
    template_name: str
    template_params: list[str]
    body: str
    cta: str
    suppression_key: str
    rationale: str

class TickResponse(BaseModel):
    actions: list[TickAction]

class ReplyRequest(BaseModel):
    conversation_id: str
    merchant_id: Optional[str] = None
    customer_id: Optional[str] = None
    from_role: Literal["merchant", "customer"]
    message: str
    received_at: Optional[str] = None
    turn_number: int

class ReplyAction(BaseModel):
    action: Literal["send", "wait", "end"]
    body: Optional[str] = None
    cta: Optional[str] = None
    wait_seconds: Optional[int] = None
    rationale: str

class HealthResponse(BaseModel):
    status: str
    uptime_seconds: int
    contexts_loaded: dict

class MetadataResponse(BaseModel):
    team_name: str
    team_members: list[str]
    model: str
    approach: str
    contact_email: str
    version: str
    submitted_at: str

# ===== Helper Functions =====

def compose_message(
    category: Dict,
    merchant: Dict,
    trigger: Dict,
    customer: Optional[Dict] = None,
) -> tuple:
    """
    Compose a message using the deterministic Vera composer.
    
    Returns: (body, cta, rationale)
    """
    try:
        msg = compose(category, merchant, trigger, customer)
        return (msg.body, msg.cta, msg.rationale)
    except Exception as e:
        # Graceful fallback
        merchant_name = merchant.get('identity', {}).get('name', 'Merchant')
        return (f"Hi {merchant_name}, let's grow together!", "open_ended", f"Fallback: {str(e)}")

# ===== Endpoints =====

@app.post("/v1/context", response_model=ContextResponse)
def receive_context(push: ContextPush):
    """Receive and store context (category, merchant, customer, or trigger)"""
    
    # Payload size guard: 500KB cap
    import sys
    payload_size = sys.getsizeof(json.dumps(push.payload)) if push.payload else 0
    if payload_size > 500_000:
        return ContextResponse(
            accepted=False,
            reason="payload_too_large"
        )
    
    scope = push.scope
    context_id = push.context_id
    version = push.version
    
    # Check for stale version
    if context_id in contexts_store[scope]:
        current_version, _ = contexts_store[scope][context_id]
        if current_version > version:
            return ContextResponse(
                accepted=False,
                reason="stale_version",
                current_version=current_version
            )
    
    # Store the context
    contexts_store[scope][context_id] = (version, push.payload)
    
    return ContextResponse(
        accepted=True,
        ack_id=f"ack_{context_id}_v{version}",
        stored_at=datetime.now().isoformat() + "Z"
    )

@app.post("/v1/tick", response_model=TickResponse)
def tick(req: TickRequest):
    """Periodic wake-up: bot inspects state and decides what to send"""
    
    actions = []
    
    # For each available trigger, check if we should compose a message
    for trigger_id in req.available_triggers:
        if trigger_id not in contexts_store["trigger"]:
            continue
        
        _, trigger = contexts_store["trigger"][trigger_id]
        merchant_id = trigger.get("merchant_id")
        customer_id = trigger.get("customer_id")
        
        # Get the contexts
        merchant_slug = None
        if merchant_id and merchant_id in contexts_store["merchant"]:
            _, merchant = contexts_store["merchant"][merchant_id]
            merchant_slug = merchant.get("category_slug")
        
        if not merchant_slug or merchant_slug not in contexts_store["category"]:
            continue
        
        _, category = contexts_store["category"][merchant_slug]
        _, merchant = contexts_store["merchant"][merchant_id]
        
        customer = None
        if customer_id and customer_id in contexts_store["customer"]:
            _, customer = contexts_store["customer"][customer_id]
        
        # Compose the message
        body, cta, rationale = compose_message(category, merchant, trigger, customer)
        
        if not body or body.startswith("Error") or len(body) < 5:
            continue
        
        # Create conversation
        conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        conversations_store[conversation_id] = {
            "merchant_id": merchant_id,
            "customer_id": customer_id,
            "trigger_id": trigger_id,
            "messages": [{"from": "vera", "body": body, "ts": datetime.now().isoformat()}],
            "state": "waiting_reply"
        }
        
        action = TickAction(
            conversation_id=conversation_id,
            merchant_id=merchant_id,
            customer_id=customer_id,
            send_as="vera" if not customer_id else "merchant_on_behalf",
            trigger_id=trigger_id,
            template_name=f"vera_{trigger.get('kind', 'generic')}_v1",
            template_params=[
                merchant.get("identity", {}).get("name", "Merchant"),
                trigger.get("kind", ""),
                merchant.get("identity", {}).get("owner_first_name", ""),
            ],
            body=body,
            cta=cta,
            suppression_key=trigger.get("suppression_key", f"msg:{trigger_id}"),
            rationale=rationale
        )
        actions.append(action)
        if len(actions) >= 20:  # Tick cap: max 20 actions
            break
    
    return TickResponse(actions=actions)

@app.post("/v1/reply", response_model=ReplyAction)
def reply(req: ReplyRequest):
    """Handle merchant/customer reply to a previous message"""
    
    # If conversation doesn't exist, create it on the fly
    if req.conversation_id not in conversations_store:
        conversations_store[req.conversation_id] = {
            "merchant_id": req.merchant_id,
            "customer_id": req.customer_id,
            "trigger_id": None,
            "messages": [],
            "state": "active",
            "turn_count": 0
        }
    
    conv = conversations_store[req.conversation_id]
    conv["messages"].append({
        "from": req.from_role,
        "body": req.message,
        "ts": req.received_at or datetime.now().isoformat()
    })
    conv["turn_count"] = conv.get("turn_count", 0) + 1
    
    message_lower = req.message.lower()
    
    # --- Auto-reply detection ---
    auto_reply_signals = [
        "thank you for contacting",
        "our team will respond",
        "we will get back",
        "auto-reply",
        "out of office",
        "this is an automated"
    ]
    is_auto_reply = any(sig in message_lower for sig in auto_reply_signals)
    
    # Count consecutive auto-replies
    if is_auto_reply:
        conv["auto_reply_count"] = conv.get("auto_reply_count", 0) + 1
        if conv["auto_reply_count"] >= 2:
            conv["state"] = "ended"
            return ReplyAction(
                action="end",
                rationale="Detected auto-reply pattern (2+ consecutive). Ending to avoid spam."
            )
        return ReplyAction(
            action="wait",
            wait_seconds=3600,
            rationale="Possible auto-reply detected. Waiting for human response."
        )
    else:
        conv["auto_reply_count"] = 0
    
    # --- Hostile / opt-out detection ---
    hostile_signals = ["stop", "spam", "report", "block", "unsubscribe", "don't message", "leave me alone"]
    is_hostile = any(sig in message_lower for sig in hostile_signals)
    
    if is_hostile:
        conv["state"] = "ended"
        return ReplyAction(
            action="end",
            rationale="Merchant expressed opt-out or hostility. Respecting boundary immediately."
        )
    
    # --- Off-topic detection ---
    off_topic_signals = ["weather", "cricket score", "what time is it", "who are you", "tell me a joke"]
    is_off_topic = any(sig in message_lower for sig in off_topic_signals)
    
    if is_off_topic:
        return ReplyAction(
            action="send",
            body="I'm Vera, your magicpin growth assistant. I help with offers, visibility, and customer outreach. Anything I can help with on that front?",
            cta="open_ended",
            rationale="Off-topic message. Redirect to value proposition without being dismissive."
        )
    
    # --- Negative / decline ---
    has_negative = any(kw in message_lower for kw in ["no", "not now", "don't", "stop", "later", "not interested"])
    has_positive = any(kw in message_lower for kw in ["yes", "sure", "ok", "please", "want", "interested", "send", "do it", "let's", "next"])
    
    if has_negative and not has_positive:
        conv["state"] = "ended"
        return ReplyAction(
            action="end",
            rationale="Merchant declined. Ending gracefully."
        )
    
    if has_positive:
        # Compose a follow-up
        merchant_id = conv["merchant_id"]
        trigger_id = conv["trigger_id"]
        
        if merchant_id in contexts_store["merchant"] and trigger_id in contexts_store["trigger"]:
            _, merchant = contexts_store["merchant"][merchant_id]
            _, trigger = contexts_store["trigger"][trigger_id]
            
            merchant_slug = merchant.get("category_slug")
            if merchant_slug in contexts_store["category"]:
                _, category = contexts_store["category"][merchant_slug]
                
                customer = None
                if conv["customer_id"] and conv["customer_id"] in contexts_store["customer"]:
                    _, customer = contexts_store["customer"][conv["customer_id"]]
                
                body, cta, rationale = compose_message(category, merchant, trigger, customer)
                
                conv["messages"].append({
                    "from": "vera",
                    "body": body,
                    "ts": datetime.now().isoformat()
                })
                
                return ReplyAction(
                    action="send",
                    body=body,
                    cta=cta,
                    rationale=f"Following up on merchant interest: {rationale}"
                )
    
    # Default: wait
    return ReplyAction(
        action="wait",
        wait_seconds=1800,
        rationale="Waiting for merchant clarity"
    )

@app.get("/v1/healthz", response_model=HealthResponse)
def healthz():
    """Liveness probe"""
    uptime = (datetime.now() - start_time).total_seconds()
    return HealthResponse(
        status="ok",
        uptime_seconds=int(uptime),
        contexts_loaded={
            "category": len(contexts_store["category"]),
            "merchant": len(contexts_store["merchant"]),
            "customer": len(contexts_store["customer"]),
            "trigger": len(contexts_store["trigger"]),
        }
    )

@app.get("/v1/metadata", response_model=MetadataResponse)
def metadata():
    """Bot identity and approach"""
    return MetadataResponse(
        team_name="magicpin",
        team_members=["Vera AI Team"],
        model="claude-3-5-sonnet-20241022",
        approach="Single-prompt composer with 4-context framework (category, merchant, trigger, customer). Dispatch by trigger.kind. Uses Claude for semantic composition with specificity, category fit, merchant fit, trigger relevance, and engagement compulsion.",
        contact_email="vera@magicpin.com",
        version="1.0.0",
        submitted_at=datetime.now().isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
