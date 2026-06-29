from playwright.sync_api import sync_playwright

def run_qa():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        errors = []
        page.on("console", lambda msg: errors.append(f"Console {msg.type}: {msg.text}") if msg.type in ["error", "warning"] else None)
        page.on("pageerror", lambda exc: errors.append(f"Page Error: {exc}"))
        
        print("Navigating to Home Page...")
        page.goto("http://localhost:8080")
        page.wait_for_load_state("networkidle")
        
        print("Checking FAQ interaction...")
        faq_buttons = page.locator(".faq-question")
        if faq_buttons.count() > 0:
            faq_buttons.first.click()
            page.wait_for_timeout(500)
            is_visible = page.locator(".faq-answer").first.is_visible()
            print(f"FAQ Answer visible after click: {is_visible}")
        else:
            print("No FAQ buttons found!")
            
        print("Navigating to Services Page...")
        page.goto("http://localhost:8080/services.html")
        page.wait_for_load_state("networkidle")
        
        print("Checking for broken images...")
        images = page.locator("img")
        broken_images = 0
        for i in range(images.count()):
            is_broken = page.evaluate("(img) => img.naturalWidth === 0 || img.naturalHeight === 0", images.nth(i).element_handle())
            if is_broken:
                broken_images += 1
        print(f"Broken images found: {broken_images}")
        
        print("\n--- QA Results ---")
        if errors:
            print("Console Errors/Warnings:")
            for e in errors:
                print(f"  - {e}")
        else:
            print("No console errors found.")
            
        browser.close()

if __name__ == "__main__":
    run_qa()