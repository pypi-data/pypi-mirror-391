"""Session state serialization for web UI backend.

This module provides a serializable data structure for storing web UI session state,
enabling support for both in-memory and Redis-based session storage.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
import json


@dataclass
class SessionState:
    """Serializable session state for NiceGUIBackend.

    This class represents all the state that needs to persist across requests
    when using Redis-backed session storage for load balancing.
    """

    # Version for future compatibility
    version: str = "1.0"

    # Session identification
    session_id: str = ""

    # Program content (line_number -> source_text)
    program_lines: Dict[int, str] = field(default_factory=dict)

    # Runtime state (serialized separately)
    runtime_state: Optional[Dict[str, Any]] = None

    # Execution state
    running: bool = False
    paused: bool = False
    output_text: str = ""
    current_file: Optional[str] = None
    recent_files: List[str] = field(default_factory=list)
    last_save_content: str = ""

    # Configuration
    max_recent_files: int = 10
    auto_save_enabled: bool = True
    auto_save_interval: int = 30

    # Find/Replace state
    last_find_text: str = ""
    last_find_position: int = 0
    last_case_sensitive: bool = False

    # Editor state
    editor_content: str = ""
    editor_cursor: Optional[int] = None

    # Auto-numbering state
    last_edited_line_index: Optional[int] = None
    last_edited_line_text: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for storage.

        Returns:
            dict: Serializable dictionary representation
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'SessionState':
        """Create SessionState from dictionary.

        Args:
            data: Dictionary from to_dict()

        Returns:
            SessionState: Restored session state
        """
        # Handle missing fields for backward compatibility
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def to_json(self) -> str:
        """Serialize to JSON string.

        Returns:
            str: JSON representation
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> 'SessionState':
        """Deserialize from JSON string.

        Args:
            json_str: JSON string from to_json()

        Returns:
            SessionState: Restored session state
        """
        return cls.from_dict(json.loads(json_str))
