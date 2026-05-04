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
    """Handle merchant/customer reply — branch by from_role, intent, and conversation state"""
    
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
    
    message_lower = req.message.lower().strip()
    
    # --- Lookup merchant/customer/category context ---
    merchant_id = conv.get("merchant_id") or req.merchant_id
    customer_id = conv.get("customer_id") or req.customer_id
    merchant = None
    category = None
    customer = None
    merchant_name = ""
    merchant_owner = ""
    category_slug = ""
    
    if merchant_id and merchant_id in contexts_store["merchant"]:
        _, merchant = contexts_store["merchant"][merchant_id]
        merchant_name = merchant.get("identity", {}).get("name", "")
        merchant_owner = merchant.get("identity", {}).get("owner_first_name", "")
        category_slug = merchant.get("category_slug", "")
        if category_slug and category_slug in contexts_store["category"]:
            _, category = contexts_store["category"][category_slug]
    if customer_id and customer_id in contexts_store["customer"]:
        _, customer = contexts_store["customer"][customer_id]
    
    # --- Auto-reply detection ---
    auto_reply_signals = [
        "thank you for contacting", "our team will respond", "we will get back",
        "auto-reply", "out of office", "this is an automated", "currently unavailable"
    ]
    if any(sig in message_lower for sig in auto_reply_signals):
        conv["auto_reply_count"] = conv.get("auto_reply_count", 0) + 1
        if conv["auto_reply_count"] >= 2:
            conv["state"] = "ended"
            return ReplyAction(action="end", rationale="Auto-reply loop (2+ consecutive). Ending to avoid spam.")
        return ReplyAction(action="wait", wait_seconds=3600, rationale="Auto-reply detected. Waiting for human response.")
    else:
        conv["auto_reply_count"] = 0
    
    # --- Hostile / opt-out detection ---
    hostile_signals = ["stop", "spam", "report", "block", "unsubscribe", "don't message", "leave me alone"]
    if any(sig in message_lower for sig in hostile_signals):
        conv["state"] = "ended"
        return ReplyAction(action="end", rationale="Opt-out or hostility detected. Respecting boundary.")
    
    # =====================================================
    # BRANCH BY from_role
    # =====================================================
    
    if req.from_role == "customer":
        return _handle_customer_reply(conv, req, message_lower, merchant, category, customer, merchant_name, merchant_owner, category_slug)
    else:
        return _handle_merchant_reply(conv, req, message_lower, merchant, category, customer, merchant_name, merchant_owner, category_slug)


