"""Process model for deadlock handling simulation."""

from dataclasses import dataclass, field
from typing import List
import numpy as np


@dataclass
class Process:
    """Represents a process in the system."""

    pid: int
    name: str
    allocation: np.ndarray  # Resources currently allocated
    request: np.ndarray     # Remaining resource requests
    service_time: float = 0.0  # CPU time used so far
    is_alive: bool = True

    @property
    def max_need(self) -> np.ndarray:
        """Maximum need = allocation + request."""
        return self.allocation + self.request

    @property
    def total_remaining(self) -> int:
        """Total remaining resources needed."""
        return int(np.sum(self.request))

    def release_all(self) -> np.ndarray:
        """Release all allocated resources. Returns the freed resources."""
        freed = self.allocation.copy()
        self.allocation = np.zeros_like(self.allocation)
        return freed

    def kill(self) -> np.ndarray:
        """Kill this process. Returns freed resources."""
        self.is_alive = False
        freed = self.allocation.copy()
        self.allocation = np.zeros_like(self.allocation)
        self.request = np.zeros_like(self.request)
        return freed

    def __repr__(self) -> str:
        status = "alive" if self.is_alive else "dead"
        return (
            f"Process({self.name}, {status}, "
            f"alloc={self.allocation.tolist()}, "
            f"req={self.request.tolist()}, "
            f"svc_time={self.service_time:.1f})"
        )
