import time, yaml
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dispatcher.mcad_dispatcher import MCADDispatcher
from hub.store import store
from hub.controller import HubController
from hub.app import MIG_C

def run_loop(config_path: str = "config.yaml"):
    cfg = yaml.safe_load(open(config_path))
    hub = HubController(cfg)
    disp = MCADDispatcher(namespace=cfg["mcad"]["namespace"], dry_run=cfg["kubectl"]["dry_run"])
    slot_s = cfg["slot_seconds"]

    while True:
        jobs = store.list_jobs()
        if not jobs:
            time.sleep(5)
            continue
        out = hub.optimize(jobs)
        print(f"status={out.solver_status} co2={out.co2_estimate_kg:.3f}kg migrations={out.migrations}")
        if out.migrations:
            MIG_C.inc(out.migrations)
        for item in out.plans:
            if item.start_slot == 0:
                kubecontext = next(r["kubecontext"] for r in cfg["regions"] if r["name"] == item.region)
                job = store.jobs[item.job_id]
                disp.dispatch_appwrapper(kubecontext, item.job_id, item.region, cfg["job_defaults"]["image"], job.cpu, job.mem_gb)
        store.save_plan(out.plans)
        time.sleep(slot_s)

if __name__ == "__main__":
    import threading
    import uvicorn

    # 1️⃣ 스케줄러 루프를 별도 스레드로 실행
    def start_scheduler():
        run_loop("config.yaml")

    t = threading.Thread(target=start_scheduler, daemon=True)
    t.start()

    # 2️⃣ 동시에 FastAPI 모니터링 서버 실행
    uvicorn.run("hub.app:app", host="0.0.0.0", port=8080)