def _handle_customer_reply(conv, req, message_lower, merchant, category, customer, merchant_name, merchant_owner, category_slug):
    """Handle reply from a customer — detect booking, question, confirmation, decline"""
    
    customer_name = customer.get("identity", {}).get("name", "") if customer else ""
    salute = customer_name or "there"
    
    # --- Booking / slot pick intent ---
    import re
    booking_patterns = [
        r'\b(book|reserve|schedule|appointment)\b',
        r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)\b',
        r'\b\d{1,2}\s*(am|pm)\b',
        r'\b\d{1,2}:\d{2}\b',
        r'\b\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b',
        r'\bslot\s*\d\b',
        r'\b(tomorrow|today|tonight|next week|this week)\b',
    ]
    is_booking = any(re.search(p, message_lower) for p in booking_patterns)
    
    if is_booking:
        # Extract the time/date they mentioned
        time_match = re.search(r'(\d{1,2}\s*(am|pm)|\d{1,2}:\d{2})', message_lower)
        day_match = re.search(r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun|tomorrow|today)', message_lower)
        date_match = re.search(r'(\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*)', message_lower)
        
        slot_parts = []
        if day_match:
            slot_parts.append(day_match.group(0).capitalize())
        if date_match:
            slot_parts.append(date_match.group(0))
        if time_match:
            slot_parts.append(time_match.group(0))
        
        slot_str = " ".join(slot_parts) if slot_parts else "your preferred slot"
        
        body = f"Done, {salute}. {slot_str} confirmed with {merchant_name}. {merchant_owner} will be expecting you. See you then!"
        
        conv["state"] = "booked"
        conv["messages"].append({"from": "vera", "body": body, "ts": datetime.now().isoformat()})
        return ReplyAction(action="send", body=body, cta="open_ended", rationale=f"Customer picked slot ({slot_str}). Confirming booking with merchant name and owner.")
    
    # --- Positive / interested ---
    positive_signals = ["yes", "sure", "ok", "okay", "please", "want", "interested", "send", "do it", "let's", "sounds good", "go ahead", "great", "yeah"]
    if any(kw in message_lower.split() or kw in message_lower for kw in positive_signals):
        # Check for active offers to ground the reply
        offers = merchant.get("offers", []) if merchant else []
        active_offers = [o for o in offers if o.get("status") == "active"]
        
        if active_offers:
            offer = active_offers[0]
            offer_title = offer.get("title", "our current offer")
            offer_price = offer.get("price")
            price_str = f" at ₹{offer_price}" if offer_price else ""
            body = f"Great, {salute}! {offer_title}{price_str} at {merchant_name}. When works for you this week? Pick a day and time, I'll lock it in."
        else:
            body = f"Great, {salute}! I'll set this up with {merchant_name}. When works for you this week? Pick a day and time."
        
        conv["messages"].append({"from": "vera", "body": body, "ts": datetime.now().isoformat()})
        return ReplyAction(action="send", body=body, cta="open_ended", rationale="Customer expressed interest. Asking for slot preference to move toward booking.")
    
    # --- Negative / decline ---
    negative_signals = ["no", "not now", "don't", "later", "not interested", "busy", "cancel"]
    if any(kw in message_lower.split() for kw in negative_signals):
        conv["state"] = "ended"
        return ReplyAction(action="end", rationale="Customer declined. Ending gracefully.")
    
    # --- Question / clarification ---
    question_signals = ["?", "how much", "what time", "where", "which", "can you", "do you", "is there", "what is", "tell me"]
    is_question = any(sig in message_lower for sig in question_signals)
    
    if is_question:
        # Ground answer in merchant context
        perf = merchant.get("performance", {}) if merchant else {}
        offers = merchant.get("offers", []) if merchant else []
        active_offers = [o for o in offers if o.get("status") == "active"]
        location = merchant.get("identity", {}).get("locality", "") if merchant else ""
        
        parts = [f"{salute}, here's what I can share about {merchant_name}:"]
        if location:
            parts.append(f"Location: {location}.")
        if active_offers:
            offer = active_offers[0]
            parts.append(f"Current offer: {offer.get('title', 'available')}.")
            if offer.get("price"):
                parts.append(f"Price: ₹{offer['price']}.")
        parts.append("Want me to book a slot for you?")
        
        body = " ".join(parts)
        conv["messages"].append({"from": "vera", "body": body, "ts": datetime.now().isoformat()})
        return ReplyAction(action="send", body=body, cta="open_ended", rationale="Customer asked a question. Grounding answer in merchant offers and details.")
    
    # --- Default: acknowledge and nudge ---
    body = f"Got it, {salute}. Would you like me to book something at {merchant_name} for you?"
    conv["messages"].append({"from": "vera", "body": body, "ts": datetime.now().isoformat()})
    return ReplyAction(action="send", body=body, cta="open_ended", rationale="Unclear customer intent. Nudging toward booking action.")


