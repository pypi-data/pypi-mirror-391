"""Plan definitions and management service."""

from api.models.billing import PlanFeatures, PlanLimits, SubscriptionPlan


class PlanService:
    """Service for managing subscription plans."""

    PLANS: dict[str, SubscriptionPlan] = {
        "free": SubscriptionPlan(
            plan_id="free",
            name="Free",
            description="Perfect for getting started",
            monthly_price=0.0,
            annual_price=0.0,
            limits=PlanLimits(
                queries_per_month=100,
                indexes_per_month=0,
                storage_mb=0,
                requests_per_minute=10,
                max_api_keys=1,
            ),
            features=PlanFeatures(
                compliance_queries=True,
                knowledge_queries=True,
                repository_indexing=False,
                document_indexing=False,
                custom_indexes=False,
                priority_support=False,
                sso=False,
                api_access=True,
            ),
            popular=False,
        ),
        "starter": SubscriptionPlan(
            plan_id="starter",
            name="Starter",
            description="For small teams and projects",
            monthly_price=29.0,
            annual_price=290.0,
            limits=PlanLimits(
                queries_per_month=5000,
                indexes_per_month=5,
                storage_mb=1000,
                requests_per_minute=60,
                max_api_keys=3,
            ),
            features=PlanFeatures(
                compliance_queries=True,
                knowledge_queries=True,
                repository_indexing=True,
                document_indexing=True,
                custom_indexes=True,
                priority_support=False,
                sso=False,
                api_access=True,
            ),
            popular=True,
        ),
        "pro": SubscriptionPlan(
            plan_id="pro",
            name="Pro",
            description="For growing teams and advanced use cases",
            monthly_price=99.0,
            annual_price=990.0,
            limits=PlanLimits(
                queries_per_month=50000,
                indexes_per_month=50,
                storage_mb=10000,
                requests_per_minute=300,
                max_api_keys=10,
            ),
            features=PlanFeatures(
                compliance_queries=True,
                knowledge_queries=True,
                repository_indexing=True,
                document_indexing=True,
                custom_indexes=True,
                priority_support=True,
                sso=False,
                api_access=True,
            ),
            popular=False,
        ),
        "enterprise": SubscriptionPlan(
            plan_id="enterprise",
            name="Enterprise",
            description="For large organizations with custom needs",
            monthly_price=0.0,
            annual_price=0.0,
            limits=PlanLimits(
                queries_per_month=-1,
                indexes_per_month=-1,
                storage_mb=-1,
                requests_per_minute=1000,
                max_api_keys=100,
            ),
            features=PlanFeatures(
                compliance_queries=True,
                knowledge_queries=True,
                repository_indexing=True,
                document_indexing=True,
                custom_indexes=True,
                priority_support=True,
                sso=True,
                api_access=True,
            ),
            popular=False,
        ),
    }

    @classmethod
    def get_plan(cls, plan_id: str) -> SubscriptionPlan | None:
        """Get plan by ID.

        Args:
            plan_id: Plan ID

        Returns:
            SubscriptionPlan or None
        """
        return cls.PLANS.get(plan_id)

    @classmethod
    def list_plans(cls) -> list[SubscriptionPlan]:
        """List all available plans.

        Returns:
            List of subscription plans
        """
        return list(cls.PLANS.values())

    @classmethod
    def get_plan_limits(cls, plan_id: str) -> PlanLimits | None:
        """Get plan limits.

        Args:
            plan_id: Plan ID

        Returns:
            PlanLimits or None
        """
        plan = cls.get_plan(plan_id)
        return plan.limits if plan else None

    @classmethod
    def get_plan_features(cls, plan_id: str) -> PlanFeatures | None:
        """Get plan features.

        Args:
            plan_id: Plan ID

        Returns:
            PlanFeatures or None
        """
        plan = cls.get_plan(plan_id)
        return plan.features if plan else None


plan_service = PlanService()

