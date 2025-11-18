"""V1 API routers."""

from fastapi import APIRouter

from api.routers.v1 import auth, billing, compliance, health, indexing, knowledge, reports, usage

router = APIRouter()

router.include_router(health.router)
router.include_router(auth.router)
router.include_router(billing.router)
router.include_router(usage.router)
router.include_router(compliance.router)
router.include_router(knowledge.router)
router.include_router(indexing.router)
router.include_router(reports.router)

