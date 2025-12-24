"""Type definitions for the Gemini Live Backend"""
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, field


class ConnectionState(str, Enum):
    """WebSocket connection states"""
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    ERROR = "ERROR"


@dataclass
class TranscriptionData:
    """Transcription data structure"""
    text: str
    is_user: bool
    is_final: bool


@dataclass
class FunctionCall:
    """Function call structure"""
    name: str
    args: Dict[str, Any]
    call_id: str


@dataclass
class FunctionResult:
    """Function result structure"""
    call_id: str
    result: Any
    error: Optional[str] = None


@dataclass
class Session:
    """Session data structure"""
    id: str
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    gemini_session: Any = None
    gemini_context_manager: Any = None  # Store context manager for proper cleanup
    memory: List[Dict[str, str]] = field(default_factory=list)

