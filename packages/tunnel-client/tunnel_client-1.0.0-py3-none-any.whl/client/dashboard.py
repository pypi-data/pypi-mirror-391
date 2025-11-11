from __future__ import annotations

import asyncio
import json
from typing import List, Optional

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import httpx
import json as _json
from pathlib import Path
from sqlalchemy import select
from sqlalchemy import text as sql_text
from sqlalchemy.ext.asyncio import AsyncSession

from .database import init_db, get_session
from .models import LocalRequest, Settings, TcpStream, TcpEvent, UdpEvent


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
_static_dir = Path(__file__).with_name("static")
app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")


class WSManager:
    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._clients.add(ws)

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            self._clients.discard(ws)

    async def broadcast(self, payload: dict) -> None:
        async with self._lock:
            for ws in list(self._clients):
                try:
                    await ws.send_json(payload)
                except Exception:
                    self._clients.discard(ws)


ws_manager = WSManager()


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/")
async def index():
    return FileResponse(str(_static_dir / "index.html"))


@app.get("/api/requests")
async def list_requests(limit: int = 100, method: Optional[str] = None, status: Optional[int] = None, session: AsyncSession = Depends(get_session)):
    stmt = select(LocalRequest).order_by(LocalRequest.id.desc()).limit(limit)
    res = await session.execute(stmt)
    items = []
    for r in res.scalars().all():
        if method and r.method != method:
            continue
        if status and r.response_status != status:
            continue
        items.append({
            "id": r.id,
            "timestamp": r.timestamp.isoformat(),
            "method": r.method,
            "url": r.url,
            "status": r.response_status,
            "duration_ms": r.duration_ms,
        })
    return {"items": items}


@app.get("/api/requests/{req_id}")
async def get_request(req_id: int, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(LocalRequest).where(LocalRequest.id == req_id))
    r = res.scalar_one_or_none()
    if not r:
        return {"error": "not found"}
    return {
        "id": r.id,
        "timestamp": r.timestamp.isoformat(),
        "method": r.method,
        "url": r.url,
        "request_headers": r.request_headers,
        "request_body": (r.request_body or b"").decode(errors="ignore"),
        "response_status": r.response_status,
        "response_headers": r.response_headers,
        "response_body": (r.response_body or b"").decode(errors="ignore"),
        "duration_ms": r.duration_ms,
    }


def _normalize_headers(h: str | dict | None) -> dict:
    if h is None:
        return {}
    if isinstance(h, str):
        try:
            return _json.loads(h)
        except Exception:
            return {}
    return dict(h)


async def _send_local(method: str, path_or_url: str, headers: dict, body: Optional[str]) -> tuple[int, dict, bytes, int]:
    # Determine base URL from app.state.local_port set by client launcher
    local_port = getattr(app.state, "local_port", None)
    if not local_port:
        raise HTTPException(500, "Local port is not configured")
    url = path_or_url
    if not (url.startswith("http://") or url.startswith("https://")):
        if not url.startswith("/"):
            url = "/" + url
        url = f"http://127.0.0.1:{int(local_port)}{url}"
    data_bytes = (body or "").encode()
    async with httpx.AsyncClient(follow_redirects=True) as client:
        t0 = app.router.default.app_loop.time() if hasattr(app.router.default, 'app_loop') else None
        import time as _time
        t0 = _time.perf_counter()
        resp = await client.request(method, url, headers=headers, content=data_bytes)
        duration_ms = int((_time.perf_counter() - t0) * 1000)
        return resp.status_code, dict(resp.headers), bytes(resp.content), duration_ms


async def _log_and_broadcast(session: AsyncSession, method: str, url: str, req_headers: dict, req_body: bytes, status: int, res_headers: dict, res_body: bytes, duration_ms: int) -> dict:
    rec = LocalRequest(
        method=method,
        url=url,
        request_headers=_json.dumps(req_headers),
        request_body=req_body if req_body else None,
        response_status=status,
        response_headers=_json.dumps(res_headers),
        response_body=res_body if res_body else None,
        duration_ms=duration_ms,
    )
    session.add(rec)
    await session.commit()
    item = {
        "id": rec.id,
        "timestamp": rec.timestamp.isoformat(),
        "method": rec.method,
        "url": rec.url,
        "status": rec.response_status,
        "duration_ms": rec.duration_ms,
    }
    await ws_manager.broadcast({"type": "created", "item": item})
    return item


@app.post("/api/replay")
async def replay_raw(payload: dict, session: AsyncSession = Depends(get_session)):
    method = str(payload.get("method") or "GET").upper()
    url = str(payload.get("url") or payload.get("path") or "/")
    headers = _normalize_headers(payload.get("headers") or payload.get("request_headers"))
    body = payload.get("body") or payload.get("request_body")
    status, resp_headers, resp_body, duration_ms = await _send_local(method, url, headers, body)
    await _log_and_broadcast(session, method, url, headers, (body or "").encode(), status, resp_headers, resp_body, duration_ms)
    return {"status": status, "headers": resp_headers, "body": resp_body.decode(errors="ignore"), "duration_ms": duration_ms}


