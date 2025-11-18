"""Billing service with Stripe integration."""

import logging
from typing import Any, Optional

import stripe
from bson import ObjectId

from api.config import settings
from api.database.mongodb import mongodb_manager

logger = logging.getLogger(__name__)

stripe.api_key = getattr(settings, "stripe_secret_key", None) or ""


class BillingService:
    """Stripe billing integration service."""

    def __init__(self):
        """Initialize billing service."""
        if not stripe.api_key:
            logger.warning("Stripe API key not configured. Billing features will be disabled.")

    async def create_customer(
        self,
        user_id: str,
        email: str,
        name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create Stripe customer for user.

        Args:
            user_id: User ID
            email: User email
            name: User name (optional)

        Returns:
            Stripe customer object
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")

        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={
                    "user_id": user_id,
                },
            )

            db = mongodb_manager.get_database()
            db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"stripe_customer_id": customer.id}},
            )

            return {
                "customer_id": customer.id,
                "email": customer.email,
            }
        except (stripe.error.StripeError, ValueError, RuntimeError, ConnectionError) as e:
            logger.error("Failed to create Stripe customer: %s", e, exc_info=True)
            raise
        except Exception as e:
            logger.error("Unexpected error creating Stripe customer: %s", e, exc_info=True)
            raise RuntimeError(f"Unexpected error creating Stripe customer: {e}") from e

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
    ) -> dict[str, Any]:
        """Create subscription for customer.

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID

        Returns:
            Subscription object
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")

        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
            )

            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end,
            }
        except (stripe.error.StripeError, ValueError, RuntimeError, ConnectionError) as e:
            logger.error("Failed to create subscription: %s", e, exc_info=True)
            raise
        except Exception as e:
            logger.error("Unexpected error creating subscription: %s", e, exc_info=True)
            raise RuntimeError(f"Unexpected error creating subscription: {e}") from e

    async def update_subscription(
        self,
        subscription_id: str,
        price_id: str,
    ) -> dict[str, Any]:
        """Update subscription to new plan.

        Args:
            subscription_id: Stripe subscription ID
            price_id: New Stripe price ID

        Returns:
            Updated subscription object
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")

        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription["items"]["data"][0].id,
                    "price": price_id,
                }],
                proration_behavior="always_invoice",
            )

            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
            }
        except (stripe.error.StripeError, ValueError, RuntimeError, ConnectionError) as e:
            logger.error("Failed to update subscription: %s", e, exc_info=True)
            raise
        except Exception as e:
            logger.error("Unexpected error updating subscription: %s", e, exc_info=True)
            raise RuntimeError(f"Unexpected error updating subscription: {e}") from e

    async def cancel_subscription(
        self,
        subscription_id: str,
        immediately: bool = False,
    ) -> dict[str, Any]:
        """Cancel subscription.

        Args:
            subscription_id: Stripe subscription ID
            immediately: Cancel immediately or at period end

        Returns:
            Cancelled subscription object
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")

        try:
            if immediately:
                subscription = stripe.Subscription.delete(subscription_id)
            else:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True,
                )

            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "cancel_at_period_end": subscription.cancel_at_period_end if hasattr(subscription, "cancel_at_period_end") else True,
            }
        except (stripe.error.StripeError, ValueError, RuntimeError, ConnectionError) as e:
            logger.error("Failed to cancel subscription: %s", e, exc_info=True)
            raise
        except Exception as e:
            logger.error("Unexpected error canceling subscription: %s", e, exc_info=True)
            raise RuntimeError(f"Unexpected error canceling subscription: {e}") from e

    async def create_usage_record(
        self,
        subscription_item_id: str,
        quantity: int,
        timestamp: Optional[int] = None,
    ) -> dict[str, Any]:
        """Record usage for metered billing.

        Args:
            subscription_item_id: Stripe subscription item ID
            quantity: Usage quantity
            timestamp: Unix timestamp (defaults to now)

        Returns:
            Usage record object
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")

        try:
            usage_record = stripe.UsageRecord.create(
                subscription_item=subscription_item_id,
                quantity=quantity,
                timestamp=timestamp,
            )

            return {
                "id": usage_record.id,
                "quantity": usage_record.quantity,
            }
        except (stripe.error.StripeError, ValueError, RuntimeError, ConnectionError) as e:
            logger.error("Failed to create usage record: %s", e, exc_info=True)
            raise
        except Exception as e:
            logger.error("Unexpected error creating usage record: %s", e, exc_info=True)
            raise RuntimeError(f"Unexpected error creating usage record: {e}") from e

    async def get_invoices(
        self,
        customer_id: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Get invoices for customer.

        Args:
            customer_id: Stripe customer ID
            limit: Maximum number of invoices

        Returns:
            List of invoice objects
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")

        try:
            invoices = stripe.Invoice.list(
                customer=customer_id,
                limit=limit,
            )

            return [
                {
                    "id": invoice.id,
                    "amount_due": invoice.amount_due / 100,
                    "currency": invoice.currency,
                    "status": invoice.status,
                    "created": invoice.created,
                    "pdf": invoice.invoice_pdf,
                }
                for invoice in invoices.data
            ]
        except (stripe.error.StripeError, ValueError, RuntimeError, ConnectionError) as e:
            logger.error("Failed to get invoices: %s", e, exc_info=True)
            raise
        except Exception as e:
            logger.error("Unexpected error getting invoices: %s", e, exc_info=True)
            raise RuntimeError(f"Unexpected error getting invoices: {e}") from e

    async def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        metadata: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Create Stripe Checkout Session (like Cursor).

        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            success_url: Success redirect URL
            cancel_url: Cancel redirect URL
            metadata: Additional metadata

        Returns:
            Checkout session object
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")

        try:
            session_params: dict[str, Any] = {
                "customer": customer_id,
                "payment_method_types": ["card"],
                "line_items": [{"price": price_id, "quantity": 1}],
                "mode": "subscription",
                "success_url": success_url,
                "cancel_url": cancel_url,
                "allow_promotion_codes": True,
            }

            if metadata:
                session_params["metadata"] = metadata

            session = stripe.checkout.Session.create(**session_params)

            return {
                "session_id": session.id,
                "url": session.url,
                "publishable_key": settings.stripe_publishable_key or "",
            }
        except (stripe.error.StripeError, ValueError, RuntimeError, ConnectionError) as e:
            logger.error("Failed to create checkout session: %s", e, exc_info=True)
            raise
        except Exception as e:
            logger.error("Unexpected error creating checkout session: %s", e, exc_info=True)
            raise RuntimeError(f"Unexpected error creating checkout session: {e}") from e

    async def create_portal_session(
        self,
        customer_id: str,
        return_url: str,
    ) -> dict[str, Any]:
        """Create Stripe Customer Portal session (like Cursor).

        Args:
            customer_id: Stripe customer ID
            return_url: Return URL after portal

        Returns:
            Portal session object
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")

        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )

            return {
                "url": session.url,
            }
        except (stripe.error.StripeError, ValueError, RuntimeError, ConnectionError) as e:
            logger.error("Failed to create portal session: %s", e, exc_info=True)
            raise
        except Exception as e:
            logger.error("Unexpected error creating portal session: %s", e, exc_info=True)
            raise RuntimeError(f"Unexpected error creating portal session: {e}") from e

    async def get_subscription(
        self,
        subscription_id: str,
    ) -> dict[str, Any]:
        """Get subscription details.

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            Subscription object
        """
        if not stripe.api_key:
            raise ValueError("Stripe API key not configured")

        try:
            subscription = stripe.Subscription.retrieve(subscription_id)

            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "customer_id": subscription.customer,
                "price_id": subscription.items.data[0].price.id if subscription.items.data else None,
            }
        except (stripe.error.StripeError, ValueError, RuntimeError, ConnectionError) as e:
            logger.error("Failed to get subscription: %s", e, exc_info=True)
            raise
        except Exception as e:
            logger.error("Unexpected error getting subscription: %s", e, exc_info=True)
            raise RuntimeError(f"Unexpected error getting subscription: {e}") from e


billing_service = BillingService()
