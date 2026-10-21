"""Working memory for the current session."""

from typing import Any


class WorkingMemory:
    """Holds current upload, search hits, and decision state."""

    def __init__(self) -> None:
        self.state: dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.state[key] = value

    def clear(self) -> None:
        self.state.clear()
