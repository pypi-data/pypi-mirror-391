"""Stripe webhook handlers."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from api.config import settings
from api.services.billing_service import billing_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(request: Request) -> dict[str, str]:
    """Handle Stripe webhook events.

    Args:
        request: FastAPI request object

    Returns:
        Success response
    """
    if not settings.stripe_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not configured",
        )

    import stripe

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing stripe-signature header",
        )

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.stripe_webhook_secret,
        )
    except ValueError as e:
        logger.error("Invalid payload: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload",
        ) from e
    except stripe.SignatureVerificationError as e:
        logger.error("Invalid signature: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature",
        ) from e

    event_type = event["type"]
    event_data = event["data"]["object"]

    logger.info("Received Stripe webhook: %s", event_type)

    try:
        if event_type == "customer.subscription.created":
            await handle_subscription_created(event_data)
        elif event_type == "customer.subscription.updated":
            await handle_subscription_updated(event_data)
        elif event_type == "customer.subscription.deleted":
            await handle_subscription_deleted(event_data)
        elif event_type == "invoice.payment_succeeded":
            await handle_payment_succeeded(event_data)
        elif event_type == "invoice.payment_failed":
            await handle_payment_failed(event_data)
        elif event_type == "checkout.session.completed":
            await handle_checkout_completed(event_data)
        else:
            logger.info("Unhandled event type: %s", event_type)

        return {"status": "success"}
    except Exception as e:
        logger.error("Error handling webhook event: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed",
        ) from e


async def handle_subscription_created(subscription: dict[str, Any]) -> None:
    """Handle subscription created event.

    Args:
        subscription: Stripe subscription object
    """
    customer_id = subscription.get("customer")
    subscription_id = subscription.get("id")
    status_value = subscription.get("status")

    from api.database.mongodb import mongodb_manager

    db = mongodb_manager.get_database()

    user_doc = db.users.find_one({"stripe_customer_id": customer_id})
    if not user_doc:
        logger.warning("User not found for customer: %s", customer_id)
        return

    from bson import ObjectId
    from datetime import datetime

    price_id = subscription.get("items", {}).get("data", [{}])[0].get("price", {}).get("id")
    plan_id = determine_plan_from_price_id(price_id)

    db.users.update_one(
        {"_id": user_doc["_id"]},
        {
            "$set": {
                "stripe_subscription_id": subscription_id,
                "subscription_status": status_value,
                "plan": plan_id,
                "subscription_start": datetime.fromtimestamp(subscription.get("current_period_start", 0)),
                "subscription_renews_at": datetime.fromtimestamp(subscription.get("current_period_end", 0)),
            }
        },
    )

    logger.info("Updated user %s subscription: %s", user_doc["_id"], subscription_id)


async def handle_subscription_updated(subscription: dict[str, Any]) -> None:
    """Handle subscription updated event.

    Args:
        subscription: Stripe subscription object
    """
    customer_id = subscription.get("customer")
    subscription_id = subscription.get("id")
    status_value = subscription.get("status")

    from api.database.mongodb import mongodb_manager
    from bson import ObjectId
    from datetime import datetime

    db = mongodb_manager.get_database()

    user_doc = db.users.find_one({"stripe_subscription_id": subscription_id})
    if not user_doc:
        logger.warning("User not found for subscription: %s", subscription_id)
        return

    price_id = subscription.get("items", {}).get("data", [{}])[0].get("price", {}).get("id")
    plan_id = determine_plan_from_price_id(price_id)

    update_data = {
        "subscription_status": status_value,
        "subscription_renews_at": datetime.fromtimestamp(subscription.get("current_period_end", 0)),
    }

    if plan_id:
        update_data["plan"] = plan_id

    db.users.update_one(
        {"_id": user_doc["_id"]},
        {"$set": update_data},
    )

    logger.info("Updated user %s subscription status: %s", user_doc["_id"], status_value)


async def handle_subscription_deleted(subscription: dict[str, Any]) -> None:
    """Handle subscription deleted event.

    Args:
        subscription: Stripe subscription object
    """
    subscription_id = subscription.get("id")

    from api.database.mongodb import mongodb_manager
    from bson import ObjectId

    db = mongodb_manager.get_database()

    user_doc = db.users.find_one({"stripe_subscription_id": subscription_id})
    if not user_doc:
        logger.warning("User not found for subscription: %s", subscription_id)
        return

    db.users.update_one(
        {"_id": user_doc["_id"]},
        {
            "$set": {
                "subscription_status": "canceled",
                "plan": "free",
            },
            "$unset": {
                "stripe_subscription_id": "",
                "subscription_renews_at": "",
            },
        },
    )

    logger.info("Canceled subscription for user %s", user_doc["_id"])


async def handle_payment_succeeded(invoice: dict[str, Any]) -> None:
    """Handle payment succeeded event.

    Args:
        invoice: Stripe invoice object
    """
    customer_id = invoice.get("customer")
    subscription_id = invoice.get("subscription")

    if not subscription_id:
        return

    from api.database.mongodb import mongodb_manager

    db = mongodb_manager.get_database()

    user_doc = db.users.find_one({"stripe_customer_id": customer_id})
    if not user_doc:
        logger.warning("User not found for customer: %s", customer_id)
        return

    db.users.update_one(
        {"_id": user_doc["_id"]},
        {"$set": {"subscription_status": "active"}},
    )

    logger.info("Payment succeeded for user %s", user_doc["_id"])


async def handle_payment_failed(invoice: dict[str, Any]) -> None:
    """Handle payment failed event.

    Args:
        invoice: Stripe invoice object
    """
    customer_id = invoice.get("customer")

    from api.database.mongodb import mongodb_manager

    db = mongodb_manager.get_database()

    user_doc = db.users.find_one({"stripe_customer_id": customer_id})
    if not user_doc:
        logger.warning("User not found for customer: %s", customer_id)
        return

    db.users.update_one(
        {"_id": user_doc["_id"]},
        {"$set": {"subscription_status": "past_due"}},
    )

    logger.warning("Payment failed for user %s", user_doc["_id"])


async def handle_checkout_completed(session: dict[str, Any]) -> None:
    """Handle checkout session completed event.

    Args:
        session: Stripe checkout session object
    """
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    metadata = session.get("metadata", {})
    user_id = metadata.get("user_id")

    if not user_id or not subscription_id:
        logger.warning("Missing user_id or subscription_id in checkout session")
        return

    from api.database.mongodb import mongodb_manager
    from bson import ObjectId
    from datetime import datetime

    db = mongodb_manager.get_database()

    subscription_data = await billing_service.get_subscription(subscription_id)
    price_id = subscription_data.get("price_id")
    plan_id = determine_plan_from_price_id(price_id)

    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "stripe_customer_id": customer_id,
                "stripe_subscription_id": subscription_id,
                "subscription_status": "active",
                "plan": plan_id or "starter",
                "subscription_start": datetime.fromtimestamp(subscription_data.get("current_period_start", 0)),
                "subscription_renews_at": datetime.fromtimestamp(subscription_data.get("current_period_end", 0)),
            }
        },
    )

    logger.info("Checkout completed for user %s, subscription %s", user_id, subscription_id)


def determine_plan_from_price_id(price_id: str | None) -> str | None:
    """Determine plan ID from Stripe price ID.

    Args:
        price_id: Stripe price ID

    Returns:
        Plan ID or None
    """
    if not price_id:
        return None

    from api.services.plan_service import plan_service

    for plan in plan_service.list_plans():
        if plan.stripe_monthly_price_id == price_id or plan.stripe_annual_price_id == price_id:
            return plan.plan_id

    return None

