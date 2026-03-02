# backend/services/github_service.py
# التعامل مع GitHub API

from github import Github, GithubException
from loguru import logger
from typing import Optional, Dict, Any

class GitHubService:
    def __init__(self, access_token: str):
        self.client = Github(access_token)
        self.user = self.client.get_user()

    async def create_repo(self, name: str, description: str = "", private: bool = False) -> Dict[str, Any]:
        """
        إنشاء مستودع جديد.
        """
        try:
            repo = self.user.create_repo(name, description=description, private=private)
            return {
                "name": repo.name,
                "html_url": repo.html_url,
                "clone_url": repo.clone_url,
            }
        except GithubException as e:
            logger.error(f"GitHub error: {e}")
            return {"error": e.data.get("message", "Unknown error")}

    async def create_file(self, repo_name: str, path: str, content: str, message: str) -> Dict[str, Any]:
        """
        إنشاء ملف جديد في المستودع.
        """
        try:
            repo = self.user.get_repo(repo_name)
            # تحقق إن كان الملف موجوداً لتحديثه، لكننا ننشئ جديداً
            result = repo.create_file(path, message, content)
            return {"commit": result["commit"].sha, "content": result["content"].path}
        except GithubException as e:
            logger.error(f"GitHub error: {e}")
            return {"error": e.data.get("message", "Unknown error")}
