# 논문식 스케줄러 vs 랜덤 비교
import json, yaml
from optimizer.schemas import *
from optimizer.model_full import build_and_solve_full

cfg = yaml.safe_load(open("config.yaml"))
regions = [r["name"] for r in cfg["regions"]]
H = cfg["horizon_slots"]

ci = json.load(open("sims/ci_day.json"))
jobs = [JobSpec(job_id=f"job-{i}", cpu=2, mem_gb=4, runtime_slots=2, release_slot=0, deadline_slot=H-1) for i in range(10)]
capacities = [ClusterCapacity(region=r, slot=t, cpu_cap=16, mem_gb_cap=64, gpu_cap=0) for r in regions for t in range(H)]
carbons = [CarbonPoint(region=r, slot=t, ci_gco2_per_kwh=ci[r][t]) for r in regions for t in range(H)]

opt_inp = OptimizeInput(jobs=jobs, capacities=capacities, carbons=carbons, regions=regions,
                        slot_seconds=cfg["slot_seconds"], horizon_slots=H, costs=cfg["costs"],
                        network_costs=cfg["network_costs"], migration_allow=True)

out = build_and_solve_full(opt_inp)
print("Optimal CO2 (kg):", out.co2_estimate_kg)
for p in out.plans:
    print(p)