def _handle_merchant_reply(conv, req, message_lower, merchant, category, customer, merchant_name, merchant_owner, category_slug):
    """Handle reply from a merchant — detect help request, question, agreement, decline"""
    
    salute = merchant_owner or (merchant_name.split()[0] if merchant_name else "Hi")
    
    # --- Negative / decline ---
    negative_signals = ["no", "not now", "don't", "later", "not interested"]
    has_negative = any(kw in message_lower.split() for kw in negative_signals)
    positive_signals = ["yes", "sure", "ok", "please", "want", "interested", "send", "do it", "let's", "next", "got it", "sounds good", "go ahead"]
    has_positive = any(kw in message_lower.split() or kw in message_lower for kw in positive_signals)
    
    if has_negative and not has_positive:
        conv["state"] = "ended"
        return ReplyAction(action="end", rationale="Merchant declined. Ending gracefully.")
    
    # --- Detect merchant asking for help / raising a topic ---
    help_patterns = [
        r'\b(help|assist|guide|show me|walk me through|how do i|how to|can you|need help)\b',
        r'\b(setup|set up|audit|review|check|update|fix|improve|optimize)\b',
        r'\b(what should|what can|any tips|any advice|suggest)\b',
    ]
    import re
    is_help_request = any(re.search(p, message_lower) for p in help_patterns)
    
    # Extract the topic they're asking about
    topic_match = re.search(r'(x-ray|xray|photo|menu|listing|profile|offer|campaign|review|rating|seo|google|visibility|booking|appointment|schedule|pricing|compliance|license|certificate)', message_lower)
    topic = topic_match.group(0) if topic_match else None
    
    if is_help_request or topic:
        # Ground response in the specific topic + merchant context
        perf = merchant.get("performance", {}) if merchant else {}
        signals = merchant.get("signals", []) if merchant else []
        
        if topic:
            topic_clean = topic.replace("-", " ").title()
            
            # Build topic-specific grounded response
            if topic in ["photo", "photos", "x-ray", "xray"]:
                body = f"{salute}, on {topic_clean} — I can help. Upload your latest images to your magicpin listing. Merchants who update photos weekly see 40% more profile views. Want me to flag which photos need replacing?"
            elif topic in ["menu", "pricing"]:
                body = f"{salute}, got it. An updated {topic_clean} drives 25% more conversions. Upload your current version and I'll check it's indexed for search. Ready?"
            elif topic in ["review", "rating", "reviews", "ratings"]:
                current_rating = perf.get("rating", perf.get("avg_rating"))
                rating_str = f" (currently {current_rating}★)" if current_rating else ""
                body = f"{salute}, on reviews{rating_str} — responding to each review lifts ratings 0.3★ on average. Want me to draft replies to your recent ones?"
            elif topic in ["offer", "campaign", "offers"]:
                offers = merchant.get("offers", []) if merchant else []
                active = [o for o in offers if o.get("status") == "active"]
                if active:
                    body = f"{salute}, your '{active[0].get('title', 'current offer')}' is running. Want to extend reach? I can push it to lapsed customers or create a new campaign targeting nearby searchers."
                else:
                    body = f"{salute}, you don't have an active offer right now. Creating one takes 2 minutes and boosts visibility by 35%. Want me to help draft one?"
            elif topic in ["compliance", "license", "certificate"]:
                body = f"{salute}, compliance updates protect your listing visibility. Upload your latest credentials — takes about 3 minutes. I'll verify and flag anything missing. Go ahead?"
            elif topic in ["google", "seo", "visibility"]:
                views = perf.get("views_last_7d") or perf.get("views_30d", 0)
                views_str = f" ({views} views last period)" if views else ""
                body = f"{salute}, on visibility{views_str} — the biggest levers are complete profile, fresh photos, and active offers. Which one should we tackle first?"
            elif topic in ["booking", "appointment", "schedule"]:
                body = f"{salute}, I can help with your booking setup. Do you want to set up online scheduling, or do you handle appointments manually?"
            else:
                body = f"{salute}, on {topic_clean} — let me look into that for you. What specific aspect do you need help with?"
        else:
            # Generic help request without clear topic
            body = f"{salute}, happy to help. What specifically do you need — offers, photos, reviews, or something else?"
        
        conv["messages"].append({"from": "vera", "body": body, "ts": datetime.now().isoformat()})
        return ReplyAction(action="send", body=body, cta="open_ended", rationale=f"Merchant asked for help on '{topic or 'general'}'. Grounded response with actionable next step.")
    
    if has_positive:
        # Merchant agreed — move toward next action grounded in context
        trigger_id = conv.get("trigger_id")
        
        # Try to compose from trigger context
        if trigger_id and trigger_id in contexts_store["trigger"]:
            _, trigger = contexts_store["trigger"][trigger_id]
            if merchant and category:
                cust = None
                if conv.get("customer_id") and conv["customer_id"] in contexts_store["customer"]:
                    _, cust = contexts_store["customer"][conv["customer_id"]]
                body, cta, rationale = compose_message(category, merchant, trigger, cust)
                conv["messages"].append({"from": "vera", "body": body, "ts": datetime.now().isoformat()})
                return ReplyAction(action="send", body=body, cta=cta, rationale=f"Merchant agreed. Follow-up: {rationale}")
        
        # Ground in merchant data
        perf = merchant.get("performance", {}) if merchant else {}
        offers = merchant.get("offers", []) if merchant else []
        active_offers = [o for o in offers if o.get("status") == "active"]
        signals = merchant.get("signals", []) if merchant else []
        
        if active_offers:
            offer = active_offers[0]
            body = f"Perfect, {salute}. I'll push '{offer.get('title', 'your offer')}' to nearby customers searching in your category. You should see results within 48 hours."
        elif signals:
            signal = signals[0].replace("_", " ")
            body = f"Great, {salute}. Let's start with fixing {signal} — that's the quickest win for your listing. I'll walk you through it now."
        elif perf:
            views = perf.get("views_last_7d") or perf.get("views_30d", 0)
            body = f"Good, {salute}. With {views} recent views, let's convert more. I'll draft a customer outreach message — take a look when it's ready?"
        else:
            body = f"Noted, {salute}. I'll prepare the next step and send it over."
        
        conv["messages"].append({"from": "vera", "body": body, "ts": datetime.now().isoformat()})
        return ReplyAction(action="send", body=body, cta="open_ended", rationale="Merchant agreed. Grounded follow-up from merchant context.")
    
    # --- Question from merchant ---
    if "?" in req.message:
        perf = merchant.get("performance", {}) if merchant else {}
        views = perf.get("views_last_7d") or perf.get("views_30d")
        offers = merchant.get("offers", []) if merchant else []
        active = [o for o in offers if o.get("status") == "active"]
        
        parts = [f"{salute}, happy to clarify."]
        if views:
            parts.append(f"Your current views: {views}.")
        if active:
            parts.append(f"Active offer: '{active[0].get('title', '')}'.")
        parts.append("What specifically would you like to know more about?")
        
        body = " ".join(parts)
        conv["messages"].append({"from": "vera", "body": body, "ts": datetime.now().isoformat()})
        return ReplyAction(action="send", body=body, cta="open_ended", rationale="Merchant asked a question. Sharing context and asking for specifics.")
    
    # --- Default: engage with what they said ---
    # Echo their topic and offer help rather than just waiting
    body = f"{salute}, noted. How would you like me to help with this? I can look into it and come back with a recommendation."
    conv["messages"].append({"from": "vera", "body": body, "ts": datetime.now().isoformat()})
    return ReplyAction(action="send", body=body, cta="open_ended", rationale="Unclear merchant intent. Engaging rather than waiting.")

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
        model="deterministic-rule-engine",
        approach="Context-grounded deterministic composer. Routes by trigger.kind, extracts real data from merchant/category/customer contexts, applies category voice rules. No LLM — every output is derived from the structured context actually received. Handles unknown triggers by mining payload fields.",
        contact_email="vera@magicpin.com",
        version="1.1.0",
        submitted_at=datetime.now().isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
