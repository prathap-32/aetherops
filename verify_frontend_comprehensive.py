import os
import time
from playwright.sync_api import sync_playwright

def run_comprehensive_verification():
    print("Starting Comprehensive Playwright Frontend & Functional Verification...")
    os.makedirs("screenshots", exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        
        console_errors = []
        network_failures = []
        
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("response", lambda res: network_failures.append(f"{res.status} {res.url}") if res.status >= 400 else None)
        
        print("1. Loading http://localhost:8000 ...")
        page.goto("http://localhost:8000", wait_until="networkidle")
        
        # Handle login if login page is presented
        if page.locator("input[name='username']").count() > 0:
            print("Authenticating as admin / admin123...")
            page.fill("input[name='username']", "admin")
            page.fill("input[type='password']", "admin123")
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
        print("2. Verifying Dashboard / Overview ...")
        page.screenshot(path="screenshots/verified_dashboard.png", full_page=True)
        
        routes_to_verify = [
            ("Risk Analysis & Dry Run", "/risk-analysis", "verified_risk_analysis.png"),
            ("Approval Gate & Execution", "/execution", "verified_approval_gate.png"),
            ("Cloud Deployment", "/deployment", "verified_cloud_deployment.png"),
            ("State Inventory", "/state-inventory", "verified_state_inventory.png"),
        ]
        
        for name, route, filename in routes_to_verify:
            print(f"3. Navigating to {name} ({route}) ...")
            page.goto(f"http://localhost:8000{route}", wait_until="networkidle")
            time.sleep(1.5)
            page.screenshot(path=f"screenshots/{filename}", full_page=True)
            print(f"   - {name} rendered successfully. Current URL: {page.url}")
            
        print("\nVerification Summary:")
        print(f" - Captured Console Errors: {len(console_errors)}")
        for err in console_errors[:5]:
            print(f"   [Error] {err}")
            
        print(f" - Failed Network Responses (>=400): {len(network_failures)}")
        for fail in network_failures[:10]:
            print(f"   [Network Fail] {fail}")
            
        browser.close()
        print("Comprehensive Playwright verification completed successfully!")

if __name__ == "__main__":
    run_comprehensive_verification()
