from __future__ import annotations

import asyncio
import base64
import json
import time
from typing import Optional
import logging

import httpx
from websockets.client import connect as ws_connect
from websockets.exceptions import ConnectionClosed
from collections import deque

from .database import get_session
from .dashboard import (
    broadcast_request_created,
    broadcast_tcp_stream_opened,
    broadcast_tcp_stream_closed,
    broadcast_tcp_event,
    broadcast_udp_event,
)
from .models import LocalRequest, TcpStream, TcpEvent, UdpEvent
from .models import Settings
from sqlalchemy import select
from .control_bus import get_queue as get_control_queue


class TunnelClient:
    def __init__(self) -> None:
        self._stop_event = asyncio.Event()
        self._server_url: Optional[str] = None
        self._subdomain: Optional[str] = None
        self._local_port: Optional[int] = None
        # TCP streams: stream_id -> (reader, writer)
        self._tcp_streams: dict[str, tuple[asyncio.StreamReader, asyncio.StreamWriter]] = {}
        # UDP socket for local service
        self._udp_transport: Optional[asyncio.DatagramTransport] = None
        self._udp_protocol: Optional[asyncio.DatagramProtocol] = None
        self._ws = None
        self._is_connected = False

    async def _load_subdomain_from_settings(self) -> str:
        """Load current subdomain from Settings, with fallback to provided default."""
        try:
            async for session in get_session():
                res = await session.execute(select(Settings).order_by(Settings.id.asc()))
                s = res.scalars().first()
                if s and s.selected_subdomain:
                    return str(s.selected_subdomain).strip().lower()
        except Exception:
            pass
        return ""

    async def connect(self, server_url: str, subdomain: str, local_port: int) -> None:
        self._server_url = server_url
        self._local_port = local_port
        # Initial subdomain: try Settings first, fallback to provided
        settings_subdomain = await self._load_subdomain_from_settings()
        actual_subdomain = settings_subdomain if settings_subdomain else subdomain.strip().lower()
        self._subdomain = actual_subdomain
        
        backoff = 1
        while not self._stop_event.is_set():
            # Re-check Settings before each reconnect to get latest subdomain
            settings_subdomain = await self._load_subdomain_from_settings()
            if settings_subdomain:
                actual_subdomain = settings_subdomain
                self._subdomain = actual_subdomain
            elif not self._subdomain:
                actual_subdomain = subdomain.strip().lower()
                self._subdomain = actual_subdomain
            
            settings_task = None
            control_task = None
            
            try:
                logging.info(f"Connecting with subdomain: {actual_subdomain}")
                async with ws_connect(f"{server_url}/tunnel/connect") as ws:
                    self._ws = ws
                    await ws.send(json.dumps({
                        "type": "register",
                        "subdomain": actual_subdomain,
                        "local_port": local_port,
                    }))
                    # await confirmation
                    reg = json.loads(await ws.recv())
                    if reg.get("status") != "success":
                        logging.error(f"Registration failed: {reg}")
                        await asyncio.sleep(backoff)
                        backoff = min(backoff * 2, 30)
                        continue
                    
                    try:
                        tcp_p = reg.get("tcp_port")
                        udp_p = reg.get("udp_port")
                        if tcp_p or udp_p:
                            logging.info(f"Registered '{actual_subdomain}': TCP port {tcp_p}, UDP port {udp_p}")
                        else:
                            logging.info(f"Registered '{actual_subdomain}'")
                    except Exception:
                        pass
                    backoff = 1
                    self._is_connected = True
                    # Update status in dashboard if available
                    try:
                        from .dashboard import app as dashboard_app
                        if hasattr(dashboard_app.state, 'connection_status'):
                            dashboard_app.state.connection_status = "connected"
                    except Exception:
                        pass

                    # Monitor settings changes - close WS if subdomain changes
                    async def monitor_settings_change():
                        while True:
                            await asyncio.sleep(2)  # Check every 2 seconds
                            if self._stop_event.is_set():
                                return
                            try:
                                new_subdomain = await self._load_subdomain_from_settings()
                                current = self._subdomain
                                # If Settings has a subdomain and it differs, reconnect
                                if new_subdomain and new_subdomain != current:
                                    logging.info(f"Subdomain changed from '{current}' to '{new_subdomain}', reconnecting...")
                                    self._subdomain = new_subdomain
                                    try:
                                        await ws.close(code=4001, reason="subdomain_changed")
                                    except Exception:
                                        pass
                                    return
                                # If Settings is empty but we have a subdomain from CLI, keep it
                            except Exception as e:
                                logging.debug(f"Settings check error: {e}")
                                pass

                    settings_task = asyncio.create_task(monitor_settings_change())
                    control_task = asyncio.create_task(self._consume_control_commands())
                    
                    # Main message loop
                    while True:
                        msg = json.loads(await ws.recv())
                        mtype = msg.get("type")
                        if mtype == "request":
                            await self.handle_request(ws, msg)
                        elif mtype == "tcp_open":
                            await self.handle_tcp_open(ws, msg)
                        elif mtype == "tcp_data":
                            await self.handle_tcp_data_from_server(msg)
                        elif mtype == "tcp_close":
                            await self.handle_tcp_close_from_server(msg)
                        elif mtype == "udp_data":
                            await self.handle_udp_from_server(ws, msg)
                            
            except ConnectionClosed as e:
                logging.debug(f"WebSocket disconnected: code={e.code}, reason={e.reason}")
                # Settings task will detect change and trigger reconnect
            except Exception as e:
                error_msg = str(e)
                if "Name or service not known" in error_msg or "SERVFAIL" in error_msg:
                    logging.error(f"DNS resolution failed for {server_url}. Check if the domain exists and DNS is configured correctly.")
                elif "Connection refused" in error_msg:
                    logging.error(f"Connection refused to {server_url}. Server might be down or not listening on this address.")
                elif "timeout" in error_msg.lower():
                    logging.error(f"Connection timeout to {server_url}. Check network connectivity and firewall.")
                else:
                    logging.warning(f"Connection error (will retry): {e}")
            finally:
                # Cancel background tasks
                if settings_task:
                    try:
                        settings_task.cancel()
                        await asyncio.gather(settings_task, return_exceptions=True)
                    except Exception:
                        pass
                if control_task:
                    try:
                        control_task.cancel()
                        await asyncio.gather(control_task, return_exceptions=True)
                    except Exception:
                        pass
                self._ws = None
                self._is_connected = False
                # Update status in dashboard
                try:
                    from .dashboard import app as dashboard_app
                    if hasattr(dashboard_app.state, 'connection_status'):
                        dashboard_app.state.connection_status = "disconnected"
                except Exception:
                    pass
                
            # If stop requested, exit loop
            if self._stop_event.is_set():
                break
            
            # Backoff before reconnect
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30)

    async def handle_request(self, ws, message: dict) -> None:
        request_id = message.get("request_id")
        method = message.get("method")
        path = message.get("path")
        headers = message.get("headers", {})
        body_b64 = message.get("body")
        body = base64.b64decode(body_b64) if body_b64 else b""
        t0 = time.perf_counter()
        # Load settings once per request (ORM)
        custom = None
        rate_limit_per_minute = None
        try:
            async for session in get_session():
                res = await session.execute(select(Settings).order_by(Settings.id.asc()))
                s = res.scalars().first()
                if s:
                    rate_limit_per_minute = s.rate_limit_per_minute
                    if s.custom_response_enabled:
                        custom = {
                            "status": int(s.custom_response_status or 200),
                            "headers": json.loads(s.custom_response_headers or "{}"),
                            "body": (s.custom_response_body or "").encode(),
                        }
        except Exception:
            pass

        # Apply client-side rate limit if set
        if rate_limit_per_minute and rate_limit_per_minute > 0:
            if not hasattr(self, "_rate_events"):
                self._rate_events = deque()
            now = time.monotonic()
            window_start = now - 60.0
            while self._rate_events and self._rate_events[0] < window_start:
                self._rate_events.popleft()
            if len(self._rate_events) >= int(rate_limit_per_minute):
                # Too many requests: return 429 immediately
                await self.send_response(ws, request_id, 429, {"content-type": "text/plain"}, b"Rate limit exceeded", int((time.perf_counter() - t0) * 1000))
                return
            self._rate_events.append(now)

        try:
            if custom is not None:
                status, resp_headers, resp_body = custom["status"], custom["headers"], custom["body"]
            else:
                status, resp_headers, resp_body = await self.forward_to_local(method, path, headers, body)
        except Exception:
            status, resp_headers, resp_body = 502, {"content-type": "text/plain"}, b"Bad gateway"
        duration_ms = int((time.perf_counter() - t0) * 1000)

        await self.send_response(ws, request_id, status, resp_headers, resp_body, duration_ms)
        item = await self._log_local_request(method, path, headers, body, status, resp_headers, resp_body, duration_ms)
        try:
            await broadcast_request_created(item)
        except Exception:
            pass

    async def _ensure_udp(self) -> None:
        if self._udp_transport is not None:
            return
        loop = asyncio.get_running_loop()
        class _ClientUdp(asyncio.DatagramProtocol):
            pass
        transport, protocol = await loop.create_datagram_endpoint(lambda: _ClientUdp(), local_addr=("127.0.0.1", 0))
        self._udp_transport = transport
        self._udp_protocol = protocol  # type: ignore[assignment]

    async def handle_udp_from_server(self, ws, message: dict) -> None:
        # message: { type: 'udp_data', addr: [ip, port], chunk: base64 }
        await self._ensure_udp()
        try:
            data = base64.b64decode(message.get("chunk") or "")
        except Exception:
            data = b""
        # forward to local UDP service
        if self._udp_transport is not None:
            self._udp_transport.sendto(data, ("127.0.0.1", int(self._local_port or 0)))
        # Log and broadcast UDP IN event
        try:
            async for session in get_session():
                addr = message.get("addr") or ["", 0]
                rec = UdpEvent(addr=f"{addr[0]}:{int(addr[1])}", direction="in", size=len(data), sample=data[:256])
                session.add(rec)
                await session.commit()
            await broadcast_udp_event({"direction": "in", "size": len(data)})
        except Exception:
            pass

    async def handle_tcp_open(self, ws, message: dict) -> None:
        stream_id = str(message.get("stream_id"))
        try:
            reader, writer = await asyncio.open_connection("127.0.0.1", int(self._local_port or 0))
        except Exception:
            # if cannot open local, immediately close stream on server
            await ws.send(json.dumps({"type": "tcp_close", "stream_id": stream_id, "reason": "local_connect_failed"}))
            return
        self._tcp_streams[stream_id] = (reader, writer)

        # Log stream open
        try:
            async for session in get_session():
                s = TcpStream(stream_id=stream_id)
                session.add(s)
                await session.commit()
            await broadcast_tcp_stream_opened(stream_id)
        except Exception:
            pass

        async def pump_local_to_server():
            try:
                while True:
                    data = await reader.read(64 * 1024)
                    if not data:
                        break
                    await ws.send(json.dumps({
                        "type": "tcp_data",
                        "stream_id": stream_id,
                        "chunk": base64.b64encode(data).decode(),
                    }))
                    # log event OUT and increment bytes_out
                    try:
                        async for session in get_session():
                            session.add(TcpEvent(stream_id=stream_id, direction="out", size=len(data), sample=data[:256]))
                            await session.execute(
                                __import__('sqlalchemy').text("UPDATE tcp_streams SET bytes_out = bytes_out + :n WHERE stream_id = :sid"),
                                {"n": len(data), "sid": stream_id},
                            )
                            await session.commit()
                        await broadcast_tcp_event({"stream_id": stream_id, "direction": "out", "size": len(data)})
                    except Exception:
                        pass
            except Exception:
                pass
            finally:
                try:
                    await ws.send(json.dumps({"type": "tcp_close", "stream_id": stream_id}))
                except Exception:
                    pass

        asyncio.create_task(pump_local_to_server())

    async def handle_tcp_data_from_server(self, message: dict) -> None:
        stream_id = str(message.get("stream_id"))
        data_b64 = message.get("chunk") or ""
        pair = self._tcp_streams.get(stream_id)
        if not pair:
            return
        reader, writer = pair
        try:
            data = base64.b64decode(data_b64)
            writer.write(data)
            await writer.drain()
            # log event IN and increment bytes_in
            try:
                async for session in get_session():
                    session.add(TcpEvent(stream_id=stream_id, direction="in", size=len(data), sample=data[:256]))
                    await session.execute(
                        __import__('sqlalchemy').text("UPDATE tcp_streams SET bytes_in = bytes_in + :n WHERE stream_id = :sid"),
                        {"n": len(data), "sid": stream_id},
                    )
                    await session.commit()
                await broadcast_tcp_event({"stream_id": stream_id, "direction": "in", "size": len(data)})
            except Exception:
                pass
        except Exception:
            pass

    async def handle_tcp_close_from_server(self, message: dict) -> None:
        stream_id = str(message.get("stream_id"))
        pair = self._tcp_streams.pop(stream_id, None)
        if not pair:
            return
        reader, writer = pair
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass
        # mark stream closed
        try:
            async for session in get_session():
                await session.execute(
                    __import__('sqlalchemy').text("UPDATE tcp_streams SET closed_at = CURRENT_TIMESTAMP WHERE stream_id = :sid"),
                    {"sid": stream_id},
                )
                await session.commit()
            await broadcast_tcp_stream_closed(stream_id)
        except Exception:
            pass

    async def _consume_control_commands(self) -> None:
        q = get_control_queue()
        while True:
            cmd = await q.get()
            t = cmd.get("type")
            if t == "tcp_send":
                stream_id = cmd.get("stream_id")
                raw: bytes = cmd.get("data") or b""
                pair = self._tcp_streams.get(stream_id)
                if pair:
                    _, writer = pair
                    try:
                        writer.write(raw)
                        await writer.drain()
                        # mirror as OUT event
                        try:
                            async for session in get_session():
                                session.add(TcpEvent(stream_id=stream_id, direction="out", size=len(raw), sample=raw[:256]))
                                await session.execute(
                                    __import__('sqlalchemy').text("UPDATE tcp_streams SET bytes_out = bytes_out + :n WHERE stream_id = :sid"),
                                    {"n": len(raw), "sid": stream_id},
                                )
                                await session.commit()
                            await broadcast_tcp_event({"stream_id": stream_id, "direction": "out", "size": len(raw)})
                        except Exception:
                            pass
                    except Exception:
                        pass
            elif t == "tcp_close":
                stream_id = cmd.get("stream_id")
                pair = self._tcp_streams.get(stream_id)
                if pair and self._ws is not None:
                    try:
                        await self._ws.send(json.dumps({"type": "tcp_close", "stream_id": stream_id}))
                    except Exception:
                        pass
            elif t == "udp_send":
                addr = cmd.get("addr") or ["", 0]
                raw: bytes = cmd.get("data") or b""
                if self._ws is not None:
                    try:
                        await self._ws.send(json.dumps({
                            "type": "udp_data",
                            "addr": addr,
                            "chunk": base64.b64encode(raw).decode(),
                        }))
                        # log UDP OUT
                        try:
                            async for session in get_session():
                                session.add(UdpEvent(addr=f"{addr[0]}:{int(addr[1])}", direction="out", size=len(raw), sample=raw[:256]))
                                await session.commit()
                            await broadcast_udp_event({"direction": "out", "size": len(raw)})
                        except Exception:
                            pass
                    except Exception:
                        pass

    async def forward_to_local(self, method: str, path: str, headers: dict, body: bytes):
        url = f"http://127.0.0.1:{self._local_port}{path}"
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.request(method, url, headers=headers, content=body)
            return resp.status_code, dict(resp.headers), bytes(resp.content)

    async def send_response(self, ws, request_id: str, status: int, headers: dict, body: bytes, duration_ms: int) -> None:
        await ws.send(json.dumps({
            "type": "response",
            "request_id": request_id,
            "status": status,
            "headers": headers,
            "body": base64.b64encode(body).decode() if body else None,
            "duration_ms": duration_ms,
        }))

    async def _log_local_request(
        self,
        method: str,
        path: str,
        req_headers: dict,
        req_body: bytes,
        status: int,
        resp_headers: dict,
        resp_body: bytes,
        duration_ms: int,
    ) -> dict:
        async for session in get_session():
            rec = LocalRequest(
                method=method,
                url=path,
                request_headers=json.dumps(req_headers),
                request_body=req_body if req_body else None,
                response_status=status,
                response_headers=json.dumps(resp_headers),
                response_body=resp_body if resp_body else None,
                duration_ms=duration_ms,
            )
            session.add(rec)
            await session.commit()
            return {
                "id": rec.id,
                "timestamp": rec.timestamp.isoformat(),
                "method": rec.method,
                "url": rec.url,
                "status": rec.response_status,
                "duration_ms": rec.duration_ms,
            }

    async def stop(self) -> None:
        self._stop_event.set()


