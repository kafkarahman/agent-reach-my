# -*- coding: utf-8 -*-
"""TikTok — yt-dlp backend for video/user/hashtag access.

yt-dlp is the most reliable free method for TikTok scraping. No login required
for public content. Video metadata, captions (when available), and hashtag
search are all supported.
"""

import shutil

from agent_reach.probe import probe_command

from .base import Channel


class TikTokChannel(Channel):
    name = "tiktok"
    description = "TikTok 视频、用户和主题标签"
    backends = ["yt-dlp"]
    tier = 0  # No login required for public content

    def can_handle(self, url: str) -> bool:
        from agent_reach.utils.url import host_matches

        return host_matches(url, "tiktok.com", "vm.tiktok.com", "vt.tiktok.com")

    def check(self, config=None):
        """Check if yt-dlp is available and can handle TikTok."""
        probe = probe_command("yt-dlp", ["--version"], timeout=10, package="yt-dlp")
        if probe.status == "missing":
            self.active_backend = None
            return "off", (
                "未安装 yt-dlp。推荐：\n"
                "  桌面（推荐）：agent-reach install --system\n"
                "  服务器/存量：pip install yt-dlp\n"
                "  更新已安装版本：python -m pip install -U yt-dlp"
            )
        if probe.status == "broken":
            self.active_backend = None
            return "error", f"yt-dlp 已安装但无法执行：{probe.hint}"
        if not probe.ok:
            self.active_backend = None
            return "error", f"yt-dlp 无法正常运行：{probe.hint or probe.output}"

        self.active_backend = "yt-dlp"
        return "ok", "yt-dlp 已安装并就绪（支持 TikTok 公开内容，无需登录）"
