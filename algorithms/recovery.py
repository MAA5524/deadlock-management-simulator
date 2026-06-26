"""
Recovery strategies for deadlock handling.

Strategy 6: Kill all deadlocked processes
Strategy 7: Kill by least service time
Strategy 8: Kill by least remaining resources needed
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np

from models.system_state import SystemState
from .detection import detect_deadlock


def recover_kill_all(state: SystemState, lang: str = "fa") -> Tuple[SystemState, List[str]]:
    """
    Strategy 6: Detect deadlock and kill ALL deadlocked processes at once.
    """
    sim = state.deep_copy()
    assert sim.allocation is not None and sim.request is not None and sim.available is not None
    log: List[str] = []

    if lang == "fa":
        log.append("🔍 استراتژی ۶: تشخیص بن‌بست و حذف همه فرآیندهای در بن‌بست")
    else:
        log.append("🔍 Strategy 6: Deadlock Detection & Kill All Deadlocked Processes")
    log.append("")

    is_deadlocked, deadlocked, detect_log = detect_deadlock(sim, lang)
    log.extend(detect_log)
    log.append("")

    if not is_deadlocked:
        if lang == "fa":
            log.append("✅ بن‌بستی وجود ندارد. نیازی به بازیابی نیست.")
        else:
            log.append("✅ No deadlock exists. No recovery needed.")
        return sim, log

    if lang == "fa":
        log.append(f"🗑️ حذف همه فرآیندهای در بن‌بست:")
    else:
        log.append(f"🗑️ Terminating all deadlocked processes:")

    for pid in deadlocked:
        p = sim.processes[pid]
        freed = p.kill()
        sim.allocation[pid] = np.zeros(sim.num_resources, dtype=np.int64)
        sim.request[pid] = np.zeros(sim.num_resources, dtype=np.int64)
        sim.available = sim.available + freed
        if lang == "fa":
            log.append(f"   ❌ {p.name} حذف شد → منابع آزاد شده: {freed.tolist()}")
        else:
            log.append(f"   ❌ {p.name} terminated → freed resources: {freed.tolist()}")

    log.append("")
    assert sim.available is not None
    if lang == "fa":
        log.append(f"   منابع آزاد پس از حذف: {sim.available.tolist()}")
    else:
        log.append(f"   Available resources after termination: {sim.available.tolist()}")
    log.append("")

    # Verify deadlock is resolved
    is_still, _, _ = detect_deadlock(sim, lang)
    if not is_still:
        if lang == "fa":
            log.append("✅ بن‌بست رفع شد.")
        else:
            log.append("✅ Deadlock has been resolved.")
    else:
        if lang == "fa":
            log.append("⚠️ هنوز مشکل وجود دارد.")
        else:
            log.append("⚠️ System is still in deadlock.")

    return sim, log


def recover_kill_least_service_time(state: SystemState, lang: str = "fa") -> Tuple[SystemState, List[str]]:
    """
    Strategy 7: Detect deadlock, then iteratively kill the process with
    the least service time until deadlock is resolved.
    """
    sim = state.deep_copy()
    assert sim.allocation is not None and sim.request is not None and sim.available is not None
    log: List[str] = []

    if lang == "fa":
        log.append("🔍 استراتژی ۷: تشخیص بن‌بست و حذف بر اساس کمترین زمان سرویس")
    else:
        log.append("🔍 Strategy 7: Deadlock Recovery - Kill by Least Service Time")
    log.append("")

    is_deadlocked, deadlocked, detect_log = detect_deadlock(sim, lang)
    log.extend(detect_log)
    log.append("")

    if not is_deadlocked:
        if lang == "fa":
            log.append("✅ بن‌بستی وجود ندارد. نیازی به بازیابی نیست.")
        else:
            log.append("✅ No deadlock exists. No recovery needed.")
        return sim, log

    if lang == "fa":
        log.append(f"📊 زمان سرویس فرآیندهای در بن‌بست:")
        for pid in deadlocked:
            p = sim.processes[pid]
            log.append(f"   {p.name}: {p.service_time:.1f} ثانیه")
    else:
        log.append(f"📊 Service time of deadlocked processes:")
        for pid in deadlocked:
            p = sim.processes[pid]
            log.append(f"   {p.name}: {p.service_time:.1f}s")
    log.append("")

    step = 0
    while is_deadlocked:
        # Sort deadlocked by service time (ascending)
        deadlocked_procs = [
            (pid, sim.processes[pid].service_time)
            for pid in deadlocked
            if sim.processes[pid].is_alive
        ]
        deadlocked_procs.sort(key=lambda x: x[1])

        if not deadlocked_procs:
            break

        victim_pid, victim_time = deadlocked_procs[0]
        victim = sim.processes[victim_pid]
        step += 1

        freed = victim.kill()
        sim.allocation[victim_pid] = np.zeros(sim.num_resources, dtype=np.int64)
        sim.request[victim_pid] = np.zeros(sim.num_resources, dtype=np.int64)
        sim.available = sim.available + freed

        if lang == "fa":
            log.append(
                f"   مرحله {step}: ❌ {victim.name} حذف شد "
                f"(زمان سرویس: {victim_time:.1f}s) → آزاد شده: {freed.tolist()}"
            )
            assert sim.available is not None
            log.append(f"     Available = {sim.available.tolist()}")
        else:
            log.append(
                f"   Step {step}: ❌ {victim.name} terminated "
                f"(Service Time: {victim_time:.1f}s) → freed: {freed.tolist()}"
            )
            assert sim.available is not None
            log.append(f"     Available = {sim.available.tolist()}")

        # Re-check
        is_deadlocked, deadlocked, _ = detect_deadlock(sim, lang)
        if not is_deadlocked:
            log.append("")
            if lang == "fa":
                log.append(f"✅ بن‌بست پس از حذف {step} فرآیند رفع شد.")
            else:
                log.append(f"✅ Deadlock resolved after terminating {step} process(es).")
            break

    return sim, log


def recover_kill_least_resources(state: SystemState, lang: str = "fa") -> Tuple[SystemState, List[str]]:
    """
    Strategy 8: Detect deadlock, then iteratively kill the process with
    the least total remaining resource needs until deadlock is resolved.
    """
    sim = state.deep_copy()
    assert sim.allocation is not None and sim.request is not None and sim.available is not None
    log: List[str] = []

    if lang == "fa":
        log.append("🔍 استراتژی ۸: تشخیص بن‌بست و حذف بر اساس کمترین منابع مورد نیاز")
    else:
        log.append("🔍 Strategy 8: Deadlock Recovery - Kill by Least Remaining Resources")
    log.append("")

    is_deadlocked, deadlocked, detect_log = detect_deadlock(sim, lang)
    log.extend(detect_log)
    log.append("")

    if not is_deadlocked:
        if lang == "fa":
            log.append("✅ بن‌بستی وجود ندارد. نیازی به بازیابی نیست.")
        else:
            log.append("✅ No deadlock exists. No recovery needed.")
        return sim, log

    if lang == "fa":
        log.append(f"📊 منابع مورد نیاز فرآیندهای در بن‌بست:")
        for pid in deadlocked:
            p = sim.processes[pid]
            total_req = int(np.sum(sim.request[pid]))
            log.append(f"   {p.name}: مجموع = {total_req} (جزئیات: {sim.request[pid].tolist()})")
    else:
        log.append(f"📊 Remaining resource requests of deadlocked processes:")
        for pid in deadlocked:
            p = sim.processes[pid]
            total_req = int(np.sum(sim.request[pid]))
            log.append(f"   {p.name}: Total = {total_req} (Details: {sim.request[pid].tolist()})")
    log.append("")

    step = 0
    while is_deadlocked:
        # Sort deadlocked by total remaining need (ascending)
        deadlocked_procs = [
            (pid, int(np.sum(sim.request[pid])))
            for pid in deadlocked
            if sim.processes[pid].is_alive
        ]
        deadlocked_procs.sort(key=lambda x: x[1])

        if not deadlocked_procs:
            break

        victim_pid, victim_need = deadlocked_procs[0]
        victim = sim.processes[victim_pid]
        step += 1

        freed = victim.kill()
        sim.allocation[victim_pid] = np.zeros(sim.num_resources, dtype=np.int64)
        sim.request[victim_pid] = np.zeros(sim.num_resources, dtype=np.int64)
        sim.available = sim.available + freed

        if lang == "fa":
            log.append(
                f"   مرحله {step}: ❌ {victim.name} حذف شد "
                f"(منابع مورد نیاز: {victim_need}) → آزاد شده: {freed.tolist()}"
            )
            assert sim.available is not None
            log.append(f"     Available = {sim.available.tolist()}")
        else:
            log.append(
                f"   Step {step}: ❌ {victim.name} terminated "
                f"(Required Resources: {victim_need}) → freed: {freed.tolist()}"
            )
            assert sim.available is not None
            log.append(f"     Available = {sim.available.tolist()}")

        # Re-check
        is_deadlocked, deadlocked, _ = detect_deadlock(sim, lang)
        if not is_deadlocked:
            log.append("")
            if lang == "fa":
                log.append(f"✅ بن‌بست پس از حذف {step} فرآیند رفع شد.")
            else:
                log.append(f"✅ Deadlock resolved after terminating {step} process(es).")
            break

    return sim, log
