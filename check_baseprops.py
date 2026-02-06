from playwright.sync_api import sync_playwright

url = "https://baseprops.tech/"
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(url, wait_until="networkidle", timeout=60000)
    found = page.locator("text=Decision Intelligence1.").first.is_visible()
    print("FOUND_DECISION_INTELLIGENCE1=", found)
    page.screenshot(path="baseprops_home.png", full_page=True)
    browser.close()
