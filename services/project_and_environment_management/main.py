# services/project_and_environment_management/main.py
import uvicorn


def main():
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="warning",
    )


if __name__ == "__main__":
    main()
