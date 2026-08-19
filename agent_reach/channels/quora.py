# -*- coding: utf-8 -*-
"""Quora — Q&A and knowledge sharing platform.

Quora is a popular Q&A platform for user questions and community answers.
Access uses HTML scraping (BeautifulSoup) since Quora's terms restrict API use
but allows public web scraping for personal use. Anonymous access to public
questions and answers is allowed.
"""

from .base import Channel


class QuoraChannel(Channel):
    name = "quora"
    description = "Quora 问题、答案和用户"
    backends = ["beautifulsoup4", "quora-api"]
    tier = 0  # Public content, no login required

    def can_handle(self, url: str) -> bool:
        from agent_reach.utils.url import host_matches

        return host_matches(url, "quora.com")

    def check(self, config=None):
        """Check if web scraping dependencies are available."""
        self.active_backend = None
        findings = []

        for backend in self.ordered_backends(config):
            if backend == "beautifulsoup4":
                result = self._check_beautifulsoup()
            else:
                result = self._check_quora_api()
            if result is None:
                continue
            findings.append((backend, *result))

        for wanted in ("ok", "warn"):
            for backend, status, message in findings:
                if status == wanted:
                    self.active_backend = backend if status == "ok" else None
                    return status, message

        if findings:
            return "error", "\n".join(m for _, _, m in findings)

        return "off", (
            "未安装 Quora 爬虫依赖。推荐：\n"
            "  pip install beautifulsoup4 requests\n"
            "  或：pip install quora-api"
        )

    def _check_beautifulsoup(self):
        """Check if BeautifulSoup4 and requests are available."""
        try:
            import bs4
            import requests
            return "ok", f"BeautifulSoup4 + requests 已安装（支持 Quora 问答爬虫）"
        except ImportError as e:
            return "warn", f"BeautifulSoup4 或 requests 缺失：{e}"

    def _check_quora_api(self):
        """Check if quora-api library is installed as fallback."""
        try:
            import quora_api
            return "warn", (
                "quora-api 已安装，但 Doctor 未执行实际爬虫命令；"
                "请手动测试 Quora 爬虫的网络连接和速率限制。"
            )
        except ImportError:
            return None
