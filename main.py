# main.py
"""
AetherOps Cloud - Real-Time Microservices Fleet Orchestrator & Live Telemetry Watchdog.

Features:
- Spawns, supervises, and maintains continuous 24/7 uptime for all 13 AetherOps microservices:
  * Gateway & Unified Dashboard: Port 8000
  * Project & Environment Management: Port 8001
  * Source & Cloud Connection: Port 8002
  * Source Code Analyzer: Port 8003
  * Requirement Analysis Engine: Port 8004
  * Architecture Graph Generator: Port 8005
  * IaC / Terraform Generator: Port 8006
  * FinOps Cost Optimizer: Port 8007
  * Security & Compliance Engine: Port 8008
  * CI/CD Pipeline Generator: Port 8009
  * Observability & Monitoring: Port 8010
  * Cloud Deployer & Drift Engine: Port 8011
  * Admin Console & Control Plane: Port 8012
- High-frequency parallel dynamic probing with millisecond latency telemetry (RTT).
- Real-time in-place terminal dashboard using Rich (flicker-free).
- Self-healing watchdog: auto-restarts failed processes with restart metrics.
- Clean SIGINT / SIGTERM signal handling.
"""

import os
import sys
import time
import signal
import datetime
import subprocess
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich import box

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SHARED_DIR = os.path.join(ROOT_DIR, "shared")
for p in (SHARED_DIR, ROOT_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

# Initialize centralized application secrets from AWS Secrets Manager
try:
    from aetherops_common.secrets import load_application_secrets
    load_application_secrets()
except Exception as _sec_err:
    print(f"[WARN] AWS Secrets Manager initialization: {_sec_err}")

# Resolve Python executable
VENV_PYTHON = os.path.join(ROOT_DIR, ".venv", "bin", "python")
PYTHON_EXE = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable
@dataclass
class ServiceSpec:
    id: str
    code: str
    name: str
    port: int
    dir: str
    health_path: str
    ui_url: str
    proc: Optional[subprocess.Popen] = None
    status: str = "STARTING"
    latency_ms: Optional[float] = None
    consecutive_passes: int = 0
    restarts: int = 0
    last_probe_time: float = 0.0
    error_msg: str = ""


FLEET_SPECS: List[ServiceSpec] = [
    ServiceSpec(
        id="auth_service",
        code="AUTH",
        name="Authentication Service",
        port=7999,
        dir="services/auth_service",
        health_path="/health",
        ui_url="http://localhost:7999/health"
    ),
    ServiceSpec(
        id="gateway",
        code="GW",
        name="Unified Dashboard & Gateway",
        port=8000,
        dir="services/gateway",
        health_path="/health",
        ui_url="http://localhost:8000"
    ),
    ServiceSpec(
        id="project_and_environment_management",
        code="MOD-PM",
        name="Project & Environment Manager",
        port=8001,
        dir="services/project_and_environment_management",
        health_path="/health",
        ui_url="http://localhost:8001/app"
    ),
    ServiceSpec(
        id="source_and_cloud_connection",
        code="MOD-SC",
        name="Source & Cloud Connection",
        port=8002,
        dir="services/source_and_cloud_connection",
        health_path="/health",
        ui_url="http://localhost:8002/app/source"
    ),
    ServiceSpec(
        id="repo_analyzer_service",
        code="MOD-RA",
        name="Source Code Analyzer",
        port=8003,
        dir="services/repo_analyzer_service",
        health_path="/health",
        ui_url="http://localhost:8003/app"
    ),
    ServiceSpec(
        id="requirement_analysis",
        code="MOD-01",
        name="Requirement Analysis Engine",
        port=8004,
        dir="services/requirement_analysis",
        health_path="/health",
        ui_url="http://localhost:8004/app"
    ),
    ServiceSpec(
        id="architecture_generator",
        code="MOD-02",
        name="Architecture Graph Generator",
        port=8005,
        dir="services/architecture_generator",
        health_path="/health",
        ui_url="http://localhost:8005/health"
    ),
    ServiceSpec(
        id="iac_generator",
        code="MOD-03",
        name="IaC Code Generator",
        port=8006,
        dir="services/iac_generator",
        health_path="/health",
        ui_url="http://localhost:8006/health"
    ),
    ServiceSpec(
        id="finops_optimizer",
        code="MOD-04",
        name="FinOps Cost Optimizer",
        port=8007,
        dir="services/finops_optimizer",
        health_path="/health",
        ui_url="http://localhost:8007/health"
    ),
    ServiceSpec(
        id="security_scanner",
        code="MOD-05",
        name="Security & Compliance Engine",
        port=8008,
        dir="services/security_scanner",
        health_path="/health",
        ui_url="http://localhost:8008/health"
    ),
    ServiceSpec(
        id="cicd_pipeline",
        code="MOD-06",
        name="CI/CD Pipeline Engine",
        port=8009,
        dir="services/cicd_pipeline",
        health_path="/health",
        ui_url="http://localhost:8009/health"
    ),
    ServiceSpec(
        id="observability_setup",
        code="MOD-07",
        name="Observability & APM Engine",
        port=8010,
        dir="services/observability_setup",
        health_path="/health",
        ui_url="http://localhost:8010/health"
    ),
    ServiceSpec(
        id="cloud_deployer",
        code="MOD-08",
        name="Cloud Deployer & Drift Engine",
        port=8011,
        dir="services/cloud_deployer",
        health_path="/health",
        ui_url="http://localhost:8011/health"
    ),
    ServiceSpec(
        id="admin_console",
        code="ADMIN",
        name="Admin Console & Control Plane",
        port=8012,
        dir="services/admin_console",
        health_path="/health",
        ui_url="http://localhost:8012/admin"
    ),
]



class RealTimeFleetOrchestrator:
    def __init__(self):
        self.running = True
        self.start_time = time.time()
        self.services: List[ServiceSpec] = FLEET_SPECS
        self.console = Console()
        self.executor = ThreadPoolExecutor(max_workers=len(self.services))
        self.events_log: List[str] = []

    def log_event(self, msg: str):
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{now_str}] {msg}"
        self.events_log.append(entry)
        if len(self.events_log) > 4:
            self.events_log.pop(0)

    def free_port_if_occupied(self, port: int):
        """Ensures port is completely free before spawning service."""
        try:
            out = subprocess.check_output(["lsof", "-ti", f":{port}"], text=True).strip()
            if out:
                for pid_str in out.split():
                    try:
                        os.kill(int(pid_str), signal.SIGKILL)
                    except OSError:
                        pass
                time.sleep(0.15)
        except Exception:
            pass

    def get_bind_host(self, port: int) -> str:
        """Determines if 0.0.0.0 can be bound, else falls back to 127.0.0.1 (e.g. if Tailscale or another interface holds the port)."""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("0.0.0.0", port))
                return "0.0.0.0"
        except OSError:
            return "127.0.0.1"

    def start_service(self, spec: ServiceSpec):
        self.free_port_if_occupied(spec.port)
        cwd = os.path.join(ROOT_DIR, spec.dir)
        env = os.environ.copy()
        existing_ppath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{cwd}:{SHARED_DIR}:{ROOT_DIR}:{existing_ppath}".rstrip(":")
        host = self.get_bind_host(spec.port)
        cmd = [
            PYTHON_EXE,
            "-m", "uvicorn",
            "app.main:app",
            "--host", host,
            "--port", str(spec.port),
            "--log-level", "warning"
        ]

        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid
        )
        spec.proc = proc
        spec.status = "STARTING"
        self.log_event(f"Spawned {spec.name} (PID: {proc.pid}) on {host}:{spec.port}")


    def probe_single_service(self, spec: ServiceSpec):
        """
        Executes a real-time HTTP probe with millisecond round-trip latency measurement.
        """
        url = f"http://127.0.0.1:{spec.port}{spec.health_path}"
        t0 = time.perf_counter()
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "AetherOps-Realtime-Probe/2.0"}
            )
            with urllib.request.urlopen(req, timeout=0.8) as resp:
                elapsed_ms = (time.perf_counter() - t0) * 1000.0
                if resp.status == 200:
                    spec.status = "ONLINE"
                    spec.latency_ms = round(elapsed_ms, 1)
                    spec.consecutive_passes += 1
                    spec.error_msg = ""
                else:
                    spec.status = "DEGRADED"
                    spec.latency_ms = round(elapsed_ms, 1)
                    spec.error_msg = f"HTTP {resp.status}"
        except urllib.error.HTTPError as e:
            spec.status = "DEGRADED"
            spec.latency_ms = round((time.perf_counter() - t0) * 1000.0, 1)
            spec.error_msg = f"HTTP {e.code}"
        except Exception as e:
            # Check if process is dead
            if spec.proc and spec.proc.poll() is not None:
                spec.status = "CRASHED"
            else:
                spec.status = "OFFLINE"
            spec.latency_ms = None
            spec.consecutive_passes = 0
            spec.error_msg = str(e)[:24]

        spec.last_probe_time = time.time()

    def probe_all_services(self):
        futures = [self.executor.submit(self.probe_single_service, s) for s in self.services]
        for f in futures:
            f.result()

    def render_fleet_dashboard(self) -> Table:
        """
        Constructs the styled real-time Rich table.
        """
        uptime_sec = int(time.time() - self.start_time)
        hrs = uptime_sec // 3600
        mins = (uptime_sec % 3600) // 60
        secs = uptime_sec % 60
        uptime_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"

        online_count = sum(1 for s in self.services if s.status == "ONLINE")
        total_count = len(self.services)
        health_pct = round((online_count / total_count) * 100)

        health_color = "bright_green" if health_pct == 100 else ("bright_yellow" if health_pct >= 70 else "bright_red")

        title_text = Text()
        title_text.append("⚡ AETHEROPS CLOUD ", style="bold bright_white")
        title_text.append("— REAL-TIME MICROSERVICES FLEET TELEMETRY\n", style="bold cyan")
        title_text.append(f"Fleet Status: ", style="dim")
        title_text.append(f"{online_count}/{total_count} Online ({health_pct}%) ", style=f"bold {health_color}")
        title_text.append("• ", style="dim")
        title_text.append(f"Uptime: {uptime_str} ", style="bold white")
        title_text.append("• ", style="dim")
        title_text.append(f"Watchdog: Active (Auto-Recover) ", style="bold green")
        title_text.append("• ", style="dim")
        title_text.append(f"Probe: Dynamic 1.0s (Parallel RTT)", style="dim")

        table = Table(
            title=title_text,
            box=box.ROUNDED,
            header_style="bold bright_white on grey23",
            border_style="bright_blue",
            expand=False
        )

        table.add_column("Code", style="bold cyan", no_wrap=True, justify="center")
        table.add_column("Service Name", style="bold white", no_wrap=True)
        table.add_column("Port", style="bright_yellow", no_wrap=True, justify="center")
        table.add_column("PID", style="dim", no_wrap=True, justify="center")
        table.add_column("Real-Time Probe", no_wrap=True, justify="center")
        table.add_column("RTT Latency", no_wrap=True, justify="right")
        table.add_column("Checks", style="dim", no_wrap=True, justify="center")
        table.add_column("Restarts", no_wrap=True, justify="center")
        table.add_column("Endpoint & Web UI", style="cyan underline", no_wrap=True)

        for s in self.services:
            pid_str = str(s.proc.pid) if s.proc and s.proc.poll() is None else "[bright_red]DEAD[/bright_red]"

            # Status Badge with pulse indicator
            if s.status == "ONLINE":
                status_text = Text("● ONLINE", style="bold bright_green")
            elif s.status == "DEGRADED":
                status_text = Text("▲ DEGRADED", style="bold bright_yellow")
            elif s.status == "STARTING":
                status_text = Text("◌ STARTING", style="bold yellow")
            else:
                status_text = Text("○ OFFLINE", style="bold bright_red")

            # Latency styling
            if s.latency_ms is not None:
                if s.latency_ms < 50.0:
                    lat_str = f"[bright_green]{s.latency_ms:.1f} ms[/bright_green]"
                elif s.latency_ms < 200.0:
                    lat_str = f"[bright_yellow]{s.latency_ms:.1f} ms[/bright_yellow]"
                else:
                    lat_str = f"[bright_red]{s.latency_ms:.1f} ms[/bright_red]"
            else:
                lat_str = "[dim]--[/dim]"

            checks_str = f"[green]{s.consecutive_passes} ok[/green]" if s.consecutive_passes > 0 else "[dim]0[/dim]"
            restarts_str = f"[bold red]{s.restarts}[/bold red]" if s.restarts > 0 else "[dim]0[/dim]"

            table.add_row(
                s.code,
                s.name,
                str(s.port),
                pid_str,
                status_text,
                lat_str,
                checks_str,
                restarts_str,
                s.ui_url
            )

        return table

    def build_full_view(self) -> Panel:
        table = self.render_fleet_dashboard()

        # Events log section
        log_text = Text()
        if not self.events_log:
            log_text.append("Initializing fleet supervisor...", style="dim")
        else:
            for line in self.events_log:
                log_text.append(f"  {line}\n", style="dim green")

        layout = Layout()
        layout.split_column(
            Layout(table, ratio=3),
            Layout(Panel(log_text, title="[bold white]Real-Time Event Stream[/bold white]", border_style="grey37", box=box.SIMPLE), ratio=1)
        )

        return Panel(
            layout,
            subtitle="[dim]Press [bold white]Ctrl+C[/bold white] to gracefully stop all services[/dim]",
            border_style="bright_blue",
            box=box.DOUBLE
        )

    def shutdown(self, signum=None, frame=None):
        self.running = False
        print(f"\n\n[FLEET SUPERVISOR] Stopping all {len(self.services)} microservices gracefully...")
        for s in self.services:
            if s.proc and s.proc.poll() is None:
                try:
                    os.killpg(os.getpgid(s.proc.pid), signal.SIGTERM)
                except Exception:
                    try:
                        s.proc.terminate()
                    except Exception:
                        pass

        time.sleep(0.8)
        for s in self.services:
            if s.proc and s.proc.poll() is None:
                try:
                    os.killpg(os.getpgid(s.proc.pid), signal.SIGKILL)
                except Exception:
                    try:
                        s.proc.kill()
                    except Exception:
                        pass

        self.executor.shutdown(wait=False)
        print("[FLEET SUPERVISOR] All microservices stopped cleanly. Goodbye.")
        sys.exit(0)

    def run(self):
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

        self.console.print(f"\n[bold cyan]Booting AetherOps Microservices Fleet ({len(self.services)} Services)...[/bold cyan]")
        for s in self.services:
            self.start_service(s)


        # Allow services initial socket binding window
        time.sleep(2.0)

        # Initial probe before displaying first frame
        self.probe_all_services()

        # Main Real-Time Probe Loop
        try:
            with Live(self.render_fleet_dashboard(), console=self.console, refresh_per_second=2, screen=False) as live:
                while self.running:
                    # 1. Execute concurrent real-time probes
                    self.probe_all_services()

                    # 2. Watchdog: check for dead processes and auto-recover
                    for s in self.services:
                        if s.proc and s.proc.poll() is not None:
                            exit_code = s.proc.returncode
                            s.restarts += 1
                            self.log_event(f"WATCHDOG: '{s.name}' exited (code: {exit_code}). Auto-restarting...")
                            time.sleep(0.5)
                            self.start_service(s)

                    # 3. Update the live terminal view
                    live.update(self.render_fleet_dashboard())

                    time.sleep(1.0)
        except KeyboardInterrupt:
            self.shutdown()


def main():
    orchestrator = RealTimeFleetOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()
