"""
GitHub API服务
集成GitHub API，实现代码仓库管理、issue跟踪、PR管理、Webhook等功能
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx
import hmac
import hashlib
from ..core.config import settings
from ..core.logger import logger


class GitHubService:
    """GitHub API服务"""

    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.base_url = settings.GITHUB_API_BASE_URL

    async def get_repository_info(
        self,
        owner: Optional[str] = None,
        repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取仓库信息

        Args:
            owner: 仓库所有者
            repo: 仓库名称

        Returns:
            仓库信息
        """
        try:
            owner = owner or settings.GITHUB_REPO_OWNER
            repo = repo or settings.GITHUB_REPO_NAME

            if not owner or not repo:
                raise ValueError("Repository owner and name must be provided")

            url = f"{self.base_url}/repos/{owner}/{repo}"
            headers = self._get_headers()

            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            return {
                "id": data.get("id"),
                "name": data.get("name"),
                "full_name": data.get("full_name"),
                "description": data.get("description"),
                "stars": data.get("stargazers_count"),
                "forks": data.get("forks_count"),
                "open_issues": data.get("open_issues_count"),
                "language": data.get("language"),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "url": data.get("html_url")
            }

        except Exception as e:
            logger.error(f"Error getting repository info: {str(e)}")
            raise

    async def list_issues(
        self,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        state: str = "open",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        列出Issues

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            state: 状态 (open, closed, all)
            limit: 返回数量

        Returns:
            Issues列表
        """
        try:
            owner = owner or settings.GITHUB_REPO_OWNER
            repo = repo or settings.GITHUB_REPO_NAME

            if not owner or not repo:
                raise ValueError("Repository owner and name must be provided")

            url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            headers = self._get_headers()

            params = {
                "state": state,
                "per_page": limit,
                "sort": "created",
                "direction": "desc"
            }

            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            issues = []
            for item in data:
                issues.append({
                    "id": item.get("id"),
                    "number": item.get("number"),
                    "title": item.get("title"),
                    "body": item.get("body"),
                    "state": item.get("state"),
                    "user": item.get("user", {}).get("login"),
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at"),
                    "comments": item.get("comments"),
                    "url": item.get("html_url")
                })

            return issues

        except Exception as e:
            logger.error(f"Error listing issues: {str(e)}")
            raise

    async def create_issue(
        self,
        title: str,
        body: str,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        创建Issue

        Args:
            title: Issue标题
            body: Issue内容
            owner: 仓库所有者
            repo: 仓库名称
            labels: 标签列表

        Returns:
            创建的Issue
        """
        try:
            owner = owner or settings.GITHUB_REPO_OWNER
            repo = repo or settings.GITHUB_REPO_NAME

            if not owner or not repo:
                raise ValueError("Repository owner and name must be provided")

            url = f"{self.base_url}/repos/{owner}/{repo}/issues"
            headers = self._get_headers()

            payload = {
                "title": title,
                "body": body
            }

            if labels:
                payload["labels"] = labels

            response = await self.http_client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            return {
                "id": data.get("id"),
                "number": data.get("number"),
                "title": data.get("title"),
                "body": data.get("body"),
                "state": data.get("state"),
                "user": data.get("user", {}).get("login"),
                "created_at": data.get("created_at"),
                "url": data.get("html_url")
            }

        except Exception as e:
            logger.error(f"Error creating issue: {str(e)}")
            raise

    async def list_pull_requests(
        self,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        state: str = "open",
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        列出Pull Requests

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            state: 状态 (open, closed, all)
            limit: 返回数量

        Returns:
            PR列表
        """
        try:
            owner = owner or settings.GITHUB_REPO_OWNER
            repo = repo or settings.GITHUB_REPO_NAME

            if not owner or not repo:
                raise ValueError("Repository owner and name must be provided")

            url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
            headers = self._get_headers()

            params = {
                "state": state,
                "per_page": limit,
                "sort": "created",
                "direction": "desc"
            }

            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            prs = []
            for item in data:
                prs.append({
                    "id": item.get("id"),
                    "number": item.get("number"),
                    "title": item.get("title"),
                    "body": item.get("body"),
                    "state": item.get("state"),
                    "user": item.get("user", {}).get("login"),
                    "created_at": item.get("created_at"),
                    "updated_at": item.get("updated_at"),
                    "head": item.get("head", {}).get("ref"),
                    "base": item.get("base", {}).get("ref"),
                    "url": item.get("html_url")
                })

            return prs

        except Exception as e:
            logger.error(f"Error listing pull requests: {str(e)}")
            raise

    async def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str,
        owner: Optional[str] = None,
        repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建Pull Request

        Args:
            title: PR标题
            body: PR内容
            head: 分支名称（源）
            base: 分支名称（目标）
            owner: 仓库所有者
            repo: 仓库名称

        Returns:
            创建的PR
        """
        try:
            owner = owner or settings.GITHUB_REPO_OWNER
            repo = repo or settings.GITHUB_REPO_NAME

            if not owner or not repo:
                raise ValueError("Repository owner and name must be provided")

            url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
            headers = self._get_headers()

            payload = {
                "title": title,
                "body": body,
                "head": head,
                "base": base
            }

            response = await self.http_client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            return {
                "id": data.get("id"),
                "number": data.get("number"),
                "title": data.get("title"),
                "body": data.get("body"),
                "state": data.get("state"),
                "user": data.get("user", {}).get("login"),
                "created_at": data.get("created_at"),
                "head": data.get("head", {}).get("ref"),
                "base": data.get("base", {}).get("ref"),
                "url": data.get("html_url")
            }

        except Exception as e:
            logger.error(f"Error creating pull request: {str(e)}")
            raise

    async def get_commits(
        self,
        owner: Optional[str] = None,
        repo: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        获取提交记录

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            limit: 返回数量

        Returns:
            提交记录列表
        """
        try:
            owner = owner or settings.GITHUB_REPO_OWNER
            repo = repo or settings.GITHUB_REPO_NAME

            if not owner or not repo:
                raise ValueError("Repository owner and name must be provided")

            url = f"{self.base_url}/repos/{owner}/{repo}/commits"
            headers = self._get_headers()

            params = {
                "per_page": limit
            }

            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            commits = []
            for item in data:
                commits.append({
                    "sha": item.get("sha"),
                    "message": item.get("commit", {}).get("message"),
                    "author": item.get("commit", {}).get("author", {}).get("name"),
                    "date": item.get("commit", {}).get("author", {}).get("date"),
                    "url": item.get("html_url")
                })

            return commits

        except Exception as e:
            logger.error(f"Error getting commits: {str(e)}")
            raise

    async def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str
    ) -> bool:
        """
        验证Webhook签名

        Args:
            payload: 请求体
            signature: 签名

        Returns:
            是否验证通过
        """
        try:
            if not settings.GITHUB_WEBHOOK_SECRET:
                logger.warning("GitHub webhook secret not configured")
                return False

            hash_object = hmac.new(
                settings.GITHUB_WEBHOOK_SECRET.encode(),
                msg=payload,
                digestmod=hashlib.sha256
            )

            expected_signature = f"sha256={hash_object.hexdigest()}"

            return hmac.compare_digest(expected_signature, signature)

        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}")
            return False

    async def handle_webhook(
        self,
        payload: Dict[str, Any],
        event_type: str
    ) -> Dict[str, Any]:
        """
        处理Webhook事件

        Args:
            payload: Webhook载荷
            event_type: 事件类型

        Returns:
            处理结果
        """
        try:
            logger.info(f"Handling GitHub webhook event: {event_type}")

            result = {
                "event_type": event_type,
                "action": payload.get("action"),
                "timestamp": datetime.now().isoformat(),
                "processed": True
            }

            # 根据事件类型处理不同的逻辑
            if event_type == "push":
                result["details"] = {
                    "ref": payload.get("ref"),
                    "commits": len(payload.get("commits", [])),
                    "pusher": payload.get("pusher", {}).get("name")
                }
            elif event_type == "pull_request":
                result["details"] = {
                    "pr_number": payload.get("pull_request", {}).get("number"),
                    "action": payload.get("action"),
                    "title": payload.get("pull_request", {}).get("title")
                }
            elif event_type == "issues":
                result["details"] = {
                    "issue_number": payload.get("issue", {}).get("number"),
                    "action": payload.get("action"),
                    "title": payload.get("issue", {}).get("title")
                }

            return result

        except Exception as e:
            logger.error(f"Error handling webhook: {str(e)}")
            return {
                "event_type": event_type,
                "processed": False,
                "error": str(e)
            }

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }

        if settings.GITHUB_TOKEN:
            headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

        return headers

    async def close(self):
        """关闭客户端"""
        await self.http_client.aclose()


# 全局实例
github_service = GitHubService()