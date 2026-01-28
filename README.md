# 澳大利亚换汇公司汇率看板

这是一个自动抓取澳大利亚各大换汇公司汇率数据的看板系统，专注于AUD/CNY汇率的买入和卖出价格。

## 功能特点

- 🔄 自动抓取6家澳大利亚换汇公司的汇率数据
- 📊 实时显示AUD/CNY汇率（买入价和卖出价）
- ⏰ 每3小时自动更新（上午10点至下午6点）
- 🌐 简单的Web界面展示数据
- 📱 响应式设计，支持移动端查看

## 支持的公司

1. **Moneychain** - https://www.moneychain.com.au/exchange-rates/
2. **Supay** - https://www.supay.com/en/
3. **Moneychase** - https://www.moneychase.com.au/currency-rate-page/
4. **Dadeforex** - https://www.dadeforex.com/
5. **GTrading** - https://www.gtrading.com.au/live-rate
6. **Kundaxpay** - https://www.kundaxpay.com.au/#/realTimeCurrency

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行系统

使用启动脚本：

```bash
python run.py
```

根据提示选择运行模式：

- **启动Web界面** (推荐): 启动Web服务器，访问 http://localhost:5000 查看汇率数据
- **运行调度器**: 启动后台自动更新服务
- **手动更新**: 立即更新一次汇率数据
- **测试爬虫**: 测试汇率抓取功能

### 3. 直接运行

```bash
# 启动Web界面
python app.py

# 启动调度器
python scheduler.py

# 手动更新数据
python exchange_scraper.py
```

## 文件结构

```
exchange_rate_dashboard/
├── app.py                 # Flask Web应用
├── scheduler.py           # 定时任务调度器
├── exchange_scraper.py    # 汇率数据抓取器
├── run.py                 # 启动脚本
├── requirements.txt       # Python依赖
├── exchange_rates.json    # 汇率数据存储文件
├── scheduler.log          # 调度器日志
└── templates/
    └── index.html         # Web界面模板
```

## 数据格式

汇率数据以JSON格式存储在 `exchange_rates.json` 中：

```json
{
  "moneychain": {
    "AUD_CNY": {
      "buy": 4.6909,
      "sell": 4.6909
    }
  },
  "timestamp": "2026-01-23T11:37:40.510953"
}
```

## API接口

- `GET /`: 主页面
- `GET /api/rates`: 获取所有汇率数据
- `GET /api/update`: 手动触发数据更新
- `GET /api/companies`: 获取支持的公司列表

## 注意事项

1. **营业时间**: 系统只在上午10点至下午6点之间自动更新数据
2. **网络连接**: 需要稳定的网络连接才能正常抓取数据
3. **网站变更**: 如果目标网站结构发生变化，可能需要更新爬虫代码
4. **数据准确性**: 显示的数据仅供参考，实际汇率以各公司官网为准

## 故障排除

### 常见问题

1. **编码错误**: 确保系统使用UTF-8编码
2. **网络超时**: 检查网络连接，必要时调整超时时间
3. **网站无法访问**: 某些网站可能有反爬虫措施或暂时不可用

### 日志查看

调度器运行日志保存在 `scheduler.log` 文件中，可以查看详细的运行信息和错误。

## 开发和扩展

### 添加新的换汇公司

在 `ExchangeRateScraper` 类中添加新的抓取方法：

```python
def scrape_new_company(self):
    # 实现新的抓取逻辑
    return rates
```

然后在 `scrape_all_companies` 方法中调用它。

### 修改更新频率

在 `scheduler.py` 中修改 `schedule.every(3).hours.do(...)` 的参数。

## 许可证

本项目仅供学习和个人使用，请遵守相关法律法规。








