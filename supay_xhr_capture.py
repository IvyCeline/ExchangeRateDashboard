"""
捕获 Supay 页面的 XHR 请求，找出加载汇率的实际请求
"""
from playwright.sync_api import sync_playwright
import json

URL = 'https://www.supay.com/en/'

def main():
    captured_requests = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # 监听所有请求
        def handle_request(request):
            url = request.url
            method = request.method
            post_data = request.post_data

            # 只记录 admin-ajax.php 的请求
            if 'admin-ajax.php' in url:
                captured_requests.append({
                    'url': url,
                    'method': method,
                    'post_data': post_data
                })

        page.on('request', handle_request)

        # 访问页面
        page.goto(URL, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(3000)  # 等待足够长的时间让所有 AJAX 完成

        # 尝试模拟用户交互 - 点击汇率相关的元素
        try:
            # 查找包含汇率的表格或元素
            page.evaluate("""
                () => {
                    // 尝试触发价格刷新
                    const buttons = document.querySelectorAll('button');
                    for(let btn of buttons) {
                        if(btn.innerText.toLowerCase().includes('rate') ||
                           btn.innerText.toLowerCase().includes('refresh') ||
                           btn.innerText.includes('汇率')) {
                            btn.click();
                            console.log('Clicked button:', btn.innerText);
                        }
                    }
                }
            """)
            page.wait_for_timeout(2000)
        except Exception as e:
            print(f"Interaction exception: {e}")

        # 再次尝试获取页面上的实际价格
        page_prices = page.evaluate("""
            () => {
                const result = {text: [], table: []};

                // 查找包含 AUD 和 CNY 的文本
                const allText = document.body.innerText;
                const lines = allText.split('\\n');
                for(let line of lines) {
                    if(line.includes('AUD') && line.includes('CNY') ||
                       line.includes('澳元') && line.includes('人民币')) {
                        result.text.push(line.trim());
                    }
                }

                // 查找表格
                const tables = document.querySelectorAll('table');
                for(let table of tables) {
                    const rows = [];
                    for(let tr of table.querySelectorAll('tr')) {
                        const cells = [];
                        for(let td of tr.querySelectorAll('td, th')) {
                            cells.push(td.innerText.trim());
                        }
                        if(cells.length > 0) rows.push(cells);
                    }
                    if(rows.length > 0) result.table.push(rows);
                }

                return result;
            }
        """)

        browser.close()

    # 保存结果
    output = {
        'captured_ajax_requests': captured_requests,
        'page_prices_found': page_prices
    }

    with open('supay_xhr_capture.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Captured {len(captured_requests)} AJAX requests")
    print("Saved to supay_xhr_capture.json")

    if captured_requests:
        print("\nFirst AJAX request details:")
        print(json.dumps(captured_requests[0], indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()

