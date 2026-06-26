"""
Avoidance strategies for deadlock handling.

Strategy 4: Banker's Algorithm (Resource Allocation Denial)
Strategy 5: Process Initiation Denial
"""

from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np

from models.system_state import SystemState


def _find_safe_sequence(
    allocation: np.ndarray,
    request: np.ndarray,
    available: np.ndarray,
    n: int,
    process_names: List[str],
    alive: List[bool],
    lang: str = "fa",
) -> Tuple[bool, List[int], List[str]]:
    """
    Core Banker's safety algorithm.

    Returns:
        (is_safe, safe_sequence_pids, step_log)
    """
    log: List[str] = []
    work = available.copy()
    finish = [False] * n
    safe_seq: List[int] = []

    # Mark dead processes as finished
    for i in range(n):
        if not alive[i]:
            finish[i] = True

    if lang == "fa":
        log.append(f"   Work اولیه = {work.tolist()}")
    else:
        log.append(f"   Initial Work = {work.tolist()}")

    iteration = 0
    changed = True
    while changed:
        changed = False
        for i in range(n):
            if finish[i]:
                continue
            if np.all(request[i] <= work):
                iteration += 1
                if lang == "fa":
                    log.append(
                        f"   مرحله {iteration}: {process_names[i]} انتخاب شد "
                        f"(Request={request[i].tolist()} <= Work={work.tolist()})"
                    )
                else:
                    log.append(
                        f"   Step {iteration}: {process_names[i]} chosen "
                        f"(Request={request[i].tolist()} <= Work={work.tolist()})"
                    )
                work = work + allocation[i]
                finish[i] = True
                safe_seq.append(i)
                if lang == "fa":
                    log.append(f"     → Work = Work + Alloc = {work.tolist()}")
                else:
                    log.append(f"     → Work = Work + Alloc = {work.tolist()}")
                changed = True

    is_safe = all(finish)
    return is_safe, safe_seq, log


def avoid_by_resource_allocation(state: SystemState, lang: str = "fa") -> Tuple[SystemState, List[str]]:
    """
    Strategy 4: Banker's Algorithm — Resource Allocation Denial.

    Before any allocation, check if system remains in safe state.
    Shows the safe sequence if system is safe.
    """
    sim = state.deep_copy()
    log: List[str] = []

    if lang == "fa":
        log.append("🛡️ استراتژی ۴: اجتناب از بن‌بست — الگوریتم بانکر")
        log.append("   قانون: قبل از هر تخصیص، بررسی حالت امن (Safe State)")
    else:
        log.append("🛡️ Strategy 4: Deadlock Avoidance — Banker's Algorithm")
        log.append("   Rule: Before any allocation, verify the Safe State.")
    log.append("")

    names = [p.name for p in sim.processes]
    alive = [p.is_alive for p in sim.processes]

    assert sim.allocation is not None and sim.request is not None and sim.available is not None

    # Check current state safety
    is_safe, safe_seq, safety_log = _find_safe_sequence(
        sim.allocation, sim.request, sim.available,
        sim.num_processes, names, alive, lang
    )
    log.extend(safety_log)
    log.append("")

    if is_safe:
        seq_names = [names[i] for i in safe_seq]
        if lang == "fa":
            log.append(f"✅ سیستم در حالت امن است!")
            log.append(f"   ترتیب امن: {' → '.join(seq_names)}")
            log.append("")
            log.append("   توضیح: هر تخصیص جدید فقط در صورتی انجام می‌شود")
            log.append("   که سیستم پس از تخصیص همچنان در حالت امن باقی بماند.")
        else:
            log.append(f"✅ System is in a SAFE state!")
            log.append(f"   Safe Sequence: {' → '.join(seq_names)}")
            log.append("")
            log.append("   Description: New allocation requests are only granted")
            log.append("   if the resulting state remains safe.")
    else:
        unfinished = [names[i] for i in range(sim.num_processes)
                      if i not in safe_seq and alive[i]]
        if lang == "fa":
            log.append(f"🔴 سیستم در حالت ناامن است!")
            log.append(f"   فرآیندهای بلوکه‌شده: {', '.join(unfinished)}")
            log.append("")
            log.append("   ⚠️ تخصیص منابع جدید رد می‌شود تا بن‌بست اتفاق نیفتد.")
        else:
            log.append(f"🔴 System is in an UNSAFE state!")
            log.append(f"   Blocked processes: {', '.join(unfinished)}")
            log.append("")
            log.append("   ⚠️ New resource allocation is denied to avoid deadlock.")

        if safe_seq:
            partial = [names[i] for i in safe_seq]
            if lang == "fa":
                log.append(f"   ترتیب امن جزئی: {' → '.join(partial)}")
            else:
                log.append(f"   Partial Safe Sequence: {' → '.join(partial)}")

    return sim, log


