from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Text, LargeBinary, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class LocalRequest(Base):
    __tablename__ = "local_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    method: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    request_headers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    request_body: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    response_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_headers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_body: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    server_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # WebSocket URL (wss:// or ws://)
    local_port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # Local port to tunnel
    selected_subdomain: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    rate_limit_per_minute: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    custom_response_enabled: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0/1
    custom_response_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    custom_response_headers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    custom_response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class TcpStream(Base):
    __tablename__ = "tcp_streams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stream_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    bytes_in: Mapped[int] = mapped_column(Integer, default=0)
    bytes_out: Mapped[int] = mapped_column(Integer, default=0)


class TcpEvent(Base):
    __tablename__ = "tcp_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stream_id: Mapped[str] = mapped_column(String, index=True)
    direction: Mapped[str] = mapped_column(String)  # 'in' or 'out'
    size: Mapped[int] = mapped_column(Integer)
    sample: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UdpEvent(Base):
    __tablename__ = "udp_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    addr: Mapped[str] = mapped_column(String)  # 'ip:port'
    direction: Mapped[str] = mapped_column(String)  # 'in' or 'out'
    size: Mapped[int] = mapped_column(Integer)
    sample: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

