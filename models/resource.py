"""Resource model for deadlock handling simulation."""

from dataclasses import dataclass


@dataclass
class Resource:
    """Represents a resource type in the system."""

    rid: int
    name: str
    total: int  # Total instances of this resource

    def __repr__(self) -> str:
        return f"Resource({self.name}, total={self.total})"
