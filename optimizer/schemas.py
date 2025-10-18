from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class JobSpec(BaseModel):
    job_id: str
    cpu: int
    mem_gb: int
    gpu: int = 0
    runtime_slots: int
    release_slot: int
    deadline_slot: int
    priority: int = 0
    affinity_regions: List[str] = Field(default_factory=list)
    data_gb: float = 0.0

class ClusterCapacity(BaseModel):
    region: str
    slot: int
    cpu_cap: int
    mem_gb_cap: int
    gpu_cap: int

class CarbonPoint(BaseModel):
    region: str
    slot: int
    ci_gco2_per_kwh: float

class OptimizeInput(BaseModel):
    jobs: List[JobSpec]
    capacities: List[ClusterCapacity]
    carbons: List[CarbonPoint]
    regions: List[str]
    slot_seconds: int
    horizon_slots: int
    prev_plan: Dict[str, Dict] = {}
    costs: Dict[str, float] = {}
    network_costs: Dict[str, Dict[str, float]] = {}
    migration_allow: bool = True

class PlanItem(BaseModel):
    job_id: str
    region: str
    start_slot: int

class OptimizeOutput(BaseModel):
    plans: List[PlanItem]
    objective: str = "min_co2+dev+net"
    co2_estimate_kg: Optional[float] = None
    solver_status: str = "unknown"
    migrations: int = 0
