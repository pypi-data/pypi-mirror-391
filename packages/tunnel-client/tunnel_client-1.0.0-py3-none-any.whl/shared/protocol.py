from __future__ import annotations

from typing import Dict, Optional, Literal, List, Tuple
from pydantic import BaseModel, Field, constr


SubdomainStr = constr(strip_whitespace=True, to_lower=True, min_length=1, max_length=63)


class RegisterMessage(BaseModel):
    type: Literal["register"] = "register"
    subdomain: SubdomainStr
    local_port: int = Field(ge=1, le=65535)


class RequestMessage(BaseModel):
    type: Literal["request"] = "request"
    request_id: str
    method: str
    path: str
    headers: Dict[str, str]
    body: Optional[str] = None  # base64 encoded


class RequestChunkMessage(BaseModel):
    type: Literal["request_chunk"] = "request_chunk"
    request_id: str
    chunk: str  # base64 chunk
    final: bool = False


class ResponseMessage(BaseModel):
    type: Literal["response"] = "response"
    request_id: str
    status: int
    headers: Dict[str, str]
    body: Optional[str] = None  # base64 encoded
    duration_ms: int


class ResponseChunkMessage(BaseModel):
    type: Literal["response_chunk"] = "response_chunk"
    request_id: str
    chunk: str  # base64 chunk
    final: bool = False


class ErrorMessage(BaseModel):
    type: Literal["error"] = "error"
    request_id: Optional[str] = None
    code: str
    message: str


class RegisteredMessage(BaseModel):
    type: Literal["registered"] = "registered"
    url: str
    status: Literal["success", "error"] = "success"
    message: Optional[str] = None
    # Optional: assigned ports for TCP/UDP tunneling on server
    tcp_port: Optional[int] = None
    udp_port: Optional[int] = None


# TCP tunneling messages
class TcpOpenMessage(BaseModel):
    type: Literal["tcp_open"] = "tcp_open"
    stream_id: str


class TcpDataMessage(BaseModel):
    type: Literal["tcp_data"] = "tcp_data"
    stream_id: str
    chunk: str  # base64


class TcpCloseMessage(BaseModel):
    type: Literal["tcp_close"] = "tcp_close"
    stream_id: str
    reason: Optional[str] = None


# UDP tunneling messages
class UdpDataMessage(BaseModel):
    type: Literal["udp_data"] = "udp_data"
    addr: Tuple[str, int]  # (ip, port) of remote peer
    chunk: str  # base64


ProtocolMessage = (
    RegisterMessage
    | RequestMessage
    | RequestChunkMessage
    | ResponseMessage
    | ResponseChunkMessage
    | ErrorMessage
    | RegisteredMessage
    | TcpOpenMessage
    | TcpDataMessage
    | TcpCloseMessage
    | UdpDataMessage
)


