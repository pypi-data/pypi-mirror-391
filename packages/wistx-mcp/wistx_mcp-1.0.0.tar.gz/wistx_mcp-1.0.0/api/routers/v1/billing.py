"""Billing and subscription endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.dependencies import get_current_user
from api.models.billing import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    CustomerPortalRequest,
    CustomerPortalResponse,
    SubscriptionPlan,
    SubscriptionStatus,
)
from api.services.billing_service import billing_service
from api.services.plan_service import plan_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/plans", response_model=list[SubscriptionPlan])
async def list_plans() -> list[SubscriptionPlan]:
    """List all available subscription plans.

    Returns:
        List of subscription plans
    """
    return plan_service.list_plans()


@router.get("/subscription", response_model=SubscriptionStatus)
async def get_subscription(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> SubscriptionStatus:
    """Get current user's subscription.

    Args:
        current_user: Current authenticated user

    Returns:
        Subscription status
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found",
        )

    from api.database.mongodb import mongodb_manager
    from bson import ObjectId

    db = mongodb_manager.get_database()
    user_doc = db.users.find_one({"_id": ObjectId(user_id)})

    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    plan_id = user_doc.get("plan", "free")
    stripe_subscription_id = user_doc.get("stripe_subscription_id")
    stripe_customer_id = user_doc.get("stripe_customer_id")

    if stripe_subscription_id:
        try:
            subscription_data = await billing_service.get_subscription(stripe_subscription_id)
            from datetime import datetime

            return SubscriptionStatus(
                plan_id=plan_id,
                status=subscription_data.get("status", "active"),
                current_period_start=datetime.fromtimestamp(subscription_data.get("current_period_start", 0)),
                current_period_end=datetime.fromtimestamp(subscription_data.get("current_period_end", 0)),
                cancel_at_period_end=subscription_data.get("cancel_at_period_end", False),
                stripe_subscription_id=stripe_subscription_id,
                stripe_customer_id=stripe_customer_id,
            )
        except (ValueError, RuntimeError, ConnectionError, TimeoutError) as e:
            logger.error("Error retrieving subscription: %s", e, exc_info=True)
        except Exception as e:
            logger.error("Unexpected error retrieving subscription: %s", e, exc_info=True)

    from datetime import datetime, timedelta

    return SubscriptionStatus(
        plan_id=plan_id,
        status="active" if plan_id == "free" else "trialing",
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30),
        cancel_at_period_end=False,
        stripe_subscription_id=stripe_subscription_id,
        stripe_customer_id=stripe_customer_id,
    )


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> CheckoutSessionResponse:
    """Create Stripe Checkout Session for subscription.

    Args:
        request: Checkout session request
        current_user: Current authenticated user

    Returns:
        Checkout session response with URL
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found",
        )

    from api.database.mongodb import mongodb_manager
    from api.services.billing_service import billing_service
    from bson import ObjectId

    db = mongodb_manager.get_database()
    user_doc = db.users.find_one({"_id": ObjectId(user_id)})

    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    stripe_customer_id = user_doc.get("stripe_customer_id")

    if not stripe_customer_id:
        email = user_doc.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User email not found",
            )

        customer_data = await billing_service.create_customer(
            user_id=user_id,
            email=email,
            name=user_doc.get("name"),
        )
        stripe_customer_id = customer_data["customer_id"]

    try:
        session_data = await billing_service.create_checkout_session(
            customer_id=stripe_customer_id,
            price_id=request.price_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata={"user_id": user_id},
        )

        from api.config import settings

        return CheckoutSessionResponse(
            session_id=session_data["session_id"],
            url=session_data["url"],
            publishable_key=settings.stripe_publishable_key or "",
        )
    except Exception as e:
        logger.error("Error creating checkout session: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session",
        ) from e


@router.post("/portal", response_model=CustomerPortalResponse)
async def create_portal_session(
    request: CustomerPortalRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> CustomerPortalResponse:
    """Create Stripe Customer Portal session for subscription management.

    Args:
        request: Portal session request
        current_user: Current authenticated user

    Returns:
        Portal session response with URL
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found",
        )

    from api.database.mongodb import mongodb_manager
    from bson import ObjectId

    db = mongodb_manager.get_database()
    user_doc = db.users.find_one({"_id": ObjectId(user_id)})

    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    stripe_customer_id = user_doc.get("stripe_customer_id")

    if not stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Stripe customer found. Please subscribe first.",
        )

    try:
        portal_data = await billing_service.create_portal_session(
            customer_id=stripe_customer_id,
            return_url=request.return_url,
        )

        return CustomerPortalResponse(url=portal_data["url"])
    except Exception as e:
        logger.error("Error creating portal session: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create portal session",
        ) from e

