# -*- coding: utf-8 -*-
"""Threads — Meta's X-competitor, growing fast in SEA/global.

Threads is Meta's decentralized social platform. Access requires browser
automation (OpenCLI) since Threads has no public API. User login is required
to view most content, but OpenCLI reuses your existing Meta/Instagram login.
"""

from .base import Channel


class ThreadsChannel(Channel):
    name = "threads"
    description = "Threads 帖子和用户（Meta 社交平台）"
    backends = ["OpenCLI"]
    tier = 1  # Requires login

    def can_handle(self, url: str) -> bool:
        from agent_reach.utils.url import host_matches

        return host_matches(url, "threads.net", "instagram.threads.com")

    def check(self, config=None):
        """Check if OpenCLI bridge is available and connected."""
        self.active_backend = None

        status, message = self._check_opencli()
        if status in ("ok", "warn"):
            if status == "ok":
                self.active_backend = "OpenCLI"
            return status, message

        return "off", (
            "未安装 OpenCLI 桥接。Threads 没有公开 API，必须用浏览器访问。推荐：\n"
            "  agent-reach install --system --channels opencli\n"
            "  （复用 Chrome 登录态，登录过 threads.net 即可用）"
        )

    def _check_opencli(self):
        """Check if OpenCLI bridge is installed and connected."""
        from agent_reach.backends import opencli_status

        st = opencli_status()
        if not st.installed:
            return "off", "OpenCLI 未安装"
        if st.broken:
            return "error", st.hint
        if st.ready:
            return "warn", (
                "OpenCLI 桥接已连接，但 Threads 登录态和实际命令未实时验证；"
                "Doctor 不执行平台命令，因此当前不标记为可用。"
            )
        return "warn", st.hint