def avoid_by_process_initiation(
    state: SystemState,
    new_process_max: Optional[List[int]] = None,
    lang: str = "fa",
) -> Tuple[SystemState, List[str]]:
    """
    Strategy 5: Process Initiation Denial.

    A new process starts only if total max claims (including new) <= total resources.
    If no new process is specified, checks current processes.
    """
    sim = state.deep_copy()
    log: List[str] = []

    if lang == "fa":
        log.append("🛡️ استراتژی ۵: اجتناب از بن‌بست — جلوگیری از شروع فرآیند جدید")
        log.append("   قانون: فرآیند جدید فقط اگر مجموع حداکثر نیاز همه فرآیندها")
        log.append("   (شامل جدید) از کل منابع تجاوز نکند.")
    else:
        log.append("🛡️ Strategy 5: Deadlock Avoidance — Process Initiation Denial")
        log.append("   Rule: A new process starts only if total max claims (including new)")
        log.append("   do not exceed total system resources.")
    log.append("")

    assert sim.allocation is not None and sim.request is not None and sim.total is not None

    # Calculate sum of max needs for current processes
    max_matrix = sim.allocation + sim.request  # Max = Allocation + Request
    sum_max = np.sum(max_matrix, axis=0)

    if lang == "fa":
        log.append(f"   کل منابع سیستم:      {sim.total.tolist()}")
        log.append(f"   مجموع Max فرآیندها:  {sum_max.tolist()}")
    else:
        log.append(f"   Total system resources: {sim.total.tolist()}")
        log.append(f"   Sum of Max Claims:      {sum_max.tolist()}")
    log.append("")

    # Show per-resource comparison
    for j in range(sim.num_resources):
        status = "✅" if sum_max[j] <= sim.total[j] else "❌"
        log.append(
            f"   R{j}: "
            f"{t_res(lang, 'Sum Max')} = {sum_max[j]} "
            f"{'<=' if sum_max[j] <= sim.total[j] else '>'} "
            f"{t_res(lang, 'Total')} = {sim.total[j]} {status}"
        )

    log.append("")

    current_ok = np.all(sum_max <= sim.total)
    if current_ok:
        if lang == "fa":
            log.append("🟢 فرآیندهای فعلی: مجموع نیازها از کل منابع تجاوز نمی‌کند.")
        else:
            log.append("🟢 Current processes: Sum of max claims is within total resources.")
    else:
        over = np.where(sum_max > sim.total)[0]
        if lang == "fa":
            log.append(
                f"🔴 فرآیندهای فعلی: مجموع نیازها از کل منابع "
                f"{[f'R{j}' for j in over]} تجاوز کرده!"
            )
            log.append("   ⚠️ حداقل یک فرآیند باید متوقف شود.")
        else:
            log.append(
                f"🔴 Current processes: Sum of max claims exceeds total resources for "
                f"{[f'R{j}' for j in over]}!"
            )
            log.append("   ⚠️ At least one process must be terminated.")

    if new_process_max is not None:
        new_max = np.array(new_process_max, dtype=np.int64)
        new_sum = sum_max + new_max

        log.append("")
        if lang == "fa":
            log.append(f"   --- بررسی فرآیند جدید ---")
            log.append(f"   Max فرآیند جدید: {new_max.tolist()}")
            log.append(f"   مجموع جدید Max: {new_sum.tolist()}")
        else:
            log.append(f"   --- Checking New Process ---")
            log.append(f"   Max need of new process: {new_max.tolist()}")
            log.append(f"   New sum of max claims:   {new_sum.tolist()}")

        can_start = np.all(new_sum <= sim.total)
        if can_start:
            if lang == "fa":
                log.append(f"   ✅ فرآیند جدید مجاز به شروع است.")
            else:
                log.append(f"   ✅ New process is allowed to start.")
        else:
            over = np.where(new_sum > sim.total)[0]
            if lang == "fa":
                log.append(
                    f"   ❌ فرآیند جدید مجاز نیست! "
                    f"(تجاوز در منابع {[f'R{j}' for j in over]})"
                )
            else:
                log.append(
                    f"   ❌ New process is denied! "
                    f"(Exceeds resources {[f'R{j}' for j in over]})"
                )
    else:
        log.append("")
        if lang == "fa":
            log.append("   ℹ️ فرآیند جدیدی برای بررسی مشخص نشده.")
            log.append("   هر فرآیند جدید باید قبل از شروع بررسی شود.")
        else:
            log.append("   ℹ️ No new process specified for verification.")
            log.append("   New processes must be verified before starting.")

    return sim, log


def t_res(lang: str, key: str) -> str:
    """Quick translator helper inside algorithms."""
    if lang == "fa":
        if key == "Sum Max": return "مجموع نیاز"
        if key == "Total": return "کل"
    return key
