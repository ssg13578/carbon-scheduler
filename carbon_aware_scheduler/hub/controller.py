import yaml
from typing import List
from collectors.carbon_collector import get_carbon_forecast
from collectors.metrics_collector import get_cluster_capacity
from optimizer.schemas import OptimizeInput, JobSpec
from optimizer.model_full import build_and_solve_full
from hub.store import store

class HubController:
    def __init__(self, cfg):
        self.cfg = cfg
        self.regions = [r["name"] for r in cfg["regions"]]
        self.slot_seconds = cfg["slot_seconds"]
        self.horizon_slots = cfg["horizon_slots"]
        self.costs = cfg.get("costs", {})
        self.network_costs = cfg.get("network_costs", {})
        self.migration_policy = cfg.get("migration_policy", {"allow": True})
        self.use_prom = cfg.get("use_prometheus", False)
        self.prom_map = {r["name"]: r.get("prometheus", {}).get("url") for r in cfg["regions"]}

    def optimize(self, jobs: List[JobSpec]):
        carbons = get_carbon_forecast(self.regions, self.horizon_slots)
        caps = get_cluster_capacity(self.regions, self.horizon_slots, self.prom_map if self.use_prom else None)
        prev = {k: {"region": v.region, "start_slot": v.start_slot} for k, v in store.get_plan().items()}

        inp = OptimizeInput(
            jobs=jobs,
            capacities=caps,
            carbons=carbons,
            regions=self.regions,
            slot_seconds=self.slot_seconds,
            horizon_slots=self.horizon_slots,
            prev_plan=prev,
            costs=self.costs,
            network_costs=self.network_costs,
            migration_allow=self.migration_policy.get("allow", True)
        )
        return build_and_solve_full(inp)
