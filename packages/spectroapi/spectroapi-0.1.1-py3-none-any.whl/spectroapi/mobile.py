# spectroapi/mobile.py

"""
This is NOT officially supported by Discord;
Use at your own risk.
"""

from __future__ import annotations

from typing import Any, Dict

from discord.gateway import DiscordWebSocket


class SpectroMobileWebSocket(DiscordWebSocket):
    async def send_as_json(self, data: Dict[str, Any]) -> None:
        try:
            if data.get("op") == self.IDENTIFY:
                props = data.get("d", {}).get("properties", {})
                if isinstance(props, dict):
                    props["$browser"] = "Discord iOS"
                    props["$device"] = "Discord iOS"
        except Exception:
            pass

        await super().send_as_json(data)


def enable_mobile_status() -> None:
    DiscordWebSocket.from_client = SpectroMobileWebSocket.from_client  
