# backend/logging_config.py
# إعدادات تسجيل الأحداث الاحترافية

import sys
from loguru import logger

def setup_logging():
    logger.remove()  # إزالة المعالج الافتراضي
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG" if config.DEBUG else "INFO",
        colorize=True,
    )
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="1 month",
        format="{time} | {level} | {name}:{function}:{line} - {message}",
        level="DEBUG",
    )
    return logger

# استدعاء الإعداد
from .config import get_settings
config = get_settings()
logger = setup_logging()
