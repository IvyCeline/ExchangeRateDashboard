from playwright.sync_api import sync_playwright
import json

URL = 'https://www.supay.com/en/'

def main():
    out = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(1500)

        # capture some globals
        globals = page.evaluate("() => ({stm_get_prices: window.stm_get_prices, ajaxurl: window.ajaxurl || window.stm_wpcfto_ajaxurl || window.sbiajaxurl})")
        out['globals'] = globals

        # Try to call jQuery.post in page context to trigger stm_get_prices action
        try:
            res = page.evaluate("""
                async () => {
                    const ajax = window.ajaxurl || window.stm_wpcfto_ajaxurl || window.sbiajaxurl || '/wp-admin/admin-ajax.php';
                    const nonce = window.stm_get_prices || window.stm_get_prices || null;
                    if (!window.jQuery) return {error: 'no-jquery'};
                    return await new Promise((resolve) => {
                        try {
                            jQuery.post(ajax, {action: 'stm_get_prices', security: nonce}, function(data){
                                resolve({status: 'ok', data: data});
                            }).fail(function(err){
                                resolve({status: 'fail', err: String(err)});
                            });
                        } catch(e) {
                            resolve({status: 'exception', error: String(e)});
                        }
                    });
                }
            """)
            out['post_result'] = res
        except Exception as e:
            out['post_exception'] = str(e)

        # Also try invoking any window functions that look like get_prices if present
        try:
            call_res = page.evaluate("""
                () => {
                    const candidates = ['stm_get_prices','get_prices','getRate','getRates'];
                    for (let name of candidates) {
                        try {
                            const fn = window[name];
                            if (typeof fn === 'function') {
                                try {
                                    const r = fn(); // might not return, but try
                                    return {called: name, result: r};
                                } catch(e) {
                                    return {called: name, error: String(e)};
                                }
                            }
                        } catch(e) {}
                    }
                    return {called: null};
                }
            """)
            out['call_result'] = call_res
        except Exception as e:
            out['call_exception'] = str(e)

        browser.close()

    with open('supay_trigger_out.json','w',encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print('Wrote supay_trigger_out.json')

if __name__ == '__main__':
    main()









