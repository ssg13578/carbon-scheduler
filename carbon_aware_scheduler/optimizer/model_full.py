import pulp
from collections import defaultdict
from typing import Dict, Tuple
from .schemas import OptimizeInput, OptimizeOutput, PlanItem

def build_and_solve_full(inp: OptimizeInput, solver_name: str = "CBC") -> OptimizeOutput:
    regions = inp.regions
    H = inp.horizon_slots
    jobs = inp.jobs
    cap = defaultdict(lambda: {"cpu": 0, "mem": 0, "gpu": 0})
    ci = defaultdict(lambda: 0.0)
    for c in inp.capacities:
        cap[(c.region, c.slot)] = {"cpu": c.cpu_cap, "mem": c.mem_gb_cap, "gpu": c.gpu_cap}
    for p in inp.carbons:
        ci[(p.region, p.slot)] = p.ci_gco2_per_kwh

    watt_cpu = float(inp.costs.get("watt_cpu", 30.0))
    lam_dev = float(inp.costs.get("lambda_plan_dev", 100.0))
    net_matrix = inp.network_costs or {}
    allow_mig = inp.migration_allow

    prob = pulp.LpProblem("caspian_full", pulp.LpMinimize)
    x: Dict[Tuple[str, str, int], pulp.LpVariable] = {}
    for j in jobs:
        for r in regions:
            if j.affinity_regions and r not in j.affinity_regions:
                continue
            for t in range(j.release_slot, j.deadline_slot - j.runtime_slots + 2):
                x[(j.job_id, r, t)] = pulp.LpVariable(f"x__{j.job_id}__{r}__{t}", cat=pulp.LpBinary)

    SLOT_HOURS = max(inp.slot_seconds / 3600.0, 0.0001)
    obj_terms = []

    for j in jobs:
        prev = inp.prev_plan.get(j.job_id)
        prev_r = prev.get("region") if prev else None
        for r in regions:
            if j.affinity_regions and r not in j.affinity_regions:
                continue
            for t in range(j.release_slot, j.deadline_slot - j.runtime_slots + 2):
                var = x[(j.job_id, r, t)]
                ci_sum = sum(ci[(r, tau)] * (j.cpu * watt_cpu * SLOT_HOURS / 1000.0) for tau in range(t, t + j.runtime_slots))
                cost = ci_sum
                if prev_r:
                    if not allow_mig and r != prev_r:
                        cost += 1e6
                    elif allow_mig and r != prev_r:
                        net_cost = net_matrix.get(prev_r, {}).get(r, 0.0)
                        cost += lam_dev + (net_cost * j.data_gb)
                obj_terms.append(var * cost)
    prob += pulp.lpSum(obj_terms)

    for j in jobs:
        starts = []
        for r in regions:
            if j.affinity_regions and r not in j.affinity_regions:
                continue
            for t in range(j.release_slot, j.deadline_slot - j.runtime_slots + 2):
                starts.append(x[(j.job_id, r, t)])
        prob += pulp.lpSum(starts) == 1

    for r in regions:
        for tau in range(H):
            c = cap.get((r, tau), {"cpu": 0, "mem": 0, "gpu": 0})
            prob += pulp.lpSum(x[(j.job_id, r, t)] * j.cpu
                               for j in jobs
                               for t in range(j.release_slot, j.deadline_slot - j.runtime_slots + 2)
                               if (t <= tau < t + j.runtime_slots) and (j.affinity_regions == [] or r in j.affinity_regions)
                               and (j.job_id, r, t) in x) <= c["cpu"]

    solver = pulp.PULP_CBC_CMD(msg=False)
    status = prob.solve(solver)
    plans, mig = [], 0
    for j in jobs:
        chosen = None
        for r in regions:
            for t in range(j.release_slot, j.deadline_slot - j.runtime_slots + 2):
                if (j.job_id, r, t) in x and pulp.value(x[(j.job_id, r, t)]) > 0.5:
                    chosen = (r, t)
                    break
            if chosen:
                break
        if not chosen:
            raise RuntimeError(f"No placement for job {j.job_id}")
        prev_r = inp.prev_plan.get(j.job_id, {}).get("region")
        if prev_r and chosen[0] != prev_r:
            mig += 1
        plans.append(PlanItem(job_id=j.job_id, region=chosen[0], start_slot=chosen[1]))
    total = pulp.value(prob.objective) or 0.0
    return OptimizeOutput(plans=plans, co2_estimate_kg=total/1000.0, solver_status=pulp.LpStatus[status], migrations=mig)
