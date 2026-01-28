"""
Check Supay raw data
"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.supay.com/rate.php?lang=en', wait_until='networkidle', timeout=30000)
    page.wait_for_timeout(2000)
    
    # Get raw table data
    result = page.evaluate("""
        () => {
            const rows = document.querySelectorAll("tr");
            for (let row of rows) {
                const text = row.innerText || "";
                if (text.toLowerCase().includes("vip") && (text.includes("AUD") || text.includes("CNY"))) {
                    const cells = Array.from(row.querySelectorAll("td, th")).map(td => td.innerText.trim());
                    return {
                        found: true,
                        cells: cells,
                        fullText: text
                    };
                }
            }
            return {found: false};
        }
    """)
    
    print('Raw result:', result)
    
    browser.close()






