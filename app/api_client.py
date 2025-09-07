import requests

BASE_API = "https://api.example.com"  # 替换成真实 REST API

def get_stock_list():
    """获取股票列表"""
    resp = requests.get(f"{BASE_API}/stocks")
    return resp.json()  # 假设返回列表 [{'symbol': 'AAPL', 'name': 'Apple'}, ...]

def get_financial_report(symbol: str, report_type: str):
    """获取财报数据"""
    resp = requests.get(f"{BASE_API}/financials/{symbol}/{report_type}")
    return resp.json()  # 假设返回字典形式
