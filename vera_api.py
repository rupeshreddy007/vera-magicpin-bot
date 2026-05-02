#!/usr/bin/env python3
"""
Vera Bot API — Stateful message composition service

Endpoints:
  POST /v1/context      — Store merchant/category/customer/trigger context
  POST /v1/tick         — Receive trigger, compose message
  POST /v1/reply        — (alias for /v1/tick)
  GET  /v1/healthz      — Health check
  GET  /v1/metadata     — Bot metadata

Context Storage:
  Scope + context_id + version (atomic, idempotent)
  Scopes: "merchant", "category", "customer", "trigger"
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json
import uuid
from typing import Dict, Any, Optional
from vera_composer import compose

app = Flask(__name__)

# In-memory context storage: {scope}:{context_id} -> {version: payload}
CONTEXT_STORE: Dict[str, Dict[int, Dict[str, Any]]] = {}
ACK_LOG: Dict[str, Dict[str, Any]] = {}


def get_context_key(scope: str, context_id: str) -> str:
    """Generate storage key for context"""
    return f"{scope}:{context_id}"


def store_context(scope: str, context_id: str, version: int, payload: Dict[str, Any]) -> str:
    """Store context atomically. Higher version replaces."""
    key = get_context_key(scope, context_id)
    
    # Initialize if not exists
    if key not in CONTEXT_STORE:
        CONTEXT_STORE[key] = {}
    
    # Only store if this is a new version (higher version replaces)
    stored = CONTEXT_STORE[key]
    current_version = max(stored.keys()) if stored else 0
    
    if version >= current_version:
        CONTEXT_STORE[key][version] = payload
        ack_id = f"ack_{uuid.uuid4().hex[:8]}"
        ACK_LOG[ack_id] = {
            "scope": scope,
            "context_id": context_id,
            "version": version,
            "stored_at": datetime.utcnow().isoformat() + "Z"
        }
        return ack_id
    else:
        # Version already processed, no-op
        return f"ack_{uuid.uuid4().hex[:8]}"


def get_latest_context(scope: str, context_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve latest version of context"""
    key = get_context_key(scope, context_id)
    if key not in CONTEXT_STORE or not CONTEXT_STORE[key]:
        return None
    
    latest_version = max(CONTEXT_STORE[key].keys())
    return CONTEXT_STORE[key][latest_version]


@app.route("/v1/context", methods=["POST"])
def context_endpoint():
    """Store context (merchant/category/customer/trigger)"""
    try:
        data = request.get_json()
        
        scope = data.get("scope")  # "merchant", "category", "customer", "trigger"
        context_id = data.get("context_id")
        version = data.get("version", 1)
        payload = data.get("payload", {})
        delivered_at = data.get("delivered_at", datetime.utcnow().isoformat() + "Z")
        
        if not scope or not context_id:
            return jsonify({
                "error": "Missing scope or context_id",
                "accepted": False
            }), 400
        
        # Store context
        ack_id = store_context(scope, context_id, version, payload)
        
        return jsonify({
            "accepted": True,
            "ack_id": ack_id,
            "stored_at": datetime.utcnow().isoformat() + "Z"
        }), 200
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "accepted": False
        }), 500


