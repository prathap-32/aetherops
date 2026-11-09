import os
import time
from playwright.sync_api import sync_playwright

def run_verification():
    print("Starting Playwright Browser Verification of AetherOps Frontend...")
    os.makedirs("screenshots", exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        
        # Capture console errors and page errors
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        
        page.on("pageerror", lambda err: print(f"Page Error: {err}"))
        
        print("1. Opening http://localhost:8000 ...")
        page.goto("http://localhost:8000", wait_until="networkidle")
        
        # Check if login page is shown
        if page.locator("input[name='username']").count() > 0 or page.locator("input[type='password']").count() > 0:
            print("Logging in with admin / admin123...")
            page.fill("input[name='username']", "admin")
            page.fill("input[type='password']", "admin123")
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
        print("2. Verifying Dashboard / Overview ...")
        page.screenshot(path="screenshots/dashboard.png", full_page=True)
        
        # Navigate to Risk Analysis / Dry Run
        print("3. Navigating to Risk Analysis & Dry Run (/risk-analysis) ...")
        page.goto("http://localhost:8000/risk-analysis", wait_until="networkidle")
        time.sleep(1)
        page.screenshot(path="screenshots/risk_analysis.png", full_page=True)
        
        # Navigate to Execution / Approval Gate
        print("4. Navigating to Approval Gate (/execution) ...")
        page.goto("http://localhost:8000/execution", wait_until="networkidle")
        time.sleep(1)
        page.screenshot(path="screenshots/approval_gate.png", full_page=True)
        
        # Navigate to Cloud Deployment
        print("5. Navigating to Cloud Deployment (/deployment) ...")
        page.goto("http://localhost:8000/deployment", wait_until="networkidle")
        time.sleep(1)
        page.screenshot(path="screenshots/cloud_deployment.png", full_page=True)
        
        # Navigate to State Inventory
        print("6. Navigating to State Inventory (/state-inventory) ...")
        page.goto("http://localhost:8000/state-inventory", wait_until="networkidle")
        time.sleep(1)
        page.screenshot(path="screenshots/state_inventory.png", full_page=True)
        
        print("Verification completed successfully!")
        print(f"Captured console errors: {len(console_errors)}")
        for err in console_errors[:10]:
            print(f" - {err}")
            
        browser.close()

if __name__ == "__main__":
    run_verification()