@app.post("/api/requests/{req_id}/replay")
async def replay_saved(req_id: int, payload: Optional[dict] = None, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(LocalRequest).where(LocalRequest.id == req_id))
    r = res.scalar_one_or_none()
    if not r:
        raise HTTPException(404, "not found")
    # Build from saved with optional overrides
    method = (payload or {}).get("method") or r.method
    url = (payload or {}).get("url") or (payload or {}).get("path") or r.url
    headers_in = (payload or {}).get("headers") or (payload or {}).get("request_headers") or r.request_headers
    body_in = (payload or {}).get("body") or (payload or {}).get("request_body") or (r.request_body or b"").decode(errors="ignore")
    headers = _normalize_headers(headers_in)
    status, resp_headers, resp_body, duration_ms = await _send_local(method, url, headers, body_in)
    await _log_and_broadcast(session, method, url, headers, (body_in or "").encode(), status, resp_headers, resp_body, duration_ms)
    return {"status": status, "headers": resp_headers, "body": resp_body.decode(errors="ignore"), "duration_ms": duration_ms}


# TCP/UDP Dashboard APIs
@app.get("/api/tcp/streams")
async def list_tcp_streams(limit: int = 100, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(TcpStream).order_by(TcpStream.opened_at.desc()).limit(limit))
    items = []
    for s in res.scalars().all():
        items.append({
            "stream_id": s.stream_id,
            "opened_at": s.opened_at.isoformat(),
            "closed_at": s.closed_at.isoformat() if s.closed_at else None,
            "bytes_in": s.bytes_in,
            "bytes_out": s.bytes_out,
        })
    return {"items": items}


@app.get("/api/tcp/streams/{stream_id}/events")
async def list_tcp_events(stream_id: str, limit: int = 200, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(TcpEvent).where(TcpEvent.stream_id == stream_id).order_by(TcpEvent.id.desc()).limit(limit))
    items = []
    for e in res.scalars().all():
        sample_bytes = e.sample or b""
        items.append({
            "id": e.id,
            "timestamp": e.timestamp.isoformat(),
            "direction": e.direction,
            "size": e.size,
            "sample_hex": sample_bytes.hex(),
            "sample_text": sample_bytes.decode(errors="replace", encoding="utf-8")[:1024],
        })
    return {"items": items}


from .control_bus import enqueue as enqueue_command  # lazy import ok


@app.post("/api/tcp/streams/{stream_id}/send")
async def tcp_send(stream_id: str, payload: dict):
    data = payload.get("data") or ""
    mode = (payload.get("mode") or "text").lower()  # 'text' or 'hex'
    if mode == "hex":
        try:
            raw = bytes.fromhex(data)
        except Exception:
            raise HTTPException(400, "Invalid hex data")
    else:
        raw = data.encode()
    await enqueue_command({"type": "tcp_send", "stream_id": stream_id, "data": raw})
    return {"status": "ok"}


@app.post("/api/tcp/streams/{stream_id}/close")
async def tcp_close(stream_id: str):
    await enqueue_command({"type": "tcp_close", "stream_id": stream_id})
    return {"status": "ok"}


@app.get("/api/udp/events")
async def list_udp_events(limit: int = 200, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(UdpEvent).order_by(UdpEvent.id.desc()).limit(limit))
    items = []
    for e in res.scalars().all():
        sample_bytes = e.sample or b""
        items.append({
            "id": e.id,
            "timestamp": e.timestamp.isoformat(),
            "addr": e.addr,
            "direction": e.direction,
            "size": e.size,
            "sample_hex": sample_bytes.hex(),
            "sample_text": sample_bytes.decode(errors="replace", encoding="utf-8")[:1024],
        })
    return {"items": items}


@app.post("/api/udp/send")
async def udp_send(payload: dict):
    addr = payload.get("addr") or {}
    ip = str(addr.get("ip") or addr[0] if isinstance(addr, list) else "")
    port = int(addr.get("port") or addr[1] if isinstance(addr, list) else 0)
    if not ip or not port:
        raise HTTPException(400, "addr is required")
    data = payload.get("data") or ""
    mode = (payload.get("mode") or "text").lower()
    if mode == "hex":
        try:
            raw = bytes.fromhex(data)
        except Exception:
            raise HTTPException(400, "Invalid hex data")
    else:
        raw = data.encode()
    await enqueue_command({"type": "udp_send", "addr": [ip, port], "data": raw})
    return {"status": "ok"}


