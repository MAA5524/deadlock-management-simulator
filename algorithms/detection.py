"""
Deadlock detection using matrix reduction algorithm.

Algorithm:
1. W = Available.copy()
2. Mark processes with zero allocation
3. Find unmarked process Pi where Request[i] <= W
4. If found: W += Allocation[i], mark Pi
5. Repeat until no more processes can be marked
6. Unmarked processes are deadlocked
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np

from models.system_state import SystemState


def detect_deadlock(state: SystemState, lang: str = "fa") -> Tuple[bool, List[int], List[str], List[List[Tuple[str, int, int]]]]:
    """
    Detect deadlock using matrix reduction algorithm.

    Returns:
        (is_deadlocked, deadlocked_pids, step_log)
    """
    log: List[str] = []
    n = state.num_processes
    assert state.available is not None and state.allocation is not None and state.request is not None
    work = state.available.copy()
    marked = [False] * n

    if lang == "fa":
        log.append(f"🔍 شروع تشخیص بن‌بست...")
        log.append(f"   Work اولیه = {work.tolist()}")
    else:
        log.append(f"🔍 Starting Deadlock Detection...")
        log.append(f"   Initial Work = {work.tolist()}")

    # Step 1: Mark processes with zero allocation
    for i in range(n):
        if not state.processes[i].is_alive:
            marked[i] = True
            continue
        if np.all(state.allocation[i] == 0):
            marked[i] = True
            if lang == "fa":
                log.append(f"   ✓ {state.processes[i].name} علامت‌گذاری شد (تخصیص صفر)")
            else:
                log.append(f"   ✓ {state.processes[i].name} marked (zero allocation)")

    # Step 2: Iterative reduction
    changed = True
    iteration = 0
    while changed:
        changed = False
        iteration += 1
        for i in range(n):
            if marked[i]:
                continue
            if np.all(state.request[i] <= work):
                work = work + state.allocation[i]
                marked[i] = True
                changed = True
                if lang == "fa":
                    log.append(
                        f"   مرحله {iteration}: {state.processes[i].name} قابل اجراست "
                        f"(Request={state.request[i].tolist()} <= Work)"
                    )
                    log.append(f"   → Work = {work.tolist()}")
                else:
                    log.append(
                        f"   Step {iteration}: {state.processes[i].name} is runnable "
                        f"(Request={state.request[i].tolist()} <= Work)"
                    )
                    log.append(f"   → Work = {work.tolist()}")

    # Step 3: Find deadlocked processes
    deadlocked = [i for i in range(n) if not marked[i] and state.processes[i].is_alive]

    cycles = find_cycles(state)

    if deadlocked:
        names = [state.processes[i].name for i in deadlocked]
        if lang == "fa":
            log.append(f"🔴 بن‌بست تشخیص داده شد!")
            log.append(f"   فرآیندهای در بن‌بست: {', '.join(names)}")
        else:
            log.append(f"🔴 Deadlock Detected!")
            log.append(f"   Deadlocked processes: {', '.join(names)}")
    else:
        if lang == "fa":
            log.append(f"🟢 بن‌بستی وجود ندارد. سیستم سالم است.")
        else:
            log.append(f"🟢 No deadlock detected. System is safe.")

    return len(deadlocked) > 0, deadlocked, log, cycles


def find_cycles(state: SystemState) -> List[List[Tuple[str, int, int]]]:
    """
    Finds cycles in the Resource Allocation Graph (Wait-For Graph).
    Returns a list of cycles, where each cycle is a list of edges.
    Edge format: ('req', p_idx, r_idx) or ('alloc', p_idx, r_idx)
    """
    assert state.allocation is not None and state.request is not None
    n = state.num_processes
    m = state.num_resources
    
    adj = {i: [] for i in range(n + m)}
    
    for i in range(n):
        if not state.processes[i].is_alive:
            continue
        for j in range(m):
            if state.request[i][j] > 0:
                adj[i].append(('req', j + n, i, j))
            if state.allocation[i][j] > 0:
                adj[j + n].append(('alloc', i, i, j))
                
    cycles = []
    visited = [0] * (n + m)
    parent_edge = {}
    
    def dfs(u):
        visited[u] = 1
        for edge_type, v, p_idx, r_idx in adj[u]:
            if visited[v] == 0:
                parent_edge[v] = (u, edge_type, p_idx, r_idx)
                dfs(v)
            elif visited[v] == 1:
                cycle = []
                cycle.append((edge_type, p_idx, r_idx))
                curr = u
                while curr != v:
                    pu, p_edge, pp, pr = parent_edge[curr]
                    cycle.append((p_edge, pp, pr))
                    curr = pu
                cycles.append(cycle[::-1])
        visited[u] = 2

    for i in range(n + m):
        if visited[i] == 0:
            dfs(i)
            
    return cycles
