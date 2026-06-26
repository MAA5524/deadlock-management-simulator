"""Dynamic step-by-step simulation engine."""

from __future__ import annotations

from typing import List, Tuple, Callable
import numpy as np

from models.system_state import SystemState
from algorithms.avoidance import _find_safe_sequence


class SimulationEngine:
    """
    Runs a tick-based simulation of processes executing, requesting resources,
    and releasing them, governed by Banker's Algorithm avoidance.
    """

    def __init__(self, initial_state: SystemState):
        self.state = initial_state.deep_copy()
        self.ticks = 0
        self.is_finished = False

    def step(self, lang: str = "fa") -> Tuple[bool, List[str]]:
        """
        Advances the simulation by one tick.
        Returns:
            (is_running, logs)
        """
        if self.is_finished:
            return False, []

        log: List[str] = []
        self.ticks += 1
        
        if lang == "fa":
            log.append(f"⏱️ --- تیک شبیه‌سازی: {self.ticks} ---")
        else:
            log.append(f"⏱️ --- Simulation Tick: {self.ticks} ---")

        assert self.state.allocation is not None
        assert self.state.request is not None
        assert self.state.available is not None

        n = self.state.num_processes
        process_names = [p.name for p in self.state.processes]
        
        active_count = 0
        progress_made = False

        for i in range(n):
            p = self.state.processes[i]
            if not p.is_alive:
                continue

            active_count += 1

            # 1. If process has pending requests, try to fulfill them
            if np.any(self.state.request[i] > 0):
                req = self.state.request[i].copy()
                
                # Check if enough available
                if np.all(req <= self.state.available):
                    # Pretend to allocate and check safety
                    temp_avail = self.state.available - req
                    temp_alloc = self.state.allocation.copy()
                    temp_alloc[i] = temp_alloc[i] + req
                    temp_req = self.state.request.copy()
                    temp_req[i] = 0

                    alive_flags = [proc.is_alive for proc in self.state.processes]
                    
                    is_safe, _, _ = _find_safe_sequence(
                        temp_alloc, temp_req, temp_avail, n, process_names, alive_flags, lang
                    )

                    if is_safe:
                        # Grant request
                        self.state.available = temp_avail
                        self.state.allocation = temp_alloc
                        self.state.request = temp_req
                        p.allocation = temp_alloc[i]
                        p.request = temp_req[i]
                        progress_made = True
                        if lang == "fa":
                            log.append(f"🟢 تخصیص امن: {p.name} منابع {req.tolist()} را دریافت کرد.")
                        else:
                            log.append(f"🟢 Safe Allocation: {p.name} granted {req.tolist()}.")
                    else:
                        if lang == "fa":
                            log.append(f"🟡 بلوکه شده: تخصیص {req.tolist()} به {p.name} ناامن است.")
                        else:
                            log.append(f"🟡 Blocked: Allocating {req.tolist()} to {p.name} is unsafe.")
                else:
                    assert self.state.available is not None
                    if lang == "fa":
                        log.append(f"🔴 منتظر: {p.name} منابع {req.tolist()} می‌خواهد ولی فقط {self.state.available.tolist()} آزاد است.")
                    else:
                        log.append(f"🔴 Waiting: {p.name} wants {req.tolist()} but only {self.state.available.tolist()} available.")
            else:
                # 2. Process has all it needs, decrement service time
                p.service_time -= 1.0
                progress_made = True
                
                if p.service_time <= 0:
                    # Finish and release
                    p.is_alive = False
                    p.service_time = 0
                    released = self.state.allocation[i].copy()
                    self.state.available = self.state.available + released
                    self.state.allocation[i] = 0
                    p.allocation = self.state.allocation[i]
                    
                    if lang == "fa":
                        log.append(f"✅ پایان یافت: {p.name} تمام شد و منابع {released.tolist()} را آزاد کرد.")
                    else:
                        log.append(f"✅ Finished: {p.name} completed and released {released.tolist()}.")
                else:
                    if lang == "fa":
                        log.append(f"⚙️ در حال اجرا: {p.name} مشغول کار است (زمان باقی‌مانده: {p.service_time}).")
                    else:
                        log.append(f"⚙️ Running: {p.name} is executing (remaining: {p.service_time}).")

        # End of tick
        if active_count == 0:
            self.is_finished = True
            if lang == "fa":
                log.append("🎉 تمامی فرآیندها با موفقیت پایان یافتند!")
            else:
                log.append("🎉 All processes completed successfully!")
            return False, log
            
        if not progress_made:
            # Deadlock state reached where no one can progress
            self.is_finished = True
            if lang == "fa":
                log.append("💀 بن‌بست سیستم! هیچ فرآیندی نمی‌تواند پیشرفت کند.")
            else:
                log.append("💀 System Deadlock! No process can make progress.")
            return False, log

        return True, log
