# -*- coding: utf-8 -*-
"""Telegram — public channel monitoring and message search.

Telegram is a messaging platform with large public channels and communities.
This module accesses public channels using telethon or pyrogram, both of which
are Telegram client libraries. Login is required (via phone or bot token),
but only to access the Telegram API.
"""

from .base import Channel


class TelegramChannel(Channel):
    name = "telegram"
    description = "Telegram 公开频道和群组"
    backends = ["telethon", "pyrogram"]
    tier = 1  # Requires login (phone or bot token)

    def can_handle(self, url: str) -> bool:
        from agent_reach.utils.url import host_matches

        return host_matches(url, "telegram.org", "telegram.me", "t.me")

    def check(self, config=None):
        """Check if telethon or pyrogram is installed."""
        self.active_backend = None
        findings = []

        for backend in self.ordered_backends(config):
            if backend == "telethon":
                result = self._check_telethon()
            else:
                result = self._check_pyrogram()
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
            "未安装 Telegram 客户端库。推荐：\n"
            "  pip install telethon（稳定性更好）\n"
            "  或：pip install pyrogram\n"
            "首次使用需要登录（手机号或 Bot Token）"
        )

    def _check_telethon(self):
        """Check if telethon is installed."""
        try:
            import telethon
            return "warn", (
                "telethon 已安装，但 Doctor 未执行登录验证；"
                "请手动使用 Telegram 账户或 Bot Token 进行身份验证。"
            )
        except ImportError:
            return None

    def _check_pyrogram(self):
        """Check if pyrogram is installed."""
        try:
            import pyrogram
            return "warn", (
                "pyrogram 已安装，但 Doctor 未执行登录验证；"
                "请手动使用 Telegram 账户或 Bot Token 进行身份验证。"
            )
        except ImportError:
            return None
