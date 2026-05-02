#!/usr/bin/env python3
"""
Vera Composer Bot API — REST interface for composition engine

Endpoints:
  POST /v1/context   — Store context (merchant/category/trigger/customer)
  POST /v1/tick      — Compose message (trigger-driven)
  POST /v1/reply     — Handle user reply (stateful interaction)
  GET  /v1/healthz   — Health check
  GET  /v1/metadata  — API metadata
"""

from flask import Flask, request, jsonify
from datetime import datetime
import uuid
import json

from vera_composer import compose, ComposedMessage

app = Flask(__name__)

# In-memory context store (merchant_id → context dict with versions)
CONTEXT_STORE = {}
INTERACTION_LOGS = []


@app.route('/v1/healthz', methods=['GET'])
def healthz():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "3.0.0"
    }), 200


@app.route('/v1/metadata', methods=['GET'])
def metadata():
    """API metadata endpoint"""
    return jsonify({
        "name": "Vera Composer Bot",
        "version": "3.0.0",
        "documentation": "https://github.com/user/vera_magicpin/README.md",
        "endpoints": {
            "healthz": {
                "method": "GET",
                "path": "/v1/healthz",
                "description": "Health check"
            },
            "metadata": {
                "method": "GET",
                "path": "/v1/metadata",
                "description": "API metadata"
            },
            "context": {
                "method": "POST",
                "path": "/v1/context",
                "description": "Store merchant/category/customer/trigger context"
            },
            "compose": {
                "method": "POST",
                "path": "/v1/tick",
                "description": "Compose message based on trigger"
            },
            "reply": {
                "method": "POST",
                "path": "/v1/reply",
                "description": "Handle user reply (stateful interaction)"
            }
        },
        "framework": "4-lever message craft (Proof, Urgency, Curiosity, Action)",
        "categories_supported": ["dentists", "salons", "restaurants", "gyms", "pharmacies"]
    }), 200


@app.route('/v1/context', methods=['POST'])
def store_context():
    """Store context (idempotent by scope + context_id + version)"""
    
    try:
        data = request.get_json()
        
        # Extract fields
        scope = data.get("scope")  # "merchant", "category", "trigger", "customer"
        context_id = data.get("context_id")
        version = data.get("version", 1)
        payload = data.get("payload", {})
        delivered_at = data.get("delivered_at", datetime.utcnow().isoformat() + "Z")
        
        # Validate
        if not scope or not context_id:
            return jsonify({"error": "Missing scope or context_id"}), 400
        
        # Create store key
        store_key = f"{scope}:{context_id}"
        
        # Check if version already exists (idempotent)
        if store_key in CONTEXT_STORE:
            existing_version = CONTEXT_STORE[store_key].get("version", 0)
            if version <= existing_version:
                # Same or older version — no-op
                return jsonify({
                    "accepted": True,
                    "ack_id": f"ack_{uuid.uuid4().hex[:6]}",
                    "stored_at": datetime.utcnow().isoformat() + "Z",
                    "note": f"Version {version} already stored (current: {existing_version})"
                }), 200
        
        # Store context
        CONTEXT_STORE[store_key] = {
            "scope": scope,
            "context_id": context_id,
            "version": version,
            "payload": payload,
            "delivered_at": delivered_at,
            "stored_at": datetime.utcnow().isoformat() + "Z"
        }
        
        return jsonify({
            "accepted": True,
            "ack_id": f"ack_{uuid.uuid4().hex[:6]}",
            "stored_at": datetime.utcnow().isoformat() + "Z"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/v1/tick', methods=['POST'])
def compose_message():
    """Compose message based on trigger (POST /v1/tick)"""
    
    try:
        data = request.get_json()
        
        # Extract trigger info
        trigger_id = data.get("trigger_id", "trigger_unknown")
        merchant_id = data.get("merchant_id")
        category_slug = data.get("category_slug")
        customer_id = data.get("customer_id")
        
        # Retrieve stored contexts
        merchant_context = CONTEXT_STORE.get(f"merchant:{merchant_id}", {}).get("payload", {})
        category_context = CONTEXT_STORE.get(f"category:{category_slug}", {}).get("payload", {})
        trigger_context = data.get("trigger", {})  # Direct trigger data
        customer_context = CONTEXT_STORE.get(f"customer:{customer_id}", {}).get("payload", {}) if customer_id else {}
        
        # Compose message
        composed = compose(
            category=category_context or {"slug": category_slug},
            merchant=merchant_context,
            trigger=trigger_context,
            customer=customer_context
        )
        
        # Build response
        response = {
            "tick_id": f"tick_{uuid.uuid4().hex[:6]}",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "trigger_id": trigger_id,
            "composed": {
                "body": composed.body,
                "cta": composed.cta,
                "send_as": composed.send_as,
                "template_name": composed.template_name,
                "template_params": composed.template_params,
                "suppression_key": composed.suppression_key,
                "rationale": composed.rationale
            }
        }
        
        # Log interaction
        INTERACTION_LOGS.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": "compose",
            "trigger_id": trigger_id,
            "merchant_id": merchant_id,
            "category_slug": category_slug,
            "composed": response["composed"]
        })
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/v1/reply', methods=['POST'])
def handle_reply():
    """Handle user reply (stateful interaction)"""
    
    try:
        data = request.get_json()
        
        # Extract reply data
        tick_id = data.get("tick_id")
        reply_type = data.get("reply_type")  # "clicked_cta", "ignored", "replied_text"
        reply_content = data.get("reply_content", "")
        merchant_id = data.get("merchant_id")
        
        # Log reply
        INTERACTION_LOGS.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": "reply",
            "tick_id": tick_id,
            "reply_type": reply_type,
            "reply_content": reply_content,
            "merchant_id": merchant_id
        })
        
        # Acknowledge reply
        return jsonify({
            "ack_id": f"ack_{uuid.uuid4().hex[:6]}",
            "tick_id": tick_id,
            "received_at": datetime.utcnow().isoformat() + "Z"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/v1/interactions', methods=['GET'])
def get_interactions():
    """Debug endpoint — retrieve recent interactions"""
    limit = request.args.get('limit', 10, type=int)
    return jsonify({
        "count": len(INTERACTION_LOGS),
        "recent": INTERACTION_LOGS[-limit:]
    }), 200


@app.route('/v1/contexts', methods=['GET'])
def get_contexts():
    """Debug endpoint — retrieve stored contexts"""
    scope_filter = request.args.get('scope')
    
    contexts = {}
    for key, value in CONTEXT_STORE.items():
        if scope_filter and not key.startswith(scope_filter):
            continue
        contexts[key] = value
    
    return jsonify({
        "count": len(contexts),
        "contexts": contexts
    }), 200


if __name__ == '__main__':
    # Run on port 5000 locally
    app.run(host='0.0.0.0', port=5000, debug=True)
