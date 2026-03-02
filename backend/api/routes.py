# backend/api/routes.py
# نقاط النهاية الخاصة بالمحادثة والمشاريع

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from ..agent.core import Agent
from .dependencies import get_current_user
from .models import User
from ..services.github_service import GitHubService

router = APIRouter()

class MessageRequest(BaseModel):
    message: str

class MessageResponse(BaseModel):
    reply: str

class CreateProjectRequest(BaseModel):
    project_name: str
    files: List[dict]  # قائمة تحتوي على مسار ومحتوى كل ملف
    description: Optional[str] = ""

@router.post("/chat", response_model=MessageResponse)
async def chat(request: MessageRequest, user: User = Depends(get_current_user)):
    """
    إرسال رسالة إلى الوكيل والحصول على الرد.
    """
    agent = Agent(user_id=user.id, github_token=user.github_token, joplin_token=user.joplin_token)
    reply = await agent.process_message(request.message)
    return MessageResponse(reply=reply)

@router.post("/projects")
async def create_project(request: CreateProjectRequest, user: User = Depends(get_current_user)):
    """
    إنشاء مشروع GitHub جديد بناءً على طلب المستخدم.
    """
    if not user.github_token:
        raise HTTPException(status_code=400, detail="يجب ربط GitHub أولاً")

    github = GitHubService(user.github_token)
    # يمكن استخدام الوكيل هنا أيضاً
    # لكن نبسط: نستخدم الخدمة مباشرة
    repo = await github.create_repo(request.project_name, request.description)
    if "error" in repo:
        raise HTTPException(status_code=400, detail=repo["error"])

    for file in request.files:
        await github.create_file(repo["name"], file["path"], file["content"], f"Add {file['path']}")

    return {"repo_url": repo["html_url"]}
