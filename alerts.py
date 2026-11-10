"""Notification-only Discord embeds for governance draft and audit events."""
from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse


def send_embed(webhook: str, title: str, description: str, fields: list[dict], color: int) -> None:
    if urlparse(webhook).scheme.lower() not in {"http", "https"}:
        raise ValueError("webhook must be HTTP(S)")
    body = {"allowed_mentions": {"parse": []}, "embeds": [{"title": title[:256], "description": description[:4000], "fields": fields[:25], "color": color, "timestamp": datetime.now(timezone.utc).isoformat(), "footer": {"text": "Governance Core • notification only"}}]}
    request = urllib.request.Request(webhook, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=15) as response:  # nosec B310: URL scheme allowlist above
        if response.status >= 300:
            raise RuntimeError(f"Discord returned HTTP {response.status}")


def notify_audit(summary: dict) -> None:
    webhook = os.environ.get("DISCORD_WEBHOOK", "").strip()
    if webhook:
        send_embed(webhook, "Governance vote audit update", "Read-only weighted vote summary; no proposal was executed.", [{"name": "Support", "value": f"{summary['support_percent']}%", "inline": True}, {"name": "Quorum", "value": f"{summary['quorum_percent']}%", "inline": True}, {"name": "Status", "value": "Reached" if summary["quorum_reached"] else "Not reached", "inline": True}], 3447003)
