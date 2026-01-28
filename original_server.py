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

@app.route('/')
def index():
    """显示汇率对比页面"""
    return render_template('index.html')

@app.route('/api/rates')
def api_rates():
    """返回汇率数据"""
    json_file = os.path.join(os.path.dirname(__file__), 'exchange_rates.json')
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})

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
            timeout=120
        )
        
        if result.returncode == 0:
            # 读取最新的数据返回给前端
            with open('exchange_rates.json', 'r', encoding='utf-8') as f:
                rates = json.load(f)
            return jsonify({'status': 'success', 'rates': rates})
        else:
            return jsonify({'status': 'error', 'message': result.stderr})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("汇率对比页面已启动")
    print("=" * 50)
    print("访问地址: http://127.0.0.1:5000")
    print("=" * 50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
