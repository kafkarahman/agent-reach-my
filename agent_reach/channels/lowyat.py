# -*- coding: utf-8 -*-
"""Lowyat.NET — Malaysia's largest forum community.

Lowyat.NET (lowyat.net) is Malaysia's premier online forum for tech, lifestyle,
marketplace discussions, and local sentiment. The site requires basic HTML
scraping (no API). This module uses BeautifulSoup for thread/post extraction.
Anonymous access to public threads is allowed.
"""

import shutil

from agent_reach.probe import probe_command

from .base import Channel


class LowYatChannel(Channel):
    name = "lowyat"
    description = "Lowyat.NET 讨论帖和搜索（马来西亚最大论坛）"
    backends = ["beautifulsoup4", "web-scraper"]
    tier = 0  # Public content, no login required

    def can_handle(self, url: str) -> bool:
        from agent_reach.utils.url import host_matches

        return host_matches(url, "lowyat.net", "forum.lowyat.net")

    def check(self, config=None):
        """Check if BeautifulSoup4 and requests are installed for scraping."""
        self.active_backend = None
        findings = []

        for backend in self.ordered_backends(config):
            if backend == "beautifulsoup4":
                result = self._check_beautifulsoup()
            else:
                result = self._check_web_scraper()
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
            "未安装 Lowyat 爬虫依赖。推荐：\n"
            "  pip install beautifulsoup4 requests\n"
            "  或：pip install web-scraper"
        )

    def _check_beautifulsoup(self):
        """Check if BeautifulSoup4 and requests are available."""
        try:
            import bs4
            import requests
            return "ok", f"BeautifulSoup4 + requests 已安装（支持 Lowyat 论坛爬虫）"
        except ImportError as e:
            return "warn", f"BeautifulSoup4 或 requests 缺失：{e}"

    def _check_web_scraper(self):
        """Check if web-scraper library is installed as fallback."""
        try:
            import web_scraper
            return "warn", (
                "web-scraper 已安装，但 Doctor 未执行实际爬虫命令；"
                "请手动测试 Lowyat 爬虫的网络连接。"
            )
        except ImportError:
            return None
