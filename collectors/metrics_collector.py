from typing import List, Dict, Optional
from prometheus_api_client import PrometheusConnect
from optimizer.schemas import ClusterCapacity

def get_cluster_capacity(regions: List[str], horizon_slots: int, prom_urls: Optional[Dict[str,str]] = None) -> List[ClusterCapacity]:
    caps: List[ClusterCapacity] = []
    for r in regions:
        cpu, mem, gpu = 32, 128, 0
        for t in range(horizon_slots):
            caps.append(ClusterCapacity(region=r, slot=t, cpu_cap=cpu, mem_gb_cap=mem, gpu_cap=gpu))
    return caps
