import argparse, yaml
from optimizer.schemas import OptimizeInput, JobSpec, ClusterCapacity, CarbonPoint
from optimizer.model_full import build_and_solve_full

def synthetic_input(cfg):
    regions = [r["name"] for r in cfg["regions"]]
    H = cfg["horizon_slots"]
    jobs = [
        JobSpec(job_id=f"job-{i}", cpu=(i % 3) + 1, mem_gb=2, runtime_slots=2,
                release_slot=0, deadline_slot=min(H-1, 4+i), data_gb=1.5)
        for i in range(3)
    ]
    capacities = [ClusterCapacity(region=r, slot=t, cpu_cap=6, mem_gb_cap=24, gpu_cap=0)
                  for r in regions for t in range(H)]
    carbons = []
    for r in regions:
        base = 400 if r == "KR" else (300 if r == "JP" else 350)
        for t in range(H):
            carbons.append(CarbonPoint(region=r, slot=t, ci_gco2_per_kwh=base + (t%4)*20))
    return OptimizeInput(
        jobs=jobs,
        capacities=capacities,
        carbons=carbons,
        regions=regions,
        slot_seconds=cfg["slot_seconds"],
        horizon_slots=H,
        costs=cfg["costs"],
        network_costs=cfg["network_costs"],
        migration_allow=cfg["migration_policy"]["allow"]
    )

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()

    cfg = yaml.safe_load(open(args.config))
    inp = synthetic_input(cfg)
    out = build_and_solve_full(inp)

    print("\n===== CASPIAN MODEL TEST RUN =====")
    print("Solver Status:", out.solver_status)
    print("Total CO₂ (kg):", round(out.co2_estimate_kg, 3))
    print("Migrations:", out.migrations)
    print("Plan:")
    for p in out.plans:
        print(f" - {p.job_id}: {p.region} @ slot {p.start_slot}")
    print("==================================\n")
