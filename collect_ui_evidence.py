import os
import time
from playwright.sync_api import sync_playwright

def collect_evidence():
    print("Starting AetherOps UI Evidence Collection & Viewport Verification...")
    
    # Ensure evidence directories exist
    os.makedirs("evidence/ui/mobile", exist_ok=True)
    os.makedirs("evidence/ui/tablet", exist_ok=True)
    os.makedirs("evidence/ui/desktop", exist_ok=True)
    
    viewports = [
        {"name": "mobile-375", "width": 375, "height": 812, "category": "mobile"},
        {"name": "mobile-390", "width": 390, "height": 844, "category": "mobile"},
        {"name": "tablet-768", "width": 768, "height": 1024, "category": "tablet"},
        {"name": "desktop-1280", "width": 1280, "height": 900, "category": "desktop"},
        {"name": "desktop-1440", "width": 1440, "height": 900, "category": "desktop"},
    ]
    
    pages = [
        {"id": "dashboard", "path": "/", "title": "Platform Dashboard"},
        {"id": "projects", "path": "/project-environment", "title": "Project Management"},
        {"id": "source_cloud", "path": "/source-connection", "title": "Source & Cloud Connection"},
        {"id": "architecture", "path": "/architecture-studio", "title": "Architecture Studio"},
        {"id": "designer", "path": "/architecture-designer", "title": "Architecture Designer"},
        {"id": "terraform", "path": "/terraform", "title": "Terraform / IaC"},
        {"id": "deployment", "path": "/deployment", "title": "Cloud Deployment"},
        {"id": "monitoring", "path": "/monitoring", "title": "Monitoring & APM"},
        {"id": "audit", "path": "/audit", "title": "Security & Session Audit"},
        {"id": "admin", "path": "/admin", "title": "Admin Console"},
    ]
    
    typography_metrics = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        
        for vp in viewports:
            print(f"\n--- Testing Viewport: {vp['name']} ({vp['width']}x{vp['height']}) ---")
            context = browser.new_context(viewport={"width": vp["width"], "height": vp["height"]})
            page = context.new_page()
            
            # Login first
            page.goto("http://localhost:8000", wait_until="networkidle")
            if page.locator("input[name='username']").count() > 0:
                page.fill("input[name='username']", "admin")
                page.fill("input[type='password']", "admin123")
                page.click("button[type='submit']")
                page.wait_for_load_state("networkidle")
                time.sleep(1.5)
                
            for pg in pages:
                url = f"http://localhost:8000{pg['path']}"
                try:
                    page.goto(url, wait_until="networkidle", timeout=10000)
                    time.sleep(1)
                    
                    # Capture screenshot
                    shot_path = f"evidence/ui/{vp['category']}/{pg['id']}-{vp['name']}.png"
                    page.screenshot(path=shot_path, full_page=False)
                    print(f"Captured: {shot_path}")
                    
                    # Measure typography on dashboard or first loaded page
                    if pg['id'] == 'dashboard':
                        metrics = page.evaluate("""() => {
                            const body = window.getComputedStyle(document.body);
                            const h1 = document.querySelector('h1');
                            const btn = document.querySelector('button');
                            const input = document.querySelector('input');
                            return {
                                fontFamily: body.fontFamily,
                                bodyFontSize: body.fontSize,
                                h1FontSize: h1 ? window.getComputedStyle(h1).fontSize : 'N/A',
                                btnFontSize: btn ? window.getComputedStyle(btn).fontSize : 'N/A',
                                inputFontSize: input ? window.getComputedStyle(input).fontSize : 'N/A',
                            };
                        """)
                        typography_metrics[vp['name']] = metrics
                except Exception as e:
                    print(f"Error loading {url} at {vp['name']}: {e}")
                    
            context.close()
        
        browser.close()
        
    print("\n--- Collected Typography Metrics ---")
    for vp_name, m in typography_metrics.items():
        print(f"Viewport [{vp_name}]: Font Family: {m['fontFamily']} | Body: {m['bodyFontSize']} | H1: {m['h1FontSize']} | Button: {m['btnFontSize']} | Input: {m['inputFontSize']}")

if __name__ == "__main__":
    collect_evidence()
