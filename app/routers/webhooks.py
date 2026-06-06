"""
Stripe webhook handler.
Listens for subscription events to update plan on API keys.
"""

import stripe
from fastapi import APIRouter, Header, HTTPException, Request
from app.config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/stripe", summary="Stripe webhook receiver")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
):
    payload = await request.body()

    # Verify webhook signature (skip in dev if no secret set)
    if STRIPE_WEBHOOK_SECRET and STRIPE_WEBHOOK_SECRET != "your_stripe_webhook_secret":
        try:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid Stripe signature")
    else:
        import json
        event = json.loads(payload)

    event_type = event.get("type", "")

    if event_type == "customer.subscription.created":
        # TODO: activate API key for this customer
        print(f"New subscription: {event['data']['object']['id']}")

    elif event_type == "customer.subscription.deleted":
        # TODO: deactivate API key for this customer
        print(f"Cancelled subscription: {event['data']['object']['id']}")

    elif event_type == "invoice.payment_failed":
        # TODO: warn customer, suspend key after grace period
        print(f"Payment failed: {event['data']['object']['customer']}")

    return {"received": True, "type": event_type}
