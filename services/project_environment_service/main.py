# services/project_and_environment_management/main.py
import os
import socket
import uvicorn

def get_bind_host(port: int) -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("0.0.0.0", port))
            return "0.0.0.0"
    except OSError:
        return "127.0.0.1"

def main():
    port = int(os.getenv("PORT", 8001))
    host = os.getenv("HOST") or get_bind_host(port)
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="warning",
    )

if __name__ == "__main__":
    main()
