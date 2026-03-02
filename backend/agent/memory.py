# backend/agent/memory.py
# إدارة الذاكرة القصيرة والطويلة المدى مع Joplin

import hashlib
from datetime import datetime
from typing import Optional
from loguru import logger
from ..services.joplin_service import JoplinService

class Memory:
    """
    مسؤول عن تخزين واسترجاع السياق الطويل المدى باستخدام Joplin.
    """
    def __init__(self, user_id: str, joplin_token: Optional[str] = None):
        self.user_id = user_id
        self.joplin = JoplinService(joplin_token) if joplin_token else None
        self.short_term = []  # ذاكرة قصيرة (آخر محادثة)

    async def get_relevant_context(self, query: str, max_length: int = 1000) -> str:
        """
        استرجاع السياق ذي الصلة من Joplin.
        """
        if not self.joplin:
            return ""

        try:
            # البحث عن ملاحظات تحوي كلمات من الاستعلام (يمكن استخدام search API)
            notes = await self.joplin.search_notes(query)
            if notes:
                # نأخذ أول ملاحظة (أو نجمع عدة ملاحظات)
                context = notes[0].get("body", "")[:max_length]
                return context
        except Exception as e:
            logger.error(f"فشل استرجاع السياق من Joplin: {e}")
        return ""

    async def save_context(self, user_message: str, agent_reply: str):
        """
        حفظ تفاعل مهم في Joplin (مثلاً عند اكتشاف موضوع جديد).
        يمكن استدعاء هذه الدالة بشكل دوري.
        """
        if not self.joplin:
            return

        try:
            # إنشاء عنوان مميز للملاحظة
            title = f"AI Chat Context - {datetime.now().isoformat()[:10]}"
            # نص الملاحظة: الرسالة والرد
            body = f"User: {user_message}\n\nAI: {agent_reply}"
            # البحث إن كان هناك ملاحظة بنفس التاريخ لتحديثها
            notes = await self.joplin.search_notes(title)
            if notes:
                note_id = notes[0]["id"]
                await self.joplin.update_note(note_id, body=body)
            else:
                await self.joplin.create_note(title=title, body=body)
        except Exception as e:
            logger.error(f"فشل حفظ السياق في Joplin: {e}")
