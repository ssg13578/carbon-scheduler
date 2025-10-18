from typing import Dict, List
from optimizer.schemas import JobSpec, PlanItem

class InMemoryStore:
    def __init__(self):
        self.jobs: Dict[str, JobSpec] = {}
        self.plan: Dict[str, PlanItem] = {}

    def add_job(self, job: JobSpec):
        self.jobs[job.job_id] = job

    def list_jobs(self) -> List[JobSpec]:
        return list(self.jobs.values())

    def save_plan(self, items: List[PlanItem]):
        for it in items:
            self.plan[it.job_id] = it

    def get_plan(self) -> Dict[str, PlanItem]:
        return self.plan

store = InMemoryStore()
