# main.py
import subprocess
import sys
import time

def main():
    print("=" * 60)
    print("Starting AetherOps AI Microservices Coordinator...")
    print("=" * 60)
    
    # 1. Run Requirement Analysis Service (Module 1) on port 8001
    p1 = subprocess.Popen(
        ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"],
        cwd="services/requirement_analysis"
    )
    
    # 2. Run Cloud Architecture Generator Service (Module 2) on port 8002
    p2 = subprocess.Popen(
        ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"],
        cwd="services/architecture_generator"
    )
    
    print("\n[STARTED] Module 1 (Requirement Analysis Service) -> http://localhost:8001")
    print("[STARTED] Module 2 (Cloud Architecture Generator)  -> http://localhost:8002")
    print("\nPress Ctrl+C to terminate all services.\n")
    
    try:
        while True:
            # Check if any process has terminated unexpectedly
            if p1.poll() is not None:
                print(f"[ERROR] Module 1 terminated with exit code {p1.returncode}")
                break
            if p2.poll() is not None:
                print(f"[ERROR] Module 2 terminated with exit code {p2.returncode}")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print("\nStopping services...")
        p1.terminate()
        p2.terminate()
        p1.wait()
        p2.wait()
        print("All microservices stopped.")

if __name__ == "__main__":
    main()
