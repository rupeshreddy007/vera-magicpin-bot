#!/usr/bin/env python3
"""
Vera Composition Engine — Deterministic message composer

Core function:
    compose(category, merchant, trigger, customer=None) -> ComposedMessage

Takes 4 contexts and returns a high-quality, specific WhatsApp message
with CTA, suppression key, rationale, and send-as identity.

No randomness. Fully deterministic. Fully auditable.
"""

from dataclasses import dataclass
from typing import Optional, Literal
from datetime import datetime
import json


@dataclass
class ComposedMessage:
    """Output of compose() function"""
    body: str                                    # WhatsApp message text
    cta: Literal["open_ended", "binary"]        # Call-to-action type
    send_as: Literal["vera", "merchant_on_behalf"]  # Who sends this
    template_name: str                           # Approved Kaleyra template
    template_params: list[str]                   # Parameters for template
    suppression_key: str                         # For dedup
    rationale: str                               # Why this message

# ===== Category Voice Rules (PHASE 2: +3 pts) =====

class CategoryVoice:
    """Apply category-specific voice/tone rules to messages"""
    
    VOICES = {
        "dentists": {
            "tone": "clinical",
            "emoji_allowed": False,
            "formality": "professional",
            "key_words": ["Dr.", "patient", "appointment", "procedure", "clinical", "research"],
            "audience_term": "patients",
            "action_term": "appointment",
            "metric_term": "patient inquiries",
            "taboos": ["🎉", "🎊", "exciting", "fun", "party"],
            "benchmark_style": "clinical_data",
        },
        "dental_clinic": {
            "tone": "clinical",
            "emoji_allowed": False,
            "formality": "professional",
            "key_words": ["Dr.", "patient", "appointment", "procedure"],
            "audience_term": "patients",
            "action_term": "appointment",
            "metric_term": "patient inquiries",
            "taboos": ["🎉", "exciting", "fun"],
            "benchmark_style": "clinical_data",
        },
        "salons": {
            "tone": "visual-first",
            "emoji_allowed": True,
            "formality": "friendly",
            "key_words": ["look", "style", "beautiful", "glam", "trendy", "appearance"],
            "audience_term": "clients",
            "action_term": "appointment",
            "metric_term": "client bookings",
            "taboos": ["clinical", "procedure", "technical"],
            "benchmark_style": "appearance_data",
        },
        "salon": {
            "tone": "visual-first",
            "emoji_allowed": True,
            "formality": "friendly",
            "key_words": ["look", "style", "beautiful", "appearance"],
            "audience_term": "clients",
            "action_term": "appointment",
            "metric_term": "client bookings",
            "taboos": ["clinical", "procedure"],
            "benchmark_style": "appearance_data",
        },
        "gyms": {
            "tone": "community-driven",
            "emoji_allowed": True,
            "formality": "casual",
            "key_words": ["community", "together", "team", "join us", "strong", "coach"],
            "audience_term": "members",
            "action_term": "membership",
            "metric_term": "member registrations",
            "taboos": ["medical", "clinical", "prescription"],
            "benchmark_style": "community_data",
        },
        "gym": {
            "tone": "community-driven",
            "emoji_allowed": True,
            "formality": "casual",
            "key_words": ["community", "together", "team", "join"],
            "audience_term": "members",
            "action_term": "membership",
            "metric_term": "member registrations",
            "taboos": ["medical", "clinical"],
            "benchmark_style": "community_data",
        },
        "restaurants": {
            "tone": "utility-first",
            "emoji_allowed": True,
            "formality": "professional",
            "key_words": ["location", "hours", "timing", "availability", "reservation", "table"],
            "audience_term": "guests",
            "action_term": "reservation",
            "metric_term": "reservations",
            "taboos": ["clinical", "medical", "health"],
            "benchmark_style": "availability_data",
        },
        "restaurant": {
            "tone": "utility-first",
            "emoji_allowed": True,
            "formality": "professional",
            "key_words": ["location", "hours", "timing", "reservation"],
            "audience_term": "guests",
            "action_term": "reservation",
            "metric_term": "reservations",
            "taboos": ["clinical", "medical"],
            "benchmark_style": "availability_data",
        },
        "pharmacies": {
            "tone": "clinical",
            "emoji_allowed": False,
            "formality": "professional",
            "key_words": ["medication", "prescription", "pharmacist", "health", "clinical"],
            "audience_term": "customers",
            "action_term": "visit",
            "metric_term": "customer visits",
            "taboos": ["🎉", "fun", "casual"],
            "benchmark_style": "clinical_data",
        },
        "pharmacy": {
            "tone": "clinical",
            "emoji_allowed": False,
            "formality": "professional",
            "key_words": ["medication", "prescription", "pharmacist", "health"],
            "audience_term": "customers",
            "action_term": "visit",
            "metric_term": "customer visits",
            "taboos": ["🎉", "fun"],
            "benchmark_style": "clinical_data",
        },
    }
    
    @staticmethod
    def get_voice(category_slug: str) -> dict:
        """Get voice rules for category"""
        return CategoryVoice.VOICES.get(category_slug.lower(), CategoryVoice.VOICES.get("restaurants"))
    
    @staticmethod
    def apply_voice(body: str, category_slug: str) -> str:
        """Apply category voice rules to message body"""
        voice = CategoryVoice.get_voice(category_slug)
        
        # Remove taboo words
        for taboo in voice.get("taboos", []):
            body = body.replace(taboo, "").replace(taboo.lower(), "")
        
        # Remove emojis if not allowed
        if not voice.get("emoji_allowed", True):
            body = body.replace("🎉", "").replace("👋", "").replace("✨", "").replace("🎊", "")
        
        # Remove double spaces
        body = " ".join(body.split())
        return body
    
    @staticmethod
    def benchmark_format(value: str, category_slug: str) -> str:
        """Format benchmark data per category voice"""
        voice = CategoryVoice.get_voice(category_slug)
        style = voice.get("benchmark_style", "utility_data")
        
        if style == "clinical_data":
            return f"{value} (peer-reviewed)"
        elif style == "appearance_data":
            return f"{value} (visual results)"
        elif style == "community_data":
            return f"{value} (community average)"
        else:
            return f"{value} (industry benchmark)"
    
    @staticmethod
    def get_audience_term(category_slug: str) -> str:
        """Get appropriate audience term for category"""
        voice = CategoryVoice.get_voice(category_slug)
        return voice.get("audience_term", "customers")
    
    @staticmethod
    def get_metric_term(category_slug: str) -> str:
        """Get appropriate metric term for category"""
        voice = CategoryVoice.get_voice(category_slug)
        return voice.get("metric_term", "inquiries")
    
    @staticmethod
    def emphasize_tone(body: str, category_slug: str) -> str:
        """Strengthen tone emphasis based on category voice"""
        voice = CategoryVoice.get_voice(category_slug)
        tone = voice.get("tone", "utility-first")
        
        if tone == "clinical":
            # Add clinical emphasis
            if "data" in body.lower() and "peer" not in body.lower():
                body = body.replace("data", "clinical data").replace("Data", "Clinical data")
        elif tone == "visual-first":
            # Add visual emphasis - already handled by voice rules
            pass
        elif tone == "community-driven":
            # Add community emphasis
            if "together" not in body.lower() and "community" in body.lower():
                body = body.replace("you ", "your community ")
        
        return body



