# main.py
"""
AetherOps Cloud - Master Microservices Fleet Orchestrator.

Spawns, supervises, and maintains continuous 24/7 uptime for all 9 AetherOps microservices:
- Admin Console & Control Plane: Port 2470
- Module 1 (Requirement Analysis): Port 8001
- Module 2 (Architecture Generator): Port 8002
- Module 3 (IaC Generator): Port 8003
- Module 4 (FinOps Optimizer): Port 8004
- Module 5 (Security Scanner): Port 8005
- Module 6 (CI/CD Pipeline): Port 8006
- Module 7 (Observability Setup): Port 8007
- Module 8 (Cloud Deployer): Port 8008

Includes automatic process restart (self-healing supervisor), graceful SIGINT/SIGTERM handling,
and real-time health telemetry monitoring.
"""

import os
import sys
import time
import signal
import subprocess
import urllib.request
import urllib.error
from typing import Dict, Any, List

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Resolve Python executable (prefer current venv, fallback to sys.executable)
VENV_PYTHON = os.path.join(ROOT_DIR, ".venv", "bin", "python")
PYTHON_EXE = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable

# Service Registry Definition
SERVICES: List[Dict[str, Any]] = [
    {
        "id": "admin_console",
        "name": "Admin Console & Gateway",
        "module": "Admin Control Plane",
        "port": 2470,
        "dir": "services/admin_console",
        "health_path": "/health"
    },
    {
        "id": "requirement_analysis",
        "name": "Requirement Analysis Engine",
        "module": "Module 1",
        "port": 8001,
        "dir": "services/requirement_analysis",
        "health_path": "/health"
    },
    {
        "id": "architecture_generator",
        "name": "Architecture Graph Generator",
        "module": "Module 2",
        "port": 8002,
        "dir": "services/architecture_generator",
        "health_path": "/health"
    },
    {
        "id": "iac_generator",
        "name": "IaC Code Generator",
        "module": "Module 3",
        "port": 8003,
        "dir": "services/iac_generator",
        "health_path": "/health"
    },
    {
        "id": "finops_optimizer",
        "name": "FinOps Cost Optimizer",
        "module": "Module 4",
        "port": 8004,
        "dir": "services/finops_optimizer",
        "health_path": "/health"
    },
    {
        "id": "security_scanner",
        "name": "Security & Compliance Engine",
        "module": "Module 5",
        "port": 8005,
        "dir": "services/security_scanner",
        "health_path": "/health"
    },
    {
        "id": "cicd_pipeline",
        "name": "CI/CD Pipeline Engine",
        "module": "Module 6",
        "port": 8006,
        "dir": "services/cicd_pipeline",
        "health_path": "/health"
    },
    {
        "id": "observability_setup",
        "name": "Observability & APM Engine",
        "module": "Module 7",
        "port": 8007,
        "dir": "services/observability_setup",
        "health_path": "/health"
    },
    {
        "id": "cloud_deployer",
        "name": "Cloud Deployer & Drift Engine",
        "module": "Module 8",
        "port": 8008,
        "dir": "services/cloud_deployer",
        "health_path": "/health"
    },
]

class FleetOrchestrator:
    def __init__(self):
        self.running = True
        self.processes: Dict[str, subprocess.Popen] = {}
        self.restart_counts: Dict[str, int] = {s["id"]: 0 for s in SERVICES}
        self.last_health_check = 0.0

    def start_service(self, service: Dict[str, Any]) -> subprocess.Popen:
        svc_id = service["id"]
        port = service["port"]
        cwd = os.path.join(ROOT_DIR, service["dir"])

        env = os.environ.copy()
        env["PYTHONPATH"] = cwd

        cmd = [
            PYTHON_EXE,
            "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", str(port),
            "--log-level", "warning"
        ]

        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        self.processes[svc_id] = proc
        return proc

    def check_service_health(self, port: int, health_path: str) -> bool:
        url = f"http://127.0.0.1:{port}{health_path}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AetherOps-Fleet-Supervisor"})
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def print_status_dashboard(self):
        os.system("clear" if os.name == "posix" and sys.stdout.isatty() else "")
        print("=" * 96)
        print("                 AETHEROPS CLOUD - 24/7 MICROSERVICES FLEET SUPERVISOR")
        print("=" * 96)
        print(f" {'MODULE':<12} | {'SERVICE NAME':<30} | {'PORT':<5} | {'PID':<7} | {'HEALTH':<10} | {'RESTARTS':<8}")
        print("-" * 96)

        for s in SERVICES:
            sid = s["id"]
            proc = self.processes.get(sid)
            pid = str(proc.pid) if proc and proc.poll() is None else "DEAD"
            is_healthy = self.check_service_health(s["port"], s["health_path"])
            health_str = "\033[92mONLINE\033[0m" if is_healthy else "\033[91mSTARTING\033[0m"
            restarts = self.restart_counts.get(sid, 0)

            print(f" {s['module']:<12} | {s['name']:<30} | {s['port']:<5} | {pid:<7} | {health_str:<19} | {restarts:<8}")

        print("=" * 96)
        print(" [UI Access]  Admin Console: http://localhost:2470/admin")
        print("              Module 1 UI:   http://localhost:8001/app")
        print(" [Controls]   Self-healing watchdog active. Press Ctrl+C to gracefully stop all services.")
        print("=" * 96)

    def shutdown(self, signum=None, frame=None):
        print("\n\n[FLEET ORCHESTRATOR] Received shutdown signal. Gracefully stopping all services...")
        self.running = False
        for sid, proc in self.processes.items():
            if proc.poll() is None:
                try:
                    proc.terminate()
                except Exception:
                    pass

        # Give processes up to 3 seconds to exit gracefully
        time.sleep(1.0)
        for sid, proc in self.processes.items():
            if proc.poll() is None:
                try:
                    proc.kill()
                except Exception:
                    pass

        print("[FLEET ORCHESTRATOR] All microservices stopped cleanly. Goodbye.")
        sys.exit(0)

    def run(self):
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

        print("[FLEET ORCHESTRATOR] Booting 9 microservices in independent workspaces...")
        for s in SERVICES:
            print(f"  -> Spawning {s['name']} on port {s['port']}...")
            self.start_service(s)

        # Allow services 2.5 seconds to bind sockets
        time.sleep(2.5)
        self.print_status_dashboard()

        last_dashboard_update = time.time()

        while self.running:
            # Self-healing watchdog: check if any process died
            for s in SERVICES:
                sid = s["id"]
                proc = self.processes.get(sid)
                if proc and proc.poll() is not None:
                    exit_code = proc.returncode
                    self.restart_counts[sid] += 1
                    print(f"\n[WATCHDOG ALERT] Service '{s['name']}' exited unexpectedly with code {exit_code}!")
                    print(f"[WATCHDOG RECOVERY] Auto-restarting '{s['name']}' on port {s['port']} (Restart #{self.restart_counts[sid]})...")
                    self.start_service(s)

            # Update dashboard every 10 seconds
            if time.time() - last_dashboard_update >= 10.0:
                self.print_status_dashboard()
                last_dashboard_update = time.time()

            time.sleep(1.0)

def main():
    orchestrator = FleetOrchestrator()
    orchestrator.run()

if __name__ == "__main__":
    main()
