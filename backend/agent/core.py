# backend/agent/core.py
# الوكيل الذكي - يدير المنطق الرئيسي

from typing import List, Dict, Any
import json
from loguru import logger
from ..services.llm_service import LLMService
from ..services.github_service import GitHubService
from ..services.joplin_service import JoplinService
from .memory import Memory
from .tools import Tools
from . import prompts

class Agent:
    """
    الوكيل الرئيسي الذي يتفاعل مع LLM والأدوات والذاكرة.
    """
    def __init__(self, user_id: str, github_token: str = None, joplin_token: str = None):
        self.user_id = user_id
        self.memory = Memory(user_id, joplin_token)  # ذاكرة طويلة المدى عبر Joplin
        self.llm = LLMService()
        self.github = GitHubService(github_token) if github_token else None
        self.joplin = JoplinService(joplin_token) if joplin_token else None
        self.tools = Tools(self.github, self.joplin, self.memory)
        self.conversation_history: List[Dict[str, str]] = []

    async def process_message(self, message: str) -> str:
        """
        معالجة رسالة المستخدم وتوليد الرد.
        """
        # إضافة الرسالة إلى التاريخ
        self.conversation_history.append({"role": "user", "content": message})

        # استدعاء الذاكرة طويلة المدى للحصول على سياق إضافي
        long_term_context = await self.memory.get_relevant_context(message)

        # بناء prompt للـ LLM
        system_prompt = prompts.SYSTEM_PROMPT
        if long_term_context:
            system_prompt += f"\n\nملاحظات سابقة من Joplin: {long_term_context}"

        # استدعاء LLM
        response = await self.llm.generate_response(
            system_prompt=system_prompt,
            conversation=self.conversation_history,
            tools=prompts.TOOL_DESCRIPTIONS
        )

        # تحليل الرد لاستدعاء الأدوات
        if response.get("tool_calls"):
            for tool_call in response["tool_calls"]:
                tool_name = tool_call["name"]
                tool_args = json.loads(tool_call["arguments"])
                logger.info(f"استدعاء الأداة: {tool_name} بالمعطيات {tool_args}")

                # تنفيذ الأداة
                tool_result = await self.tools.execute(tool_name, **tool_args)

                # إضافة نتيجة الأداة للمحادثة
                self.conversation_history.append({
                    "role": "tool",
                    "tool_name": tool_name,
                    "content": json.dumps(tool_result)
                })

            # بعد تنفيذ الأدوات، نطلب من LLM صياغة الرد النهائي
            final_response = await self.llm.generate_response(
                system_prompt=system_prompt,
                conversation=self.conversation_history
            )
            reply = final_response["content"]
        else:
            reply = response["content"]

        # حفظ السياق في الذاكرة طويلة المدى (مثلاً بعد عدد معين من الرسائل)
        await self.memory.save_context(message, reply)

        self.conversation_history.append({"role": "assistant", "content": reply})
        return reply
