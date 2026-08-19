# -*- coding: utf-8 -*-
"""Lemon8 — Malaysia/SEA lifestyle platform (ByteDance-owned).

Lemon8 is ByteDance's lifestyle social app popular in Malaysia and across SEA.
Access requires browser automation (e.g. OpenCLI) or unofficial API client.
This module prioritizes OpenCLI for its browser-based integration, with optional
fallback to unofficial Python library if available.
"""

from .base import Channel


class Lemon8Channel(Channel):
    name = "lemon8"
    description = "Lemon8 内容和用户（马来西亚/东南亚生活方式平台）"
    backends = ["OpenCLI", "lemon8-api"]
    tier = 1  # Needs login for most content

    def can_handle(self, url: str) -> bool:
        from agent_reach.utils.url import host_matches

        return host_matches(url, "lemon8.com", "lemon8app.com")

    def check(self, config=None):
        """Probe OpenCLI first, then unofficial API library."""
        self.active_backend = None
        findings = []

        for backend in self.ordered_backends(config):
            if backend == "OpenCLI":
                result = self._check_opencli()
            else:
                result = self._check_lemon8_api()
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
            "未安装任何 Lemon8 后端。推荐：\n"
            "  桌面：agent-reach install --system --channels opencli\n"
            "       （复用 Chrome 登录态，登录过 lemon8.com 即可用）\n"
            "  服务器/存量：pip install lemon8-api"
        )

    def _check_opencli(self):
        """OpenCLI candidate for browser-based access."""
        from agent_reach.backends import opencli_status

        st = opencli_status()
        if not st.installed:
            return None
        if st.broken:
            return "error", st.hint
        if st.ready:
            return "warn", (
                "OpenCLI 桥接已连接，但 Lemon8 登录态和实际命令未实时验证；"
                "Doctor 不执行平台命令，因此当前不标记为可用。"
            )
        return "warn", st.hint

    def _check_lemon8_api(self):
        """Check if lemon8-api Python library is installed."""
        try:
            import lemon8_api
            return "warn", (
                "lemon8-api 已安装，但 Doctor 未执行实际 API 调用来验证连接；"
                "请手动测试 Lemon8 API 的登录状态和 token 有效性。"
            )
        except ImportError:
            return None
