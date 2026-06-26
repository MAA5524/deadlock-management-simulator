"""
Prevention strategies for deadlock handling.

Strategy 1: Remove Hold & Wait
Strategy 2: Remove Mutual Exclusion
Strategy 3: Remove Circular Wait
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np

from models.system_state import SystemState


def prevent_hold_and_wait(state: SystemState, lang: str = "fa") -> Tuple[SystemState, List[str]]:
    """
    Strategy 1: Prevent deadlock by removing hold-and-wait condition.

    Each process must request ALL resources before starting.
    If all resources are not available, the process releases everything and waits.
    """
    sim = state.deep_copy()
    
    assert sim.allocation is not None and sim.request is not None and sim.available is not None
    
    log: List[str] = []

    if lang == "fa":
        log.append("🛡️ استراتژی ۱: حذف شرط گرفتن و منتظر بودن (Hold & Wait)")
        log.append("   قانون: هر فرآیند باید همه منابعش را یکجا درخواست کند.")
    else:
        log.append("🛡️ Strategy 1: Remove Hold & Wait")
        log.append("   Rule: Each process must request all resources upfront.")
    log.append("")

    waiting = []
    running = []

    for i in range(sim.num_processes):
        p = sim.processes[i]
        if not p.is_alive:
            continue

        total_need = sim.allocation[i] + sim.request[i]
        # Can we fulfill all needs if process releases its current resources?
        potential_available = sim.available + sim.allocation[i]

        if lang == "fa":
            log.append(f"   بررسی {p.name}:")
            log.append(f"     نیاز کل: {total_need.tolist()}")
            log.append(f"     منابع در دسترس (پس از آزادسازی): {potential_available.tolist()}")
        else:
            log.append(f"   Checking {p.name}:")
            log.append(f"     Total Need: {total_need.tolist()}")
            log.append(f"     Available resources (after release): {potential_available.tolist()}")

        if np.all(total_need <= potential_available):
            if lang == "fa":
                log.append(f"     ✅ {p.name} می‌تواند همه منابعش را یکجا بگیرد → ادامه اجرا")
            else:
                log.append(f"     ✅ {p.name} can acquire all resources at once → continues execution")
            running.append(p.name)
        else:
            # Release all resources
            freed = sim.allocation[i].copy()
            sim.allocation[i] = np.zeros(sim.num_resources, dtype=np.int64)
            sim.request[i] = total_need.copy()
            sim.available = sim.available + freed
            if lang == "fa":
                log.append(
                    f"     ⏳ {p.name} نمی‌تواند همه منابعش را بگیرد "
                    f"→ منابع آزاد شد: {freed.tolist()} → منتظر"
                )
            else:
                log.append(
                    f"     ⏳ {p.name} cannot acquire all resources "
                    f"→ released: {freed.tolist()} → waiting"
                )
            waiting.append(p.name)

    log.append("")
    if lang == "fa":
        if running:
            log.append(f"🟢 فرآیندهای در حال اجرا: {', '.join(running)}")
        if waiting:
            log.append(f"🟡 فرآیندهای منتظر: {', '.join(waiting)}")
        assert sim.available is not None
        log.append(f"   منابع آزاد پس از اعمال: {sim.available.tolist()}")
    else:
        if running:
            log.append(f"🟢 Running processes: {', '.join(running)}")
        if waiting:
            log.append(f"🟡 Waiting processes: {', '.join(waiting)}")
        assert sim.available is not None
        log.append(f"   Available resources after apply: {sim.available.tolist()}")

    log.append("")
    if not waiting:
        if lang == "fa":
            log.append("✅ بن‌بست غیرممکن: همه فرآیندها می‌توانند اجرا شوند.")
        else:
            log.append("✅ Deadlock impossible: all processes can execute.")
    else:
        if lang == "fa":
            log.append("✅ بن‌بست غیرممکن: فرآیندهای منتظر هیچ منبعی را نگه نداشته‌اند.")
        else:
            log.append("✅ Deadlock impossible: waiting processes hold zero resources.")

    # Sync process objects
    for i in range(sim.num_processes):
        sim.processes[i].allocation = sim.allocation[i]
        sim.processes[i].request = sim.request[i]

    return sim, log


def prevent_mutual_exclusion(state: SystemState, lang: str = "fa") -> Tuple[SystemState, List[str]]:
    """
    Strategy 2: Prevent deadlock by removing mutual exclusion.

    Make resources shareable — multiple processes can use the same resource.
    """
    sim = state.deep_copy()
    
    assert sim.allocation is not None and sim.request is not None
    
    log: List[str] = []

    if lang == "fa":
        log.append("🛡️ استراتژی ۲: حذف شرط انحصار منابع (Mutual Exclusion)")
        log.append("   قانون: منابع قابل اشتراک‌گذاری هستند و چند فرآیند می‌توانند")
        log.append("   همزمان از یک منبع استفاده کنند.")
        log.append("")
        log.append("   ⚠️ توجه: این روش فقط برای منابع فقط‌خواندنی عملی است.")
    else:
        log.append("🛡️ Strategy 2: Remove Mutual Exclusion")
        log.append("   Rule: Resources are shareable; multiple processes can use them concurrently.")
        log.append("")
        log.append("   ⚠️ Note: This is only practical for read-only resources.")
    log.append("")

    for i in range(sim.num_processes):
        p = sim.processes[i]
        if not p.is_alive:
            continue

        if np.any(sim.request[i] > 0):
            granted = sim.request[i].copy()
            sim.allocation[i] = sim.allocation[i] + granted
            sim.request[i] = np.zeros(sim.num_resources, dtype=np.int64)
            if lang == "fa":
                log.append(
                    f"   ✅ {p.name}: منابع درخواستی {granted.tolist()} "
                    f"بدون بررسی موجودی تخصیص داده شد (منبع مشترک)"
                )
                log.append(f"      تخصیص جدید: {sim.allocation[i].tolist()}")
            else:
                log.append(
                    f"   ✅ {p.name}: requested resources {granted.tolist()} "
                    f"allocated directly (shared resource)"
                )
                log.append(f"      New allocation: {sim.allocation[i].tolist()}")
        else:
            if lang == "fa":
                log.append(f"   ℹ️ {p.name}: درخواستی ندارد.")
            else:
                log.append(f"   ℹ️ {p.name}: Has no pending requests.")

    log.append("")
    if lang == "fa":
        log.append("✅ بن‌بست غیرممکن: هیچ فرآیندی منتظر منبع نیست.")
        log.append("⚠️ هشدار: ممکن است ناسازگاری داده رخ دهد (Data Inconsistency).")
    else:
        log.append("✅ Deadlock impossible: no process is waiting for resources.")
        log.append("⚠️ Warning: This may lead to Data Inconsistency.")

    # Sync
    for i in range(sim.num_processes):
        sim.processes[i].allocation = sim.allocation[i]
        sim.processes[i].request = sim.request[i]

    return sim, log


def prevent_circular_wait(state: SystemState, lang: str = "fa") -> Tuple[SystemState, List[str]]:
    """
    Strategy 3: Prevent deadlock by removing circular wait.

    Impose a total ordering on resources. Each process can only request
    resources with a higher index than its highest currently-held resource.
    """
    sim = state.deep_copy()
    
    assert sim.allocation is not None and sim.request is not None and sim.available is not None
    
    log: List[str] = []

    if lang == "fa":
        log.append("🛡️ استراتژی ۳: حذف شرط انتظار چرخشی (Circular Wait)")
        log.append("   قانون: ترتیب خطی روی منابع: R0 < R1 < R2 < ...")
        log.append("   هر فرآیند فقط منابع با شماره بالاتر از بالاترین منبع فعلی را درخواست کند.")
    else:
        log.append("🛡️ Strategy 3: Remove Circular Wait")
        log.append("   Rule: Linear ordering on resources: R0 < R1 < R2 < ...")
        log.append("   Processes can only request resources indexed higher than their highest held resource.")
    log.append("")

    violations = []
    valid_requests = []

    for i in range(sim.num_processes):
        p = sim.processes[i]
        if not p.is_alive:
            continue

        # Find highest held resource index
        held_indices = np.where(sim.allocation[i] > 0)[0]
        highest_held = int(held_indices[-1]) if len(held_indices) > 0 else -1

        if lang == "fa":
            log.append(f"   بررسی {p.name}:")
            if highest_held >= 0:
                log.append(f"     بالاترین منبع نگه‌داشته: R{highest_held}")
            else:
                log.append(f"     هیچ منبعی نگه نداشته")
        else:
            log.append(f"   Checking {p.name}:")
            if highest_held >= 0:
                log.append(f"     Highest held resource: R{highest_held}")
            else:
                log.append(f"     Holds no resources")

        # Check each request
        request_indices = np.where(sim.request[i] > 0)[0]
        proc_violations = []
        proc_valid = []

        for j in request_indices:
            if j > highest_held:
                proc_valid.append(j)
                if lang == "fa":
                    log.append(f"     ✅ درخواست R{j}: مجاز (R{j} > R{highest_held})")
                else:
                    log.append(f"     ✅ Request R{j}: Allowed (R{j} > R{highest_held})")
            else:
                proc_violations.append(j)
                if lang == "fa":
                    log.append(f"     ❌ درخواست R{j}: غیرمجاز! (R{j} <= R{highest_held})")
                else:
                    log.append(f"     ❌ Request R{j}: Violated! (R{j} <= R{highest_held})")

        if proc_violations:
            violations.append((p.name, proc_violations))
            # Process must release resources >= violating index and re-request
            min_violation = min(proc_violations)
            released_indices = [j for j in held_indices if j >= min_violation]
            released = np.zeros(sim.num_resources, dtype=np.int64)
            for j in released_indices:
                released[j] = sim.allocation[i][j]
                sim.request[i][j] += sim.allocation[i][j]
                sim.allocation[i][j] = 0
            sim.available = sim.available + released
            if lang == "fa":
                log.append(
                    f"     → {p.name} باید منابع {[f'R{j}' for j in released_indices]} "
                    f"را آزاد و دوباره درخواست کند"
                )
            else:
                log.append(
                    f"     → {p.name} must release {[f'R{j}' for j in released_indices]} "
                    f"and re-request later"
                )
        elif len(request_indices) > 0:
            valid_requests.append(p.name)

    log.append("")
    if violations:
        names = [v[0] for v in violations]
        if lang == "fa":
            log.append(f"🟡 فرآیندهایی با نقض ترتیب: {', '.join(names)}")
            log.append("   منابع نقض‌کننده آزاد شدند و به صف درخواست بازگشتند.")
        else:
            log.append(f"🟡 Processes with ordering violation: {', '.join(names)}")
            log.append("   Violating resources released and put back to request queue.")
    else:
        if lang == "fa":
            log.append("🟢 هیچ نقض ترتیبی وجود ندارد.")
        else:
            log.append("🟢 No ordering violations detected.")

    if lang == "fa":
        log.append("✅ بن‌بست غیرممکن: انتظار چرخشی حذف شد.")
    else:
        log.append("✅ Deadlock impossible: circular wait removed.")

    # Sync
    for i in range(sim.num_processes):
        sim.processes[i].allocation = sim.allocation[i]
        sim.processes[i].request = sim.request[i]

    return sim, log
