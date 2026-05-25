from fastapi import APIRouter

from app.api.v1.routes import analytics, auth, chat, documents, leads, whatsapp

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(chat.router, prefix="/chat", tags=["Chat"])
router.include_router(documents.router, prefix="/documents", tags=["Documents"])
router.include_router(leads.router, prefix="/leads", tags=["Leads"])
router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
router.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp"])
