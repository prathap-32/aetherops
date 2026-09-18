# services/admin_console/main.py
import uvicorn

def main():
    uvicorn.run("app.main:app", host="0.0.0.0", port=2470, reload=True)

if __name__ == "__main__":
    main()
