import os, subprocess, tempfile
from jinja2 import Environment, FileSystemLoader

class MCADDispatcher:
    def __init__(self, namespace: str, dry_run: bool = True):
        tpl_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(loader=FileSystemLoader(tpl_dir))
        self.tpl = self.env.get_template('appwrapper_tpl.yaml.j2')
        self.ns = namespace
        self.dry = dry_run

    def dispatch_appwrapper(self, kubecontext: str, job_id: str, region: str, image: str, cpu: int, mem_gb: int):
        manifest = self.tpl.render(job_id=job_id, region=region, image=image, cpu=cpu, mem_gb=mem_gb, namespace=self.ns)
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml") as f:
            f.write(manifest)
            path = f.name
        cmd = ["kubectl", "--context", kubecontext, "apply", "-f", path]
        if self.dry:
            print(f"[DRY-RUN] kubectl --context {kubecontext} apply -f {path}")
            print(manifest)
        else:
            subprocess.check_call(cmd)
        os.unlink(path)
