# -*- coding: utf-8 -*-
"""
汇率对比页面服务器
运行: python original_server.py
访问: http://127.0.0.1:5000
"""
import json
import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# 中英文公司名称对照
COMPANIES = {
    'dadeforex': {
        'name': 'DadeForex (大德通汇)',
        'url': 'https://www.dadeforex.com/'
    },
    'supay': {
        'name': 'Supay (联通换汇)',
        'url': 'https://www.supay.com/en/'
    },
    'kundaxpay': {
        'name': 'Kundaxpay (坤达速汇)',
        'url': 'https://www.kundaxpay.com.au/#/realTimeCurrency'
    },
    'moneychain': {
        'name': 'Moneychain (融侨速汇)',
        'url': 'https://www.moneychain.com.au/exchange-rates/'
    },
    'moneychase': {
        'name': 'Moneychase (万通国际)',
        'url': 'https://www.moneychase.com.au/currency-rate-page/'
    },
    'gtrading': {
        'name': 'GTrading (环球汇兑)',
        'url': 'https://www.gtrading.com.au/live-rate'
    }
}

# 默认数据（当没有数据时显示）
DEFAULT_RATES = {
    'dadeforex': {'AUD_CNY': {'buy': None, 'sell': None}},
    'supay': {'AUD_CNY': {'buy': None, 'sell': None}},
    'kundaxpay': {'AUD_CNY': {'buy': None, 'sell': None}},
    'moneychain': {'AUD_CNY': {'buy': None, 'sell': None}},
    'moneychase': {'AUD_CNY': {'buy': None, 'sell': None}},
    'gtrading': {'AUD_CNY': {'buy': None, 'sell': None}},
    'timestamp': None
}

def get_rates():
    """获取汇率数据"""
    json_file = os.path.join(os.path.dirname(__file__), 'exchange_rates.json')
    
    try:
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # 验证数据是否有效
            if data and 'timestamp' in data:
                return data
    except Exception as e:
        print(f"Error loading rates: {e}")
    
    # 返回默认数据
    return DEFAULT_RATES.copy()

@app.route('/')
def index():
    """显示汇率对比页面"""
    rates_data = get_rates()
    return render_template('index.html', rates=rates_data, companies=COMPANIES)

@app.route('/api/rates')
def api_rates():
    """返回汇率数据"""
    data = get_rates()
    return jsonify(data)

@app.route('/api/companies')
def api_companies():
    """返回公司信息"""
    return jsonify(COMPANIES)

@app.route('/api/update')
def api_update():
    """刷新汇率数据"""
    try:
        import subprocess
        result = subprocess.run(
            ['python', 'exchange_scraper.py'],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            timeout=180  # 增加超时时间
        )
        
        print(f"Scraper stdout: {result.stdout[:500] if result.stdout else 'None'}")
        print(f"Scraper stderr: {result.stderr[:500] if result.stderr else 'None'}")
        
        if result.returncode == 0:
            # 读取最新的数据返回给前端
            rates = get_rates()
            return jsonify({'status': 'success', 'rates': rates})
        else:
            return jsonify({'status': 'error', 'message': result.stderr[-500:]})
    except subprocess.TimeoutExpired:
        return jsonify({'status': 'error', 'message': 'Timeout: scraping took too long'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("汇率对比页面已启动")
    print("=" * 50)
    print("访问地址: http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
