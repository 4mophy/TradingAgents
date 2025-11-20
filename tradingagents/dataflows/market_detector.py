"""
市场和股票代码检测器
根据股票代码格式自动识别所属市场，并推荐最佳数据源
"""
import re
from typing import Literal, Optional

MarketType = Literal["A_STOCK", "US_STOCK", "HK_STOCK", "INDEX", "UNKNOWN"]


def detect_market(symbol: str) -> MarketType:
    """
    根据股票代码格式检测所属市场

    参数:
        symbol: 股票代码

    返回:
        市场类型: A_STOCK, US_STOCK, HK_STOCK, INDEX, UNKNOWN
    """
    symbol = symbol.strip().upper()

    # A股代码模式
    # 沪市: 600xxx, 601xxx, 603xxx, 605xxx (主板)
    # 深市: 000xxx (主板), 001xxx (主板), 002xxx (中小板), 003xxx (主板)
    # 创业板: 300xxx
    # 科创板: 688xxx
    if re.match(r'^(000|001|002|003|300|600|601|603|605|688)\d{3}$', symbol):
        return "A_STOCK"

    # 纯6位数字也可能是A股
    if re.match(r'^\d{6}$', symbol):
        return "A_STOCK"

    # 港股代码模式
    # 格式: 5位数字 或 5位数字.HK
    if re.match(r'^\d{5}(\.HK)?$', symbol):
        return "HK_STOCK"

    # 美股代码模式
    # 一般是1-5个字母
    if re.match(r'^[A-Z]{1,5}$', symbol):
        return "US_STOCK"

    # 美股代码可能带后缀 (如 BRK.B, BRK.A)
    if re.match(r'^[A-Z]{1,5}\.[A-Z]$', symbol):
        return "US_STOCK"

    # A股指数代码
    # 上证指数: 000001, 上证50: 000016, 沪深300: 000300
    # 深证成指: 399001, 创业板指: 399006
    if re.match(r'^(000|399)\d{3}$', symbol):
        # 这些可能是指数或A股股票，需要上下文判断
        # 常见指数代码
        common_indices = ['000001', '000016', '000300', '000688', '000905',
                         '399001', '399006', '399106', '399305']
        if symbol in common_indices:
            return "INDEX"
        return "A_STOCK"

    return "UNKNOWN"


def get_recommended_vendor(symbol: str) -> str:
    """
    根据股票代码推荐最佳数据源

    参数:
        symbol: 股票代码

    返回:
        推荐的数据源名称
    """
    market = detect_market(symbol)

    recommendations = {
        "A_STOCK": "akshare",      # A股优先使用 akshare
        "US_STOCK": "yfinance",    # 美股优先使用 yfinance
        "HK_STOCK": "yfinance",    # 港股 yfinance 和 akshare 都支持，优先 yfinance
        "INDEX": "akshare",        # 中国指数优先使用 akshare
        "UNKNOWN": "yfinance",     # 未知类型默认 yfinance（兼容性最好）
    }

    return recommendations[market]


def get_vendor_with_fallback(symbol: str) -> str:
    """
    获取推荐数据源及 fallback 列表（逗号分隔）

    参数:
        symbol: 股票代码

    返回:
        数据源列表字符串，如 "akshare,yfinance"
    """
    market = detect_market(symbol)

    fallback_chains = {
        "A_STOCK": "akshare,yfinance",      # A股: akshare -> yfinance
        "US_STOCK": "yfinance,alpha_vantage",  # 美股: yfinance -> alpha_vantage
        "HK_STOCK": "yfinance,akshare",     # 港股: yfinance -> akshare
        "INDEX": "akshare,yfinance",        # 指数: akshare -> yfinance
        "UNKNOWN": "yfinance,akshare,alpha_vantage",  # 未知: 全部尝试
    }

    return fallback_chains[market]


def get_market_display_name(market: MarketType) -> str:
    """
    获取市场类型的显示名称

    参数:
        market: 市场类型

    返回:
        市场显示名称
    """
    display_names = {
        "A_STOCK": "A股市场",
        "US_STOCK": "美股市场",
        "HK_STOCK": "港股市场",
        "INDEX": "指数",
        "UNKNOWN": "未知市场"
    }

    return display_names.get(market, "未知")


# 示例和测试
if __name__ == "__main__":
    test_symbols = [
        # A股
        "000001", "600000", "300750", "688001",
        # 美股
        "AAPL", "TSLA", "MSFT", "BRK.B",
        # 港股
        "00700", "00700.HK", "09988",
        # 指数
        "000300", "399001",
    ]

    print("股票代码市场检测测试:\n")
    print(f"{'代码':<15} {'市场类型':<15} {'推荐数据源':<15} {'Fallback链'}")
    print("-" * 70)

    for symbol in test_symbols:
        market = detect_market(symbol)
        vendor = get_recommended_vendor(symbol)
        fallback = get_vendor_with_fallback(symbol)
        market_name = get_market_display_name(market)
        print(f"{symbol:<15} {market_name:<15} {vendor:<15} {fallback}")
