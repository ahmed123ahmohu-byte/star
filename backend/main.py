# backend/main.py
# نقطة الدخول الرئيسية للتطبيق FastAPI

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import get_settings
from .logging_config import logger
from .api.routes import router as api_router
from .api.auth import router as auth_router

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # بدء التشغيل
    logger.info("بدء تشغيل الخادم...")
    # يمكن تهيئة اتصال بقاعدة البيانات أو Redis هنا
    yield
    # عند الإغلاق
    logger.info("إيقاف الخادم...")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
)

# إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تضمين المسارات
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "مرحباً بك في مساعد AI الذكي!"}
