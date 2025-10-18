from fastapi import FastAPI
from pydantic import BaseModel
import yaml
from fastapi.responses import Response
from prometheus_client import CollectorRegistry, Gauge, Counter, generate_latest, CONTENT_TYPE_LATEST

from hub.store import store
from hub.controller import HubController

app = FastAPI(title="Carbon-Aware Scheduler Hub")
CFG = yaml.safe_load(open("config.yaml"))
HUB = HubController(CFG)

REG = CollectorRegistry()
CO2_G = Gauge('plan_co2_estimate_kg', 'Planned CO2 (kg)', registry=REG)
SOLVER_OK = Gauge('solver_optimal', '1 if optimal', registry=REG)
MIG_C = Counter('migration_event_total', 'Number of migrations', registry=REG)

class SubmitReq(BaseModel):
    job_id: str
    cpu: int = 1
    mem_gb: int = 2
    gpu: int = 0
    runtime_slots: int = 2
    release_slot: int = 0
    deadline_slot: int = 8
    priority: int = 0
    affinity_regions: list[str] = []
    data_gb: float = 0.0

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/submit")
async def submit(req: SubmitReq):
    from optimizer.schemas import JobSpec
    job = JobSpec(**req.model_dump())
    store.add_job(job)
    return {"accepted": True, "job": job.model_dump()}

@app.post("/optimize")
async def optimize_now():
    jobs = store.list_jobs()
    out = HUB.optimize(jobs)
    CO2_G.set(out.co2_estimate_kg or 0)
    SOLVER_OK.set(1.0 if out.solver_status.lower() == "optimal" else 0.0)
    if out.migrations:
        MIG_C.inc(out.migrations)
    store.save_plan(out.plans)
    return out.model_dump()

@app.get("/plan")
async def plan():
    return {k: v.model_dump() for k, v in store.get_plan().items()}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(REG), media_type=CONTENT_TYPE_LATEST)