@app.route("/v1/tick", methods=["POST"])
def tick_endpoint():
    """Receive trigger and compose message"""
    try:
        data = request.get_json()
        
        trigger_id = data.get("trigger_id", f"trig_{uuid.uuid4().hex[:8]}")
        scope = data.get("scope", "merchant")  # Which context to use
        merchant_id = data.get("merchant_id")
        customer_id = data.get("customer_id")
        category_id = data.get("category_id")
        trigger_type = data.get("trigger_type")
        payload = data.get("payload", {})
        
        # Retrieve stored contexts
        merchant = get_latest_context("merchant", merchant_id) if merchant_id else {}
        customer = get_latest_context("customer", customer_id) if customer_id else {}
        category = get_latest_context("category", category_id) if category_id else {}
        
        # Build trigger context
        trigger = {
            "trigger_type": trigger_type,
            "payload": payload,
            "suppression_key": f"{trigger_type}:{merchant_id}"
        }
        
        # Compose message using vera_composer
        try:
            composed = compose(category, merchant, trigger, customer)
            
            return jsonify({
                "success": True,
                "trigger_id": trigger_id,
                "message": {
                    "body": composed.body,
                    "cta": composed.cta,
                    "send_as": composed.send_as,
                    "template_name": composed.template_name,
                    "template_params": composed.template_params,
                    "suppression_key": composed.suppression_key,
                    "rationale": composed.rationale
                },
                "composed_at": datetime.utcnow().isoformat() + "Z"
            }), 200
        
        except Exception as compose_error:
            return jsonify({
                "success": False,
                "trigger_id": trigger_id,
                "error": f"Composition failed: {str(compose_error)}",
                "composed_at": datetime.utcnow().isoformat() + "Z"
            }), 500
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/v1/reply", methods=["POST"])
def reply_endpoint():
    """Alias for /v1/tick (for compatibility)"""
    return tick_endpoint()


@app.route("/v1/healthz", methods=["GET"])
def healthz():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "contexts_stored": len(CONTEXT_STORE),
        "acks_logged": len(ACK_LOG)
    }), 200


@app.route("/v1/metadata", methods=["GET"])
def metadata():
    """Bot metadata endpoint"""
    return jsonify({
        "name": "Vera Composer Bot",
        "version": "3.0.0",
        "framework": "Flask",
        "description": "Deterministic WhatsApp message composition engine using 4-lever framework (Proof, Urgency, Curiosity, Action)",
        "features": [
            "Signal-based message routing",
            "Category-specific voice rules",
            "Merchant-specific personalization",
            "Explicit urgency messaging",
            "Peer benchmark integration",
            "Graceful fallback handling",
            "Stateful context management"
        ],
        "categories": ["dentists", "dental_clinic", "salons", "salon", "gyms", "gym", "restaurants", "restaurant", "pharmacies", "pharmacy"],
        "trigger_types": [
            "research_digest",
            "performance_dip",
            "performance_spike",
            "renewal_due",
            "milestone",
            "festival_upcoming",
            "regulation_change",
            "lapsed_hard_reengagement",
            "recall_reminder",
            "lapsed_soft_reengagement",
            "new_customer_welcome",
            "wedding_followup"
        ],
        "context_scopes": ["merchant", "category", "customer", "trigger"],
        "endpoints": [
            {
                "method": "POST",
                "path": "/v1/context",
                "description": "Store context (merchant/category/customer/trigger)",
                "idempotent": True
            },
            {
                "method": "POST",
                "path": "/v1/tick",
                "description": "Receive trigger and compose message",
                "idempotent": False
            },
            {
                "method": "POST",
                "path": "/v1/reply",
                "description": "Alias for /v1/tick",
                "idempotent": False
            },
            {
                "method": "GET",
                "path": "/v1/healthz",
                "description": "Health check",
                "idempotent": True
            },
            {
                "method": "GET",
                "path": "/v1/metadata",
                "description": "Bot metadata",
                "idempotent": True
            }
        ]
    }), 200


@app.route("/", methods=["GET"])
def root():
    """Root endpoint with API documentation"""
    return jsonify({
        "name": "Vera Composer Bot",
        "version": "3.0.0",
        "endpoints": {
            "health": "GET /v1/healthz",
            "metadata": "GET /v1/metadata",
            "store_context": "POST /v1/context",
            "compose": "POST /v1/tick or POST /v1/reply"
        },
        "documentation": "See /v1/metadata for full API details"
    }), 200


if __name__ == "__main__":
    # Development mode
    app.run(host="0.0.0.0", port=5000, debug=True)
