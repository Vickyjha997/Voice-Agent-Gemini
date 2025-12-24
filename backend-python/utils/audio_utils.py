"""Audio utility functions for backend processing"""
import base64
from typing import Any


def decode_base64(base64_str: str) -> bytes:
    """Converts a base64 string to bytes."""
    return base64.b64decode(base64_str)


def encode_base64(data: bytes) -> str:
    """Converts bytes to base64 string."""
    return base64.b64encode(data).decode('utf-8')


def validate_audio_data(data: Any) -> bool:
    """Validates audio data format"""
    if not data or not isinstance(data, dict):
        return False
    if 'data' not in data or not isinstance(data['data'], str):
        return False
    if 'mimeType' not in data or 'audio' not in data['mimeType']:
        return False
    return True