# Broadcast helpers for tunnel client
async def broadcast_tcp_stream_opened(stream_id: str) -> None:
    await ws_manager.broadcast({"type": "tcp_stream_opened", "stream_id": stream_id})


async def broadcast_tcp_stream_closed(stream_id: str) -> None:
    await ws_manager.broadcast({"type": "tcp_stream_closed", "stream_id": stream_id})


async def broadcast_tcp_event(event: dict) -> None:
    await ws_manager.broadcast({"type": "tcp_event", "event": event})


async def broadcast_udp_event(event: dict) -> None:
    await ws_manager.broadcast({"type": "udp_event", "event": event})


@app.delete("/api/requests")
async def clear_requests(session: AsyncSession = Depends(get_session)):
    await session.execute(sql_text("DELETE FROM local_requests"))
    await session.commit()
    return {"status": "cleared"}


@app.get("/api/connection/status")
async def get_connection_status():
    """Get current tunnel connection status."""
    status = getattr(app.state, "connection_status", "unknown")
    is_connected = getattr(app.state, "tunnel_client", None) is not None and (
        hasattr(app.state.tunnel_client, "_is_connected") and 
        app.state.tunnel_client._is_connected
    )
    
    # Double-check WebSocket status
    client = getattr(app.state, "tunnel_client", None)
    if client and hasattr(client, "_ws") and client._ws is not None:
        is_connected = True
        status = "connected"
    elif client and not is_connected:
        status = "disconnected"
    
    # Get subdomain from client or settings
    subdomain = None
    if client and hasattr(client, "_subdomain"):
        subdomain = client._subdomain
    
    # If no subdomain from client, try to get from settings
    if not subdomain:
        async for session in get_session():
            res = await session.execute(select(Settings).order_by(Settings.id.asc()))
            s = res.scalars().first()
            if s and s.selected_subdomain:
                subdomain = s.selected_subdomain
            break
    
    # Generate public URL
    public_url = None
    if subdomain:
        public_url = f"https://{subdomain}.tunnel.tunneloon.online"
    
    return {
        "status": status,
        "connected": is_connected,
        "subdomain": subdomain,
        "public_url": public_url,
    }


@app.get("/api/settings")
async def get_settings(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(Settings).order_by(Settings.id.asc()))
    s = res.scalars().first()
    if not s:
        s = Settings()
        session.add(s)
        await session.commit()
        await session.refresh(s)
    return {
        "server_url": "",  # Server is hardcoded, don't expose
        "local_port": s.local_port,
        "selected_subdomain": s.selected_subdomain,
        "rate_limit_per_minute": s.rate_limit_per_minute,
        "custom_response_enabled": bool(s.custom_response_enabled or 0),
        "custom_response_status": s.custom_response_status or 200,
        "custom_response_headers": s.custom_response_headers or "{}",
        "custom_response_body": s.custom_response_body or "",
    }


@app.post("/api/settings")
async def update_settings(payload: dict, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(Settings).order_by(Settings.id.asc()))
    s = res.scalars().first()
    if not s:
        s = Settings()
        session.add(s)
    # Update all fields that might be present
    # Server URL is hardcoded, ignore if present
    if "local_port" in payload:
        s.local_port = payload["local_port"]
    if "selected_subdomain" in payload:
        s.selected_subdomain = payload["selected_subdomain"]
    if "rate_limit_per_minute" in payload:
        s.rate_limit_per_minute = payload["rate_limit_per_minute"]
    if "custom_response_enabled" in payload:
        s.custom_response_enabled = 1 if payload["custom_response_enabled"] else 0
    if "custom_response_status" in payload:
        s.custom_response_status = payload.get("custom_response_status") or 200
    if "custom_response_headers" in payload:
        s.custom_response_headers = payload.get("custom_response_headers") or "{}"
    if "custom_response_body" in payload:
        s.custom_response_body = payload.get("custom_response_body") or ""
    await session.commit()
    return {"status": "ok"}


@app.post("/api/generate-subdomain")
async def generate_subdomain(session: AsyncSession = Depends(get_session)):
    """Generate a random subdomain and save it."""
    from .utils import generate_random_subdomain
    subdomain = generate_random_subdomain()
    res = await session.execute(select(Settings).order_by(Settings.id.asc()))
    s = res.scalars().first()
    if not s:
        s = Settings()
        session.add(s)
    s.selected_subdomain = subdomain
    await session.commit()
    return {"subdomain": subdomain}


@app.websocket("/ws")
async def ws(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        while True:
            await ws.receive_text()  # keepalive/no-op
    except WebSocketDisconnect:
        pass
    finally:
        await ws_manager.disconnect(ws)


async def broadcast_request_created(item: dict) -> None:
    await ws_manager.broadcast({"type": "created", "item": item})


