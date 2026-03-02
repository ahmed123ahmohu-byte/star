# backend/api/auth.py
# نقاط نهاية GitHub OAuth

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import httpx
from ..config import get_settings
from ..services.github_service import exchange_code_for_token
from ..services.jwt import create_access_token
from ..models.user import User  # نموذج المستخدم (سنتجاوز التفاصيل)

router = APIRouter()
settings = get_settings()

@router.get("/github/login")
async def github_login():
    """
    إعادة توجيه المستخدم إلى GitHub لتسجيل الدخول.
    """
    github_authorize_url = "https://github.com/login/oauth/authorize"
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": "repo user",  # نطلب صلاحية الوصول للمستودعات
        "response_type": "code",
    }
    # بناء URL
    url = f"{github_authorize_url}?{'&'.join([f'{k}={v}' for k,v in params.items()])}"
    return RedirectResponse(url)

@router.get("/github/callback")
async def github_callback(code: str):
    """
    GitHub يعيد التوجيه إلى هنا مع رمز التفويض.
    """
    token_data = await exchange_code_for_token(code)
    if "error" in token_data:
        raise HTTPException(status_code=400, detail="فشل تبادل الرمز")

    access_token = token_data["access_token"]
    # هنا نحصل على معلومات المستخدم من GitHub (اختياري)
    async with httpx.AsyncClient() as client:
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {access_token}"}
        )
        github_user = user_resp.json()

    # نقوم بإنشاء مستخدم في نظامنا (أو تحديثه) وربط التوكن
    # نفترض وجود دالة get_or_create_user
    user = await get_or_create_user(github_user["id"], github_user["login"], access_token)

    # إنشاء JWT token للدخول إلى واجهتنا
    jwt_token = create_access_token({"sub": user.id})

    # إعادة التوجيه إلى التطبيق مع التوكن
    # مثلاً: myapp://callback?token=...
    return RedirectResponse(f"myapp://callback?token={jwt_token}")
