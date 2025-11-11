"""Utility functions for client."""
from __future__ import annotations

import random
import string
from urllib.parse import urlparse


def normalize_server_url(server_input: str) -> str:
    """
    Convert HTTP/HTTPS URL to WebSocket URL.
    
    Examples:
        https://tunnel.example.com -> wss://tunnel.example.com
        http://localhost:8081 -> ws://localhost:8081
        wss://already.ws -> wss://already.ws (unchanged)
        ws://already.ws -> ws://already.ws (unchanged)
    """
    server_input = server_input.strip()
    
    # If already WebSocket URL, return as-is
    if server_input.startswith(("ws://", "wss://")):
        return server_input
    
    # If HTTP/HTTPS, convert to WS/WSS
    if server_input.startswith("http://"):
        return server_input.replace("http://", "ws://", 1)
    if server_input.startswith("https://"):
        return server_input.replace("https://", "wss://", 1)
    
    # If no protocol, assume HTTPS -> WSS
    if not server_input.startswith(("http://", "https://", "ws://", "wss://")):
        return f"wss://{server_input}"
    
    return server_input


def generate_random_subdomain(length: int = 8) -> str:
    """Generate a random subdomain name."""
    chars = string.ascii_lowercase + string.digits
    # First char must be letter
    first = random.choice(string.ascii_lowercase)
    rest = ''.join(random.choice(chars) for _ in range(length - 1))
    return f"{first}{rest}"

