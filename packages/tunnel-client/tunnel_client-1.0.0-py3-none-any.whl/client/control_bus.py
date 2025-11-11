from __future__ import annotations

import asyncio
from typing import Dict, Any

_queue: asyncio.Queue[Dict[str, Any]] | None = None


def get_queue() -> asyncio.Queue[Dict[str, Any]]:
    global _queue
    if _queue is None:
        _queue = asyncio.Queue()
    return _queue


async def enqueue(cmd: Dict[str, Any]) -> None:
    await get_queue().put(cmd)