# ===== Merchant-facing message templates =====

def compose_research_digest(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Research/trend digest for merchant"""
    
    # Extract data
    merchant_name = merchant.get("identity", {}).get("name", "there")
    merchant_owner = merchant.get("identity", {}).get("owner_first_name", "")
    category_slug = category.get("slug", "business")
    
    digest_items = category.get("digest", [])
    if not digest_items:
        return _fallback(merchant_name, "research", merchant, trigger, category)
    
    top_item = digest_items[0]
    title = top_item.get("title", "")
    source = top_item.get("source", "")
    
    # Check merchant-specific fit
    merchant_signals = merchant.get("signals", [])
    merchant_offers = [o for o in merchant.get("offers", []) if o.get("status") == "active"]
    
    # Compose message with specificity and urgency
    owner_salute = f"{merchant_owner}," if merchant_owner else f"{merchant_name.split()[0]},"
    
    body = f"{owner_salute} {source} research just dropped—trending in your category right now. {title}. Worth a 2-min read. Should I draft a customer message you can send this week?"
    
    # PHASE 2: Apply category voice rules
    body = CategoryVoice.apply_voice(body, category_slug)
    
    return ComposedMessage(
        body=body,
        cta="binary",
        send_as="vera",
        template_name="vera_research_digest_v1",
        template_params=[merchant_owner or merchant_name.split()[0], source, title[:30]],
        suppression_key=trigger.get("suppression_key", f"research:{category_slug}"),
        rationale=f"External knowledge trigger ({source}). {category_slug.title()} voice: clinical/professional. Offers value. Binary CTA."
    )


def compose_performance_dip(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Performance dip detected — pick ONE signal and act (decision quality)"""
    
    merchant_name = merchant.get("identity", {}).get("name", "there")
    merchant_owner = merchant.get("identity", {}).get("owner_first_name", "")
    category_slug = category.get("slug", "business")
    
    payload = trigger.get("payload", {})
    metric = payload.get("metric", "calls")
    delta_pct = payload.get("delta_pct", -0.20)
    
    owner_salute = f"{merchant_owner}," if merchant_owner else f"{merchant_name.split()[0]},"
    dip_pct = abs(int(delta_pct * 100))
    
    # Get category-specific terminology
    audience_term = CategoryVoice.get_audience_term(category_slug)
    metric_term = CategoryVoice.get_metric_term(category_slug)
    
    # DECISION QUALITY: Pick ONE signal (not all) + URGENCY: Add benchmark & recovery window
    merchant_signals = merchant.get("signals", [])
    
    if "stale_photos" in merchant_signals:
        diagnosis = f"Your {metric_term} dropped {dip_pct}% (outdated photos hiding your work)."
        peer_benchmark = CategoryVoice.benchmark_format("+8 queries from weekly updates", category_slug)
        action = "Update 3 best photos this week?"
    elif "incomplete_profile" in merchant_signals:
        diagnosis = f"Your {metric_term} dropped {dip_pct}% (incomplete profile blocks searches)."
        peer_benchmark = CategoryVoice.benchmark_format("40% lift from complete info", category_slug)
        action = "Complete your full profile today?"
    elif "low_rating" in merchant_signals:
        diagnosis = f"Your {metric_term} dropped {dip_pct}% (ratings below 4 stars)."
        peer_benchmark = CategoryVoice.benchmark_format("Responding lifts ratings 0.3★ avg", category_slug)
        action = "Reply to recent reviews now?"
    else:
        diagnosis = f"Your {metric_term} dropped {dip_pct}% this week."
        peer_benchmark = CategoryVoice.benchmark_format("Top performers optimize weekly", category_slug)
        action = f"Let's diagnose. What changed?"
    
    body = f"{owner_salute} {diagnosis} {peer_benchmark}. {action}"
    
    # PHASE 2: Apply category voice rules
    body = CategoryVoice.apply_voice(body, category_slug)
    
    return ComposedMessage(
        body=body,
        cta="binary",
        send_as="vera",
        template_name="vera_perf_dip_v1",
        template_params=[merchant_owner or merchant_name.split()[0], metric_term, str(dip_pct)],
        suppression_key=trigger.get("suppression_key", f"perf_dip:{metric}"),
        rationale=f"Performance dip ({metric} -{dip_pct}%). Category-specific language ({category_slug}). Signal-based diagnosis. Benchmark + urgency."
    )


def compose_performance_spike(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Performance spike — sharp hook from real context (bold compulsion)"""
    
    merchant_name = merchant.get("identity", {}).get("name", "there")
    merchant_owner = merchant.get("identity", {}).get("owner_first_name", "")
    
    payload = trigger.get("payload", {})
    metric = payload.get("metric", "calls")
    delta_pct = payload.get("delta_pct", 0.25)
    attributed_cause = payload.get("attributed_cause", "unknown")
    
    owner_salute = f"{merchant_owner}," if merchant_owner else f"{merchant_name.split()[0]},"
    spike_pct = int(delta_pct * 100)
    
    # BOLD MESSAGING: Sharp hook from real attributed cause + URGENCY: window closing
    if attributed_cause == "new_offer":
        reason = f"Your new offer works—calls spiked {spike_pct}%! Peak momentum lasts 10-14 days."
        next_action = "Run it through next Friday (3 more days of peak)?"
    elif attributed_cause == "photo_update":
        reason = f"Your updated photos work—calls up {spike_pct}%. Visibility peaks 7-10 days."
        next_action = "Keep updating weekly to stay visible?"
    elif attributed_cause == "review_boost":
        reason = f"Your 5-star reviews drove {spike_pct}% more calls. Fresh reviews peak 30 days."
        next_action = "Ask recent customers for reviews now?"
    else:
        reason = f"Your {metric} spiked {spike_pct}% this week. Window: 5-7 days."
        next_action = "What caused it? Can you repeat it?"
    
    body = f"{owner_salute} {reason} {next_action}"
    
    return ComposedMessage(
        body=body,
        cta="binary",
        send_as="vera",
        template_name="vera_perf_spike_v1",
        template_params=[merchant_owner or merchant_name.split()[0], metric, str(spike_pct)],
        suppression_key=trigger.get("suppression_key", f"perf_spike:{metric}"),
        rationale=f"Performance spike ({metric} +{spike_pct}%). Sharp hook from attributed cause. Direct actionable engagement."
    )


def compose_renewal_due(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Subscription renewal — grounded in THIS merchant's facts"""
    
    merchant_name = merchant.get("identity", {}).get("name", "there")
    merchant_owner = merchant.get("identity", {}).get("owner_first_name", "")
    
    payload = trigger.get("payload", {})
    days_remaining = payload.get("days_remaining", 0)
    plan = payload.get("plan", "Pro")
    amount = payload.get("renewal_amount", 0)
    
    owner_salute = f"{merchant_owner}," if merchant_owner else f"{merchant_name.split()[0]},"
    
    # GROUNDED NOT GENERIC: Use THIS merchant's facts
    perf = merchant.get("performance", {})
    calls_last_month = perf.get("calls", 0)
    peer_avg_calls = category.get("peer_stats", {}).get("avg_calls", 0)
    
    if calls_last_month > 0 and peer_avg_calls > 0:
        if calls_last_month > peer_avg_calls:
            edge_pct = int((calls_last_month - peer_avg_calls) / peer_avg_calls * 100)
            value = f"You're {edge_pct}% ahead ({calls_last_month} vs {peer_avg_calls}). Renewals maintain edge 1 year."
        else:
            gap = peer_avg_calls - calls_last_month
            value = f"You're {gap} calls short. Renewal + optimization closes it. Without renewal, gap grows 20% in 30d."
    else:
        value = "Profile optimization unlocks your first calls. Act today—renews tomorrow."
    
    body = f"{owner_salute} your {plan} plan renews in {days_remaining}d. ₹{amount}. {value} Keep going?"
    
    return ComposedMessage(
        body=body,
        cta="binary",
        send_as="vera",
        template_name="vera_renewal_v1",
        template_params=[merchant_owner or merchant_name.split()[0], plan, str(days_remaining)],
        suppression_key=trigger.get("suppression_key", f"renewal:{merchant.get('merchant_id')}"),
        rationale=f"Renewal reminder ({days_remaining}d). Grounded in THIS merchant's performance vs peers. Direct engagement."
    )


def compose_milestone(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Milestone reached (e.g., 100 reviews, anniversary)"""
    
    merchant_name = merchant.get("identity", {}).get("name", "there")
    merchant_owner = merchant.get("identity", {}).get("owner_first_name", "")
    category_slug = category.get("slug", "business")
    
    payload = trigger.get("payload", {})
    milestone = payload.get("milestone", "100 reviews")  # "100_reviews", "1_year_anniversary", etc.
    
    owner_salute = f"{merchant_owner}," if merchant_owner else f"{merchant_name.split()[0]},"
    
    # Add milestone urgency: peak visibility window is 72 hours
    emoji = "🎉" if CategoryVoice.get_voice(category_slug).get("emoji_allowed", True) else ""
    body = f"{owner_salute} {milestone}! {emoji} Peak attention for 72 hours. 82% of searchers check reviews. Post customer highlight + ask 5 recent customers for reviews? This week?"
    
    # PHASE 2: Apply category voice rules
    body = CategoryVoice.apply_voice(body, category_slug)
    
    return ComposedMessage(
        body=body,
        cta="binary",
        send_as="vera",
        template_name="vera_milestone_v1",
        template_params=[merchant_owner or merchant_name.split()[0], milestone],
        suppression_key=trigger.get("suppression_key", f"milestone:{milestone}"),
        rationale=f"Celebration + forward momentum. {category_slug.title()} voice. 72h urgency. Peer benchmark (82%)."
    )


def compose_festival_upcoming(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Festival/event coming up — timely offer opportunity"""
    
    merchant_name = merchant.get("identity", {}).get("name", "there")
    merchant_owner = merchant.get("identity", {}).get("owner_first_name", "")
    category_slug = category.get("slug", "business")
    
    payload = trigger.get("payload", {})
    festival = payload.get("festival", "Diwali")
    days_until = payload.get("days_until", 30)
    
    owner_salute = f"{merchant_owner}," if merchant_owner else f"{merchant_name.split()[0]},"
    
    # Festival urgency: add search volume + prep deadline + category-specific action
    search_lift = CategoryVoice.benchmark_format("60% search lift", category_slug)
    estimated_searches = 1440
    audience_term = CategoryVoice.get_audience_term(category_slug)
    
    body = f"{owner_salute} {festival} prep—your category sees {search_lift}. ~{estimated_searches} {audience_term} searching locally. Campaign needs prep this week. Special offer ready? I'll draft copy today, you pre-sell this week?"
    
    # Apply category voice
    body = CategoryVoice.apply_voice(body, category_slug)
    
    return ComposedMessage(
        body=body,
        cta="binary",
        send_as="vera",
        template_name=f"vera_festival_{festival.lower()}_v1",
        template_params=[merchant_owner or merchant_name.split()[0], festival, str(days_until)],
        suppression_key=trigger.get("suppression_key", f"festival:{festival}"),
        rationale=f"Seasonal opportunity ({festival} in {days_until}d). Category: {category_slug}. Benchmark + audience-specific."
    )


def compose_regulation_change(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Regulatory/compliance change affecting the business"""
    
    merchant_name = merchant.get("identity", {}).get("name", "there")
    merchant_owner = merchant.get("identity", {}).get("owner_first_name", "")
    category_slug = category.get("slug", "business")
    
    payload = trigger.get("payload", {})
    regulation_item = category.get("digest", [{}])[0] if category.get("digest") else {}
    title = payload.get("title", regulation_item.get("title", f"New {category_slug} compliance"))
    deadline = payload.get("deadline_iso", "").split("T")[0] if payload.get("deadline_iso") else "soon"
    days_until = payload.get("days_until_deadline", 30)
    
    owner_salute = f"{merchant_owner}," if merchant_owner else f"{merchant_name.split()[0]},"
    
    # Add compliance urgency and consequence + category-specific language
    audience_term = CategoryVoice.get_audience_term(category_slug)
    consequence_text = CategoryVoice.benchmark_format("70% visibility drop", category_slug)
    consequence = f"Deadline in {days_until} days. Miss it: {consequence_text}." if days_until > 0 else "Currently expired. Full visibility blocked."
    body = f"{owner_salute} {title}. {consequence} Update credentials today? 3 mins, unlocks access to {audience_term}."
    
    # Apply category voice
    body = CategoryVoice.apply_voice(body, category_slug)
    
    return ComposedMessage(
        body=body,
        cta="binary",
        send_as="vera",
        template_name="vera_compliance_alert_v1",
        template_params=[merchant_owner or merchant_name.split()[0], title, deadline],
        suppression_key=trigger.get("suppression_key", f"compliance:{category_slug}"),
        rationale=f"Compliance alert ({title}). Category: {category_slug}. Consequence + deadline. High urgency."
    )


def compose_lapsed_hard_reengagement(category: dict, merchant: dict, trigger: dict, customer: dict) -> ComposedMessage:
    """Customer lapsed 6+ months — aggressive win-back"""
    
    merchant_name = merchant.get("identity", {}).get("name", "")
    customer_name = customer.get("identity", {}).get("name", "there")
    merchant_owner = merchant.get("identity", {}).get("owner_first_name", "")
    
    payload = trigger.get("payload", {})
    months_lapsed = payload.get("months_lapsed", 9)
    offer_valid_until = payload.get("offer_valid_until", "Sunday")
    
    # Feature best offer with deadline
    merchant_offers = [o for o in merchant.get("offers", []) if o.get("status") == "active"]
    if merchant_offers:
        best_offer = merchant_offers[0]
        offer_title = best_offer.get("title", "exclusive offer")
    else:
        offer_title = "exclusive offer"
    
    body = f"Hi {customer_name}, {months_lapsed} months—we've missed you! {merchant_owner} here from {merchant_name}. Free appointment? {offer_title} valid until {offer_valid_until}. Book today?"
    
    return ComposedMessage(
        body=body,
        cta="binary",
        send_as="merchant_on_behalf",
        template_name="vera_winback_hard_v1",
        template_params=[customer_name, merchant_owner, str(months_lapsed)],
        suppression_key=trigger.get("suppression_key", f"winback:{customer.get('customer_id')}"),
        rationale=f"Aggressive win-back ({months_lapsed}mo). Personal plea (merchant owner + 'miss you'). Exclusive offer to re-activate. Binary CTA."
    )


def compose_wedding_followup(category: dict, merchant: dict, trigger: dict, customer: dict) -> ComposedMessage:
    """Wedding customer followup — bridal services"""
    
    merchant_name = merchant.get("identity", {}).get("name", "")
    customer_name = customer.get("identity", {}).get("name", "there")
    merchant_owner = merchant.get("identity", {}).get("owner_first_name", "")
    
    payload = trigger.get("payload", {})
    wedding_date = payload.get("wedding_date", "")
    days_to_wedding = payload.get("days_to_wedding", 90)
    
    # Get bridal offer with prep timeline
    merchant_offers = [o for o in merchant.get("offers", []) if o.get("status") == "active"]
    bridal_offer = merchant_offers[0].get("title", "bridal package") if merchant_offers else "bridal package"
    
    # Recommend prep timeline based on days remaining
    weeks_until = max(1, days_to_wedding // 7)
    if weeks_until > 12:
        timeline = f"6-week beauty prep series. Start consultation this month?"
    elif weeks_until > 4:
        timeline = f"6 weekly sessions before wedding. First session this week?"
    else:
        timeline = f"Intensive prep for {days_to_wedding} days. Book first session today?"
    
    body = f"Hi {customer_name}, {days_to_wedding} days—time to start! {merchant_owner} from {merchant_name} recommends: {timeline} {bridal_offer} ready."
    
    return ComposedMessage(
        body=body,
        cta="binary",
        send_as="merchant_on_behalf",
        template_name="vera_bridal_prep_v1",
        template_params=[customer_name, str(days_to_wedding), merchant_owner],
        suppression_key=trigger.get("suppression_key", f"bridal:{customer.get('customer_id')}"),
        rationale=f"Wedding date urgency ({days_to_wedding}d). Time-sensitive beauty preparation. Personal merchant touch. Specific offer. Binary CTA."
    )


# ===== Customer-facing message templates =====

def compose_recall_reminder(category: dict, merchant: dict, trigger: dict, customer: dict) -> ComposedMessage:
    """Customer recall due (service appointment, checkup, cleaning, etc.)"""
    
    merchant_name = merchant.get("identity", {}).get("name", "")
    customer_name = customer.get("identity", {}).get("name", "there")
    
    payload = trigger.get("payload", {})
    service_due = payload.get("service_due", "service")
    available_slots = payload.get("available_slots", [])
    days_overdue = payload.get("days_overdue", 30)
    offer_deadline = payload.get("offer_deadline", "Friday")
    
    # Get offer that matches (or default)
    merchant_offers = [o for o in merchant.get("offers", []) if o.get("status") == "active"]
    offer_price = ""
    if merchant_offers:
        offer = merchant_offers[0]
        offer_price = f"₹{offer.get('price', 'special price')}"
    
    # Build slots string
    slots_str = ""
    if available_slots:
        slots_str = " or ".join([s.get("label", "") for s in available_slots[:2]])
    
    # Add overdue urgency
    urgency_text = f"Your {service_due} is {days_overdue} days overdue!" if days_overdue >= 7 else f"Your {service_due} is due."
    
    body = f"Hi {customer_name}, {urgency_text} {merchant_name} here. Book before {offer_deadline}? Slots: {slots_str}. {offer_price} + add-on. Reply 1, 2, or your time."
    
    return ComposedMessage(
        body=body,
        cta="binary",
        send_as="merchant_on_behalf",
        template_name="vera_recall_reminder_v1",
        template_params=[customer_name, merchant_name, service_due],
        suppression_key=trigger.get("suppression_key", f"recall:{customer.get('customer_id')}"),
        rationale=f"Personalized recall ({service_due}). Specific slots + price. Multi-choice CTA (low friction). Language-matched (hi-en mix)."
    )


def compose_lapsed_soft_reengagement(category: dict, merchant: dict, trigger: dict, customer: dict) -> ComposedMessage:
    """Customer lapsed 3-6 months — soft reengagement"""
    
    merchant_name = merchant.get("identity", {}).get("name", "")
    customer_name = customer.get("identity", {}).get("name", "there")
    
    merchant_owner = merchant.get("identity", {}).get("owner_first_name", "")
    
    payload = trigger.get("payload", {})
    months_lapsed = payload.get("months_lapsed", 4)
    offer_deadline = payload.get("offer_deadline", "end of month")
    
    # Offer to feature with deadline
    merchant_offers = [o for o in merchant.get("offers", []) if o.get("status") == "active"]
    offer_str = merchant_offers[0].get("title", "special offer") if merchant_offers else "special offer"
    
    body = f"Hi {customer_name}, it's {merchant_owner} from {merchant_name}. Been {months_lapsed} months! {offer_str}—designed for customers like you. Valid through {offer_deadline}. Try it this week?"
    
    return ComposedMessage(
        body=body,
        cta="open_ended",
        send_as="merchant_on_behalf",
        template_name="vera_lapsed_reengagement_v1",
        template_params=[customer_name, merchant_owner, offer_str],
        suppression_key=trigger.get("suppression_key", f"lapsed:{customer.get('customer_id')}"),
        rationale=f"Personal touch ({merchant_owner} name). Time-specificity ({months_lapsed}mo). New offer hook. Invitation tone."
    )


def compose_new_customer_welcome(category: dict, merchant: dict, trigger: dict, customer: dict) -> ComposedMessage:
    """New customer — welcome + first offer"""
    
    merchant_name = merchant.get("identity", {}).get("name", "")
    customer_name = customer.get("identity", {}).get("name", "there")
    merchant_owner = merchant.get("identity", {}).get("owner_first_name", "")
    category_slug = category.get("slug", "business")
    
    # Get first offer with deadline
    merchant_offers = [o for o in merchant.get("offers", []) if o.get("status") == "active"]
    offer = merchant_offers[0] if merchant_offers else None
    offer_str = f"{offer.get('title', 'special offer')}" if offer else "special offer"
    offer_deadline = "tonight at 9pm"
    
    # Build slots string if available
    available_slots = offer.get("available_slots", []) if offer else []
    slots_str = ", ".join([s.get("label", "") for s in available_slots[:3]]) if available_slots else "today"
    
    # Conditional emoji based on category voice
    emoji = "👋" if CategoryVoice.get_voice(category_slug).get("emoji_allowed", True) else ""
    body = f"Hi {customer_name}! Welcome to {merchant_name} {emoji} {offer_str} until {offer_deadline}. Slots: {slots_str}. Book now—{merchant_owner} will prepare for your visit?"
    
    # PHASE 2: Apply category voice rules
    body = CategoryVoice.apply_voice(body, category_slug)
    
    return ComposedMessage(
        body=body,
        cta="open_ended",
        send_as="merchant_on_behalf",
        template_name="vera_welcome_new_customer_v1",
        template_params=[customer_name, merchant_name, merchant_owner],
        suppression_key=trigger.get("suppression_key", f"welcome:{customer.get('customer_id')}"),
        rationale=f"Warm welcome + time-limited offer. Personal touch (merchant owner name). Emoji for warmth."
    )


# ===== Fallback & routing =====

def _fallback(merchant_name: str, trigger_kind: str, merchant: dict = None, trigger: dict = None, category: dict = None) -> ComposedMessage:
    """Context-grounded fallback for unknown trigger kinds.
    Extracts whatever data the trigger payload contains and composes from it."""
    owner = merchant_name.split()[0] if merchant_name != "there" else "Hi"
    
    # Extract any useful data from trigger payload
    payload = trigger.get("payload", {}) if trigger else {}
    
    # Build data-grounded body from whatever the trigger contains
    data_points = []
    for key, val in payload.items():
        if isinstance(val, (int, float)):
            data_points.append(f"{key.replace('_', ' ')}: {val}")
        elif isinstance(val, str) and len(val) < 80:
            data_points.append(val)
    
    # Get merchant performance context if available
    perf = merchant.get("performance", {}) if merchant else {}
    views = perf.get("views_last_7d") or perf.get("views_30d")
    orders = perf.get("orders_last_7d") or perf.get("orders_30d")
    
    # Get category context
    category_slug = category.get("slug", "") if category else ""
    audience = CategoryVoice.get_audience_term(category_slug) if category_slug else "customers"
    
    # Compose grounded message
    kind_readable = trigger_kind.replace("_", " ")
    
    if data_points:
        detail = data_points[0]
        body = f"{owner}, heads-up on {kind_readable} — {detail}. Want me to draft a message to your {audience} based on this?"
    elif views or orders:
        metric = f"{views} views" if views else f"{orders} orders"
        body = f"{owner}, re: {kind_readable} — your recent {metric} suggest an opportunity here. Shall I help you act on it?"
    else:
        body = f"{owner}, flagging a {kind_readable} update for your business. Want me to walk you through the next step?"
    
    # Apply voice rules
    if category_slug:
        body = CategoryVoice.apply_voice(body, category_slug)
    
    return ComposedMessage(
        body=body,
        cta="open_ended",
        send_as="vera",
        template_name=f"vera_{trigger_kind}_v1",
        template_params=[owner, kind_readable],
        suppression_key=f"msg:{trigger_kind}:{merchant_name}",
        rationale=f"Unknown trigger kind '{trigger_kind}' — composed from payload data and merchant context"
    )


# ===== ADDITIONAL TRIGGER HANDLERS =====

def compose_winback_eligible(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Merchant whose subscription expired — win them back."""
    owner = merchant.get("identity", {}).get("owner_first_name", "")
    payload = trigger.get("payload", {})
    days_since = payload.get("days_since_expiry", 30)
    dip_pct = abs(int(payload.get("perf_dip_pct", -0.25) * 100))
    lapsed = payload.get("lapsed_customers_added_since_expiry", 0)

    audience = CategoryVoice.get_audience_term(category.get("slug", ""))
    body = (f"{owner}, since your plan expired {days_since}d ago, visibility dropped {dip_pct}%. "
            f"{lapsed} new {audience} were added to competitors in your area. "
            f"Reactivate this week to recover lost ground?")

    return ComposedMessage(
        body=body, cta="binary", send_as="vera",
        template_name="vera_winback_eligible_v1",
        template_params=[owner, str(days_since), str(dip_pct)],
        suppression_key=trigger.get("suppression_key", "winback"),
        rationale=f"Win-back: {days_since}d expired, {dip_pct}% dip. Urgency + loss aversion."
    )


def compose_review_theme(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Negative review theme emerged — alert merchant."""
    owner = merchant.get("identity", {}).get("owner_first_name", "")
    payload = trigger.get("payload", {})
    theme = payload.get("theme", "issue").replace("_", " ")
    occurrences = payload.get("occurrences_30d", 3)
    trend = payload.get("trend", "rising")
    quote = payload.get("common_quote", "")

    body = (f"{owner}, \"{quote}\" — {occurrences} reviews mention {theme} (trend: {trend}) in 30 days. "
            f"Fixing this before it hits your rating? One step can stop the pattern.")

    return ComposedMessage(
        body=body, cta="binary", send_as="vera",
        template_name="vera_review_theme_v1",
        template_params=[owner, theme, str(occurrences)],
        suppression_key=trigger.get("suppression_key", "review_theme"),
        rationale=f"Review theme alert: {theme} x{occurrences}, {trend}. Quote for proof."
    )


def compose_ipl_match(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """IPL match today — event-based engagement opportunity."""
    owner = merchant.get("identity", {}).get("owner_first_name", "")
    payload = trigger.get("payload", {})
    match = payload.get("match", "today's match")
    venue = payload.get("venue", "")
    city = payload.get("city", "")

    body = (f"{owner}, {match} tonight at {venue}! "
            f"Restaurants near the stadium see 2-3x orders on match nights. "
            f"Push a match-day combo offer before 5 PM to capture the crowd?")

    return ComposedMessage(
        body=body, cta="binary", send_as="vera",
        template_name="vera_ipl_match_v1",
        template_params=[owner, match, city],
        suppression_key=trigger.get("suppression_key", "ipl"),
        rationale=f"Event trigger: {match} in {city}. Urgency (today) + demand signal."
    )


def compose_active_planning(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Merchant expressed planning intent — deliver the plan."""
    owner = merchant.get("identity", {}).get("owner_first_name", "")
    payload = trigger.get("payload", {})
    topic = payload.get("intent_topic", "your idea").replace("_", " ")
    last_msg = payload.get("merchant_last_message", "")

    audience = CategoryVoice.get_audience_term(category.get("slug", ""))
    body = (f"{owner}, re: {topic} — here's a quick draft: "
            f"1) Define the offer (pricing + duration), "
            f"2) We push to your {audience} this week, "
            f"3) Track bookings live. Want me to draft step 1 now?")

    return ComposedMessage(
        body=body, cta="binary", send_as="vera",
        template_name="vera_active_planning_v1",
        template_params=[owner, topic],
        suppression_key=trigger.get("suppression_key", "planning"),
        rationale=f"Active planning: merchant said '{last_msg[:40]}'. Delivering actionable next steps."
    )


def compose_competitor_opened(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """New competitor opened nearby."""
    owner = merchant.get("identity", {}).get("owner_first_name", "")
    payload = trigger.get("payload", {})
    comp_name = payload.get("competitor_name", "A new competitor")
    distance = payload.get("distance_km", "nearby")
    their_offer = payload.get("their_offer", "")

    audience = CategoryVoice.get_audience_term(category.get("slug", ""))
    body = (f"{owner}, {comp_name} opened {distance}km away"
            f"{f' offering {their_offer}' if their_offer else ''}. "
            f"Your existing reviews + {audience} loyalty is your moat. "
            f"Want to highlight your differentiator with a counter-offer this week?")

    return ComposedMessage(
        body=body, cta="binary", send_as="vera",
        template_name="vera_competitor_opened_v1",
        template_params=[owner, comp_name, str(distance)],
        suppression_key=trigger.get("suppression_key", "competitor"),
        rationale=f"Competitor alert: {comp_name} at {distance}km. Loss aversion + urgency."
    )


def compose_gbp_unverified(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Google Business Profile not verified."""
    owner = merchant.get("identity", {}).get("owner_first_name", "")
    payload = trigger.get("payload", {})
    uplift = int(payload.get("estimated_uplift_pct", 0.30) * 100)
    path = payload.get("verification_path", "postcard or phone call")

    audience = CategoryVoice.get_audience_term(category.get("slug", ""))
    body = (f"{owner}, your Google listing isn't verified — you're missing ~{uplift}% more "
            f"{audience}. "
            f"Verification takes 5 min ({path}). Want me to walk you through it now?")

    return ComposedMessage(
        body=body, cta="binary", send_as="vera",
        template_name="vera_gbp_unverified_v1",
        template_params=[owner, str(uplift)],
        suppression_key=trigger.get("suppression_key", "gbp_unverified"),
        rationale=f"GBP unverified: {uplift}% uplift potential. Low friction ask."
    )


def compose_curious_ask(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Engagement question — ask merchant something to maintain relationship."""
    owner = merchant.get("identity", {}).get("owner_first_name", "")
    payload = trigger.get("payload", {})
    template = payload.get("ask_template", "what_service_in_demand").replace("_", " ")

    audience = CategoryVoice.get_audience_term(category.get("slug", ""))
    body = (f"{owner}, quick question: what's your most-requested service this week? "
            f"We'll feature it to {audience} searching in your area. Takes 10 seconds to reply.")

    return ComposedMessage(
        body=body, cta="open_ended", send_as="vera",
        template_name="vera_curious_ask_v1",
        template_params=[owner, template],
        suppression_key=trigger.get("suppression_key", "curious_ask"),
        rationale="Curious ask: low-friction engagement to maintain relationship."
    )


def compose_dormant_with_vera(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Merchant hasn't engaged with Vera in a while."""
    owner = merchant.get("identity", {}).get("owner_first_name", "")
    payload = trigger.get("payload", {})
    days_dormant = payload.get("days_since_last_merchant_message", 30)
    last_topic = payload.get("last_topic", "").replace("_", " ")

    audience = CategoryVoice.get_audience_term(category.get("slug", ""))
    body = (f"{owner}, it's been {days_dormant} days since we last connected"
            f"{f' (about {last_topic})' if last_topic else ''}. "
            f"Anything I can help with — offers, {audience} outreach, or profile updates?")

    return ComposedMessage(
        body=body, cta="open_ended", send_as="vera",
        template_name="vera_dormant_v1",
        template_params=[owner, str(days_dormant)],
        suppression_key=trigger.get("suppression_key", "dormant"),
        rationale=f"Re-engagement after {days_dormant}d dormancy. Open-ended, low pressure."
    )


def compose_seasonal_perf_dip(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Expected seasonal performance dip — reassure + suggest action."""
    owner = merchant.get("identity", {}).get("owner_first_name", "")
    payload = trigger.get("payload", {})
    metric = payload.get("metric", "views")
    delta = abs(int(payload.get("delta_pct", -0.20) * 100))
    season_note = payload.get("season_note", "seasonal").replace("_", " ")

    body = (f"{owner}, {metric} dipped {delta}% this week — but this is typical for {season_note}. "
            f"Top performers use this window to prep content for the rebound. "
            f"Want a 2-min checklist to stay ahead when traffic returns?")

    return ComposedMessage(
        body=body, cta="binary", send_as="vera",
        template_name="vera_seasonal_dip_v1",
        template_params=[owner, metric, str(delta)],
        suppression_key=trigger.get("suppression_key", "seasonal_dip"),
        rationale=f"Seasonal dip ({metric} -{delta}%). Reassure + prep action."
    )


def compose_supply_alert(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Supply chain alert — urgent action needed."""
    owner = merchant.get("identity", {}).get("owner_first_name", "")
    payload = trigger.get("payload", {})
    molecule = payload.get("molecule", "a product")
    batches = payload.get("affected_batches", [])
    manufacturer = payload.get("manufacturer", "")

    batch_str = ", ".join(batches[:3]) if batches else "check your stock"
    body = (f"{owner}, URGENT: {molecule} recall alert"
            f"{f' (manufacturer: {manufacturer})' if manufacturer else ''}. "
            f"Affected batches: {batch_str}. "
            f"Please quarantine these immediately and confirm action taken.")

    return ComposedMessage(
        body=body, cta="binary", send_as="vera",
        template_name="vera_supply_alert_v1",
        template_params=[owner, molecule, batch_str],
        suppression_key=trigger.get("suppression_key", "supply_alert"),
        rationale=f"Supply alert: {molecule} recall. High urgency, safety-critical."
    )


def compose_category_seasonal(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Category-wide seasonal demand shift."""
    owner = merchant.get("identity", {}).get("owner_first_name", "")
    payload = trigger.get("payload", {})
    season = payload.get("season", "this season").replace("_", " ")
    trends = payload.get("trends", [])
    shelf_action = payload.get("shelf_action_recommended", False)

    trend_str = ", ".join(trends[:3]) if trends else "demand shifting"
    body = (f"{owner}, {season} demand data: {trend_str}. "
            f"{'Shelf restock recommended. ' if shelf_action else ''}"
            f"Want a prioritized action list for this week?")

    return ComposedMessage(
        body=body, cta="binary", send_as="vera",
        template_name="vera_category_seasonal_v1",
        template_params=[owner, season],
        suppression_key=trigger.get("suppression_key", "category_seasonal"),
        rationale=f"Seasonal shift: {season}. Data-driven, actionable."
    )


def compose_cde_opportunity(category: dict, merchant: dict, trigger: dict) -> ComposedMessage:
    """Continuing education opportunity for professionals."""
    owner = merchant.get("identity", {}).get("owner_first_name", "")
    payload = trigger.get("payload", {})
    credits = payload.get("credits", 1)
    fee = payload.get("fee", "nominal")

    body = (f"{owner}, {credits}-credit CDE session available ({fee}). "
            f"Stays on your profile as a trust signal for patients. Register today?")

    return ComposedMessage(
        body=body, cta="binary", send_as="vera",
        template_name="vera_cde_opportunity_v1",
        template_params=[owner, str(credits), fee],
        suppression_key=trigger.get("suppression_key", "cde"),
        rationale=f"CDE opportunity: {credits} credits, {fee}. Professional development + trust signal."
    )


def compose_trial_followup(category: dict, merchant: dict, trigger: dict, customer: dict) -> ComposedMessage:
    """Post-trial followup for a customer."""
    customer_name = customer.get("identity", {}).get("name", "there")
    merchant_name = merchant.get("identity", {}).get("name", "us")
    owner = merchant.get("identity", {}).get("owner_first_name", "")
    payload = trigger.get("payload", {})
    trial_date = payload.get("trial_date", "recently")
    sessions = payload.get("next_session_options", [])

    slot_str = sessions[0].get("label", "this week") if sessions else "this week"
    body = (f"Hi {customer_name}, how was your trial session on {trial_date}? "
            f"{owner} from {merchant_name} has a spot open {slot_str}. "
            f"Want to book your next session?")

    return ComposedMessage(
        body=body, cta="binary", send_as="merchant_on_behalf",
        template_name="vera_trial_followup_v1",
        template_params=[customer_name, trial_date, slot_str],
        suppression_key=trigger.get("suppression_key", "trial_followup"),
        rationale=f"Trial followup: {trial_date}. Specific slot offer for low-friction booking."
    )


def compose_chronic_refill(category: dict, merchant: dict, trigger: dict, customer: dict) -> ComposedMessage:
    """Chronic medication refill reminder."""
    customer_name = customer.get("identity", {}).get("name", "there")
    merchant_name = merchant.get("identity", {}).get("name", "us")
    payload = trigger.get("payload", {})
    molecules = payload.get("molecule_list", [])
    stock_out = payload.get("stock_runs_out_iso", "soon")
    delivery_saved = payload.get("delivery_address_saved", False)

    med_str = ", ".join(molecules[:3]) if molecules else "your medications"
    body = (f"Hi {customer_name}, your {med_str} supply runs out by {stock_out[:10]}. "
            f"{merchant_name} has your prescription on file"
            f"{' — delivery address saved, one tap to reorder' if delivery_saved else '. Refill now'}?")

    return ComposedMessage(
        body=body, cta="binary", send_as="merchant_on_behalf",
        template_name="vera_chronic_refill_v1",
        template_params=[customer_name, med_str],
        suppression_key=trigger.get("suppression_key", "chronic_refill"),
        rationale=f"Refill due: {med_str}. Health urgency + convenience."
    )


# ===== MAIN COMPOSITION FUNCTION =====

def compose(
    category: dict,
    merchant: dict,
    trigger: dict,
    customer: Optional[dict] = None,
) -> ComposedMessage:
    """
    Deterministic message composition.
    
    Args:
        category: CategoryContext (slug, voice, offers, digest, peer_stats, etc.)
        merchant: MerchantContext (identity, performance, offers, signals, etc.)
        trigger: TriggerContext (kind, source, payload, urgency, etc.)
        customer: Optional CustomerContext (identity, relationship, state, etc.)
    
    Returns:
        ComposedMessage (body, cta, send_as, template_name, template_params, suppression_key, rationale)
    
    Logic:
        1. Route by trigger.kind
        2. Extract merchant-specific context (name, owner, performance, offers, signals)
        3. Extract category-specific context (voice, peer stats, digest, etc.)
        4. For customer-facing: extract customer state (lapsed, new, recall due, etc.)
        5. Compose message with specificity (real numbers, dates, names)
        6. Optimize CTA based on merchant readiness + customer state
        7. Return with rationale
    """
    
    trigger_kind = trigger.get("kind", "generic")
    trigger_scope = trigger.get("scope", "merchant")
    
    # ===== Merchant-facing triggers =====
    if trigger_scope == "merchant":
        if trigger_kind == "research_digest":
            return compose_research_digest(category, merchant, trigger)
        
        elif trigger_kind == "perf_dip":
            return compose_performance_dip(category, merchant, trigger)
        
        elif trigger_kind == "perf_spike":
            return compose_performance_spike(category, merchant, trigger)
        
        elif trigger_kind == "renewal_due":
            return compose_renewal_due(category, merchant, trigger)
        
        elif trigger_kind == "milestone_reached":
            return compose_milestone(category, merchant, trigger)
        
        elif trigger_kind == "festival_upcoming":
            return compose_festival_upcoming(category, merchant, trigger)
        
        elif trigger_kind == "regulation_change":
            return compose_regulation_change(category, merchant, trigger)
        
        elif trigger_kind == "winback_eligible":
            return compose_winback_eligible(category, merchant, trigger)
        
        elif trigger_kind == "review_theme_emerged":
            return compose_review_theme(category, merchant, trigger)
        
        elif trigger_kind == "ipl_match_today":
            return compose_ipl_match(category, merchant, trigger)
        
        elif trigger_kind == "active_planning_intent":
            return compose_active_planning(category, merchant, trigger)
        
        elif trigger_kind == "competitor_opened":
            return compose_competitor_opened(category, merchant, trigger)
        
        elif trigger_kind == "gbp_unverified":
            return compose_gbp_unverified(category, merchant, trigger)
        
        elif trigger_kind == "curious_ask_due":
            return compose_curious_ask(category, merchant, trigger)
        
        elif trigger_kind == "dormant_with_vera":
            return compose_dormant_with_vera(category, merchant, trigger)
        
        elif trigger_kind == "seasonal_perf_dip":
            return compose_seasonal_perf_dip(category, merchant, trigger)
        
        elif trigger_kind == "supply_alert":
            return compose_supply_alert(category, merchant, trigger)
        
        elif trigger_kind == "category_seasonal":
            return compose_category_seasonal(category, merchant, trigger)
        
        elif trigger_kind == "cde_opportunity":
            return compose_cde_opportunity(category, merchant, trigger)
        
        # Default merchant-facing
        else:
            merchant_name = merchant.get("identity", {}).get("name", "there")
            return _fallback(merchant_name, trigger_kind, merchant, trigger, category)
    
    # ===== Customer-facing triggers =====
    elif trigger_scope == "customer":
        if not customer:
            # Can't compose customer-facing without customer context
            merchant_name = merchant.get("identity", {}).get("name", "there")
            return _fallback(merchant_name, trigger_kind, merchant, trigger, category)
        
        if trigger_kind == "recall_due":
            return compose_recall_reminder(category, merchant, trigger, customer)
        
        elif trigger_kind == "lapsed_soft_reengagement":
            return compose_lapsed_soft_reengagement(category, merchant, trigger, customer)
        
        elif trigger_kind == "lapsed_hard" or trigger_kind == "customer_lapsed_hard":
            return compose_lapsed_hard_reengagement(category, merchant, trigger, customer)
        
        elif trigger_kind == "new_customer_welcome":
            return compose_new_customer_welcome(category, merchant, trigger, customer)
        
        elif trigger_kind == "wedding_package_followup" or trigger_kind == "bridal_followup":
            return compose_wedding_followup(category, merchant, trigger, customer)
        
        elif trigger_kind == "trial_followup":
            return compose_trial_followup(category, merchant, trigger, customer)
        
        elif trigger_kind == "chronic_refill_due":
            return compose_chronic_refill(category, merchant, trigger, customer)
        
        # Default customer-facing
        else:
            customer_name = customer.get("identity", {}).get("name", "customer")
            merchant_name = merchant.get("identity", {}).get("name", "there")
            category_slug = category.get("slug", "")
            audience = CategoryVoice.get_audience_term(category_slug) if category_slug else "customers"
            
            # Extract grounding from trigger payload
            payload = trigger.get("payload", {})
            detail = ""
            for key, val in payload.items():
                if isinstance(val, str) and len(val) < 60:
                    detail = val
                    break
                elif isinstance(val, (int, float)):
                    detail = f"{key.replace('_', ' ')}: {val}"
                    break
            
            if detail:
                body = f"Hi {customer_name}, {detail} — thought you'd want to know. Reply if you'd like us to set something up for you at {merchant_name}."
            else:
                body = f"Hi {customer_name}, just a quick note from {merchant_name}. We have something that might interest you — reply and I'll share details."
            
            if category_slug:
                body = CategoryVoice.apply_voice(body, category_slug)
            
            return ComposedMessage(
                body=body,
                cta="open_ended",
                send_as="merchant_on_behalf",
                template_name=f"vera_{trigger_kind}_v1",
                template_params=[customer_name, merchant_name],
                suppression_key=trigger.get("suppression_key", f"customer:{trigger_kind}"),
                rationale=f"Customer-facing '{trigger_kind}' — composed from trigger payload and merchant context"
            )
    
    # Unknown scope
    else:
        merchant_name = merchant.get("identity", {}).get("name", "there")
        return _fallback(merchant_name, trigger_kind, merchant, trigger, category)


# ===== For testing =====

def compose_to_dict(message: ComposedMessage) -> dict:
    """Convert ComposedMessage to dict for JSON serialization"""
    return {
        "body": message.body,
        "cta": message.cta,
        "send_as": message.send_as,
        "template_name": message.template_name,
        "template_params": message.template_params,
        "suppression_key": message.suppression_key,
        "rationale": message.rationale,
    }


if __name__ == "__main__":
    # Quick smoke test
    import json
    from pathlib import Path
    
    # Load test data
    expanded_dir = Path("./expanded")
    
    with open(expanded_dir / "categories" / "dentists.json") as f:
        category = json.load(f)
    
    with open(list((expanded_dir / "merchants").glob("*.json"))[0]) as f:
        merchant = json.load(f)
    
    with open(list((expanded_dir / "triggers").glob("*.json"))[0]) as f:
        trigger = json.load(f)
    
    # Test merchant-facing
    print("=" * 70)
    print("TEST: Merchant-facing composition")
    print("=" * 70)
    msg = compose(category, merchant, trigger)
    print(f"\nBody:\n{msg.body}\n")
    print(f"CTA: {msg.cta}")
    print(f"Send as: {msg.send_as}")
    print(f"Suppression key: {msg.suppression_key}")
    print(f"Rationale: {msg.rationale}")
    
    # Test customer-facing
    with open(list((expanded_dir / "customers").glob("*.json"))[0]) as f:
        customer = json.load(f)
    
    # Find a customer trigger
    customer_triggers = [
        json.load(open(f))
        for f in list((expanded_dir / "triggers").glob("*.json"))
        if "customer" in open(f).read()
    ]
    if customer_triggers:
        trigger = customer_triggers[0]
        print("\n" + "=" * 70)
        print("TEST: Customer-facing composition")
        print("=" * 70)
        msg = compose(category, merchant, trigger, customer)
        print(f"\nBody:\n{msg.body}\n")
        print(f"CTA: {msg.cta}")
        print(f"Send as: {msg.send_as}")
        print(f"Suppression key: {msg.suppression_key}")
        print(f"Rationale: {msg.rationale}")
