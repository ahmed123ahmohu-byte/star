# backend/agent/tools.py
# مجموعة الأدوات التي يمكن للوكيل استدعاؤها

from typing import Dict, Any, List
from loguru import logger

class Tools:
    """
    يحتوي على دوال قابلة للاستدعاء من قبل الوكيل.
    """
    def __init__(self, github_service, joplin_service, memory):
        self.github = github_service
        self.joplin = joplin_service
        self.memory = memory

    async def execute(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        تنفيذ الأداة حسب الاسم.
        """
        tool_method = getattr(self, tool_name, None)
        if not tool_method:
            return {"error": f"الأداة {tool_name} غير موجودة"}
        try:
            return await tool_method(**kwargs)
        except Exception as e:
            logger.exception(f"خطأ في تنفيذ الأداة {tool_name}")
            return {"error": str(e)}

    async def create_github_project(self, project_name: str, files: List[Dict[str, str]], description: str = "") -> Dict[str, Any]:
        """
        إنشاء مشروع GitHub جديد ورفع الملفات.
        يتطلب أن يكون github مُهيأ.
        """
        if not self.github:
            return {"error": "GitHub غير متصل، يرجى تسجيل الدخول أولاً"}

        # إنشاء الـ repository
        repo = await self.github.create_repo(project_name, description)
        if "error" in repo:
            return repo

        # رفع الملفات
        for file in files:
            path = file["path"]
            content = file["content"]
            commit_msg = f"إضافة {path}"
            result = await self.github.create_file(repo["name"], path, content, commit_msg)
            if "error" in result:
                return result

        return {"success": True, "repo_url": repo["html_url"]}

    async def generate_code(self, specification: str) -> Dict[str, Any]:
        """
        توليد كود باستخدام LLM بناءً على المواصفات.
        (يمكن استدعاء LLMService مباشرة)
        """
        # سيتم تنفيذها عبر LLMService
        from ..services.llm_service import LLMService
        llm = LLMService()
        code = await llm.generate_code(specification)
        return {"code": code}

    async def read_joplin_note(self, note_id: str) -> Dict[str, Any]:
        if not self.joplin:
            return {"error": "Joplin غير متصل"}
        note = await self.joplin.get_note(note_id)
        return note

    async def write_joplin_note(self, title: str, body: str) -> Dict[str, Any]:
        if not self.joplin:
            return {"error": "Joplin غير متصل"}
        note = await self.joplin.create_note(title, body)
        return note
