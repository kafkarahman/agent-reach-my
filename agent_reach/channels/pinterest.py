# -*- coding: utf-8 -*-
"""Pinterest — visual discovery and trend platform.

Pinterest is a visual-first social platform for pinning and discovering content.
yt-dlp supports Pinterest pin and board downloads. Public pins are accessible
without login.
"""

import shutil

from agent_reach.probe import probe_command

from .base import Channel


class PinterestChannel(Channel):
    name = "pinterest"
    description = "Pinterest 图钉、看板和用户"
    backends = ["yt-dlp", "pinterest-api"]
    tier = 0  # Public content, no login required for reading

    def can_handle(self, url: str) -> bool:
        from agent_reach.utils.url import host_matches

        return host_matches(url, "pinterest.com", "pin.it")

    def check(self, config=None):
        """Check if yt-dlp or Pinterest API is available."""
        self.active_backend = None
        findings = []

        for backend in self.ordered_backends(config):
            if backend == "yt-dlp":
                result = self._check_ytdlp()
            else:
                result = self._check_pinterest_api()
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
            "未安装任何 Pinterest 后端。推荐：\n"
            "  桌面：agent-reach install --system\n"
            "       （yt-dlp 支持 Pinterest）\n"
            "  服务器/存量：pip install -U yt-dlp"
        )

    def _check_ytdlp(self):
        """Check if yt-dlp is available."""
        probe = probe_command("yt-dlp", ["--version"], timeout=10, package="yt-dlp")
        if probe.status == "missing":
            return None
        if probe.status == "broken":
            return "error", f"yt-dlp 已安装但无法执行：{probe.hint}"
        if not probe.ok:
            return "warn", f"yt-dlp 已安装但验证失败：{probe.hint or probe.output}"

        self.active_backend = "yt-dlp"
        return "ok", "yt-dlp 已安装并就绪（支持 Pinterest）"

    def _check_pinterest_api(self):
        """Check if Pinterest Python API library is installed."""
        try:
            import pinterest_api
            return "warn", (
                "pinterest-api 已安装，但 Doctor 未执行实际 API 调用来验证连接。"
            )
        except ImportError:
            return None
