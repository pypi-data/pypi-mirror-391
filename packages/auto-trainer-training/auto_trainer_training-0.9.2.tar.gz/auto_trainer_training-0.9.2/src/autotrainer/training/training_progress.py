import time
from datetime import datetime, timezone
from typing import Dict, Tuple, Any, Optional, List
from typing_extensions import Self

import humps


class TrainingProgress:
    def __init__(self):
        self._timestamp: Optional[datetime] = None
        self._time_in_training: float = 0.0
        self._pellet_start_location: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self._pellet_current_location: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self._phase_attempts: int = 0
        self._session_count: int = 0
        self._pellets_presented: int = 0
        self._pellets_consumed: int = 0
        self._successful_reaches: int = 0
        self._action_context: List[Dict[str, Any]] = []
        self._user_context: Dict[str, Any] = {}

        self._current_timer: float = 0.0

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value: datetime) -> None:
        self._timestamp = value

    @property
    def time_in_training(self) -> float:
        running = 0 if self._current_timer == 0.0 else time.time() - self._current_timer
        return self._time_in_training + running

    @time_in_training.setter
    def time_in_training(self, value: float) -> None:
        self._time_in_training = value

    @property
    def session_count(self) -> int:
        return self._session_count

    @session_count.setter
    def session_count(self, value: int) -> None:
        self._session_count = value

    @property
    def pellets_presented(self) -> int:
        return self._pellets_presented

    @pellets_presented.setter
    def pellets_presented(self, value: int) -> None:
        self._pellets_presented = value

    @property
    def pellets_consumed(self) -> int:
        return self._pellets_consumed

    @pellets_consumed.setter
    def pellets_consumed(self, value: int) -> None:
        self._pellets_consumed = value

    @property
    def pellet_start_location(self) -> Tuple[float, float, float]:
        return self._pellet_start_location

    @pellet_start_location.setter
    def pellet_start_location(self, value: Tuple[float, float, float]) -> None:
        self._pellet_start_location = value

    @property
    def pellet_current_location(self) -> Tuple[float, float, float]:
        return self._pellet_current_location

    @pellet_current_location.setter
    def pellet_current_location(self, value: Tuple[float, float, float]) -> None:
        self._pellet_current_location = value

    @property
    def successful_reaches(self) -> int:
        return self._successful_reaches

    @successful_reaches.setter
    def successful_reaches(self, value: int) -> None:
        self._successful_reaches = value

    @property
    def phase_attempts(self) -> int:
        return self._phase_attempts

    @phase_attempts.setter
    def phase_attempts(self, value: int) -> None:
        self._phase_attempts = value

    @property
    def action_context(self) -> Dict[str, Any]:
        return self._action_context

    @action_context.setter
    def action_context(self, value: Dict[str, Any]) -> None:
        self._action_context = value

    @property
    def user_context(self) -> Dict[str, Any]:
        return self._user_context

    @user_context.setter
    def user_context(self, value: Dict[str, Any]) -> None:
        self._user_context = value

    def progress_resumed(self):
        if self._timestamp is None:
            self.timestamp = datetime.now(tz=timezone.utc)

        self._current_timer = time.time()

    def progress_paused(self):
        self.time_in_training += time.time() - self._current_timer

        self._current_timer = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON serialization"""
        data = {
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "time_in_training": self.time_in_training,
            "session_count": self.session_count,
            "pellets_consumed": self.pellets_consumed,
            "pellet_start_location": list(self.pellet_start_location),
            "pellet_current_location": list(self.pellet_current_location),
            "successful_reaches": self.successful_reaches,
            "phase_attempts": self.phase_attempts,
            "action_context": None,
            "user_context": self.user_context
        }
        return humps.camelize(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Self:
        """Deserialize from dictionary"""
        data = humps.decamelize(data)
        progress = cls()
        progress.timestamp = datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None
        progress.time_in_training = float(data["time_in_training"])
        progress.session_count = int(data["session_count"])
        progress.pellets_consumed = int(data["pellets_consumed"])
        progress.pellet_start_location = tuple(data["pellet_start_location"])
        progress.pellet_current_location = tuple(data["pellet_current_location"])
        progress.successful_reaches = int(data.get("successful_reaches", 0))
        progress.phase_attempts = int(data.get("phase_attempts", 0))
        progress.action_context = data.get("action_context", None)
        progress.user_context = data.get("user_context", {})

        return progress

    def status(self) -> str:
        status = ""

        def add_line(line: str) -> None:
            nonlocal status
            status += f"{line}\n"

        def add_prop(line: str) -> None:
            add_line(f"  {line}")

        add_prop(f"Start: {self.timestamp}")
        add_prop(f"Attempts: {self.phase_attempts}")
        add_prop(f"Sessions: {self.session_count}")
        add_prop(f"Pellets presented: {self.pellets_presented}")
        add_prop(f"Pellets consumed: {self.pellets_consumed}")
        add_prop(f"Reaches: {self.successful_reaches}")

        return status
