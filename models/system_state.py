"""System state management for deadlock handling simulation."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

from .process import Process
from .resource import Resource


@dataclass
class SystemState:
    """
    Holds the complete system state: processes, resources, and matrices.
    All matrix operations use NumPy for performance.
    """

    num_processes: int = 0
    num_resources: int = 0
    processes: List[Process] = field(default_factory=list)
    resources: List[Resource] = field(default_factory=list)
    total: Optional[np.ndarray] = None       # [m] total resources
    available: Optional[np.ndarray] = None   # [m] available resources
    allocation: Optional[np.ndarray] = None  # [n x m] allocation matrix
    request: Optional[np.ndarray] = None     # [n x m] request matrix

    def initialize(self, num_processes: int, num_resources: int, total: List[int]):
        """Initialize with given dimensions and total resources."""
        self.num_processes = num_processes
        self.num_resources = num_resources
        self.total = np.array(total, dtype=np.int64)
        self.allocation = np.zeros((num_processes, num_resources), dtype=np.int64)
        self.request = np.zeros((num_processes, num_resources), dtype=np.int64)
        self.available = self.total.copy()

        self.resources = [
            Resource(rid=j, name=f"R{j}", total=total[j])
            for j in range(num_resources)
        ]
        self.processes = [
            Process(
                pid=i,
                name=f"P{i}",
                allocation=self.allocation[i],
                request=self.request[i],
                service_time=round(random.uniform(0.5, 10.0), 1),
            )
            for i in range(num_processes)
        ]

    def set_allocation(self, proc_idx: int, values: List[int]):
        """Set allocation for a process and recalculate available."""
        old = self.allocation[proc_idx].copy()
        self.allocation[proc_idx] = np.array(values, dtype=np.int64)
        self.processes[proc_idx].allocation = self.allocation[proc_idx]
        self._recalculate_available()

    def set_request(self, proc_idx: int, values: List[int]):
        """Set request for a process."""
        self.request[proc_idx] = np.array(values, dtype=np.int64)
        self.processes[proc_idx].request = self.request[proc_idx]

    def _recalculate_available(self):
        """Available = Total - sum(Allocation)."""
        self.available = self.total - np.sum(self.allocation, axis=0)

    def validate(self) -> tuple[bool, str]:
        """Validate that system state is consistent."""
        if self.total is None:
            return False, "سیستم مقداردهی نشده است."

        # Check no allocation exceeds total
        alloc_sum = np.sum(self.allocation, axis=0)
        if np.any(alloc_sum > self.total):
            over = np.where(alloc_sum > self.total)[0]
            return False, f"مجموع تخصیص منابع {over.tolist()} از کل بیشتر است."

        # Check available is non-negative
        if np.any(self.available < 0):
            return False, "منابع آزاد منفی شده (تخصیص بیش از حد)."

        # Check no single allocation exceeds total
        for i in range(self.num_processes):
            if np.any(self.allocation[i] > self.total):
                return False, f"تخصیص فرآیند P{i} از کل منابع بیشتر است."

        return True, "وضعیت سیستم معتبر است. ✅"

    def deep_copy(self) -> "SystemState":
        """Create a deep copy of this state for simulation."""
        new_state = SystemState()
        new_state.num_processes = self.num_processes
        new_state.num_resources = self.num_resources
        new_state.total = self.total.copy()
        new_state.available = self.available.copy()
        new_state.allocation = self.allocation.copy()
        new_state.request = self.request.copy()
        new_state.resources = [
            Resource(rid=r.rid, name=r.name, total=r.total)
            for r in self.resources
        ]
        new_state.processes = [
            Process(
                pid=p.pid,
                name=p.name,
                allocation=new_state.allocation[p.pid],
                request=new_state.request[p.pid],
                service_time=p.service_time,
                is_alive=p.is_alive,
            )
            for p in self.processes
        ]
        return new_state

    def generate_random(self, num_processes: int, num_resources: int,
                        max_resource: int = 10):
        """Generate a random but valid system state."""
        total = np.array(
            [random.randint(3, max_resource) for _ in range(num_resources)],
            dtype=np.int64,
        )
        self.initialize(num_processes, num_resources, total.tolist())

        # Generate random allocations that don't exceed total
        for j in range(num_resources):
            remaining = int(total[j])
            for i in range(num_processes):
                max_alloc = min(remaining, int(total[j]) // 2)
                alloc = random.randint(0, max(0, max_alloc))
                self.allocation[i][j] = alloc
                remaining -= alloc

        self._recalculate_available()

        # Generate random requests
        for i in range(num_processes):
            for j in range(num_resources):
                max_req = int(self.total[j]) - int(self.allocation[i][j])
                self.request[i][j] = random.randint(0, max(0, max_req))

        # Sync process objects
        for i in range(num_processes):
            self.processes[i].allocation = self.allocation[i]
            self.processes[i].request = self.request[i]
            self.processes[i].service_time = round(random.uniform(0.5, 10.0), 1)
