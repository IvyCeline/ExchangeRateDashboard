#!/usr/bin/env python3
"""
汇率看板启动脚本
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("澳大利亚换汇公司汇率看板")
    print("=" * 40)

    # 检查当前目录
    current_dir = Path(__file__).parent
    os.chdir(current_dir)

    print(f"工作目录: {current_dir}")

    # 检查必要的文件是否存在
    required_files = [
        'exchange_scraper.py',
        'scheduler.py',
        'app.py',
        'templates/index.html'
    ]

    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)

    if missing_files:
        print("错误: 缺少以下文件:")
        for file in missing_files:
            print(f"  - {file}")
        return 1

    print("所有必要文件都存在 ✓")

    # 提供选项
    print("\n请选择运行模式:")
    print("1. 启动Web界面 (推荐)")
    print("2. 运行调度器 (后台自动更新)")
    print("3. 手动更新汇率数据")
    print("4. 测试爬虫")

    choice = input("\n请输入选择 (1-4): ").strip()

    if choice == '1':
        print("启动Web界面...")
        print("浏览器将自动打开 http://localhost:5000")
        print("按Ctrl+C停止服务器")
        try:
            subprocess.run([sys.executable, 'app.py'], check=True)
        except KeyboardInterrupt:
            print("\nWeb服务器已停止")
        except subprocess.CalledProcessError as e:
            print(f"启动失败: {e}")

    elif choice == '2':
        print("启动调度器...")
        print("调度器将每3小时自动更新汇率数据 (上午10点-下午6点)")
        print("按Ctrl+C停止调度器")
        try:
            subprocess.run([sys.executable, 'scheduler.py'], check=True)
        except KeyboardInterrupt:
            print("\n调度器已停止")
        except subprocess.CalledProcessError as e:
            print(f"启动失败: {e}")

    elif choice == '3':
        print("手动更新汇率数据...")
        try:
            subprocess.run([sys.executable, 'exchange_scraper.py'], check=True)
            print("汇率数据已更新")
        except subprocess.CalledProcessError as e:
            print(f"更新失败: {e}")

    elif choice == '4':
        print("测试爬虫...")
        try:
            result = subprocess.run([sys.executable, '-c',
                "from exchange_scraper import ExchangeRateScraper; "
                "scraper = ExchangeRateScraper(); "
                "rates = scraper.scrape_all_companies(); "
                "print('测试结果:'); "
                "import json; "
                "print(json.dumps(rates, indent=2, ensure_ascii=False, default=str))"
            ], capture_output=True, text=True, encoding='utf-8')
            print(result.stdout)
            if result.stderr:
                print("错误信息:")
                print(result.stderr)
        except Exception as e:
            print(f"测试失败: {e}")

    else:
        print("无效选择")

    return 0

if __name__ == "__main__":
    sys.exit(main())








