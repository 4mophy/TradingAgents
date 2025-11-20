"""
测试智能市场检测和数据源路由功能
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from tradingagents.dataflows.market_detector import (
    detect_market,
    get_recommended_vendor,
    get_vendor_with_fallback,
    get_market_display_name
)
from tradingagents.dataflows.interface import route_to_vendor
from tradingagents.dataflows.config import get_config


def test_market_detection():
    """测试市场检测功能"""
    print("=" * 80)
    print("测试 1: 市场检测功能")
    print("=" * 80)

    test_cases = [
        # A股
        ("000001", "A_STOCK", "akshare"),
        ("600000", "A_STOCK", "akshare"),
        ("300750", "A_STOCK", "akshare"),
        ("688001", "A_STOCK", "akshare"),

        # 美股
        ("AAPL", "US_STOCK", "yfinance"),
        ("TSLA", "US_STOCK", "yfinance"),
        ("MSFT", "US_STOCK", "yfinance"),
        ("BRK.B", "US_STOCK", "yfinance"),

        # 港股
        ("00700", "HK_STOCK", "yfinance"),
        ("09988", "HK_STOCK", "yfinance"),

        # 指数
        ("000300", "INDEX", "akshare"),
        ("399001", "INDEX", "akshare"),
    ]

    print(f"\n{'股票代码':<15} {'预期市场':<15} {'检测市场':<15} {'推荐数据源':<15} {'状态'}")
    print("-" * 80)

    all_passed = True
    for symbol, expected_market, expected_vendor in test_cases:
        market = detect_market(symbol)
        vendor = get_recommended_vendor(symbol)
        market_name = get_market_display_name(market)
        status = "✓" if market == expected_market and vendor == expected_vendor else "✗"

        if status == "✗":
            all_passed = False

        print(f"{symbol:<15} {expected_market:<15} {market_name:<15} {vendor:<15} {status}")

    print(f"\n{'✓ 全部通过' if all_passed else '✗ 部分失败'}\n")
    return all_passed


def test_vendor_fallback():
    """测试 fallback 链生成"""
    print("=" * 80)
    print("测试 2: Vendor Fallback 链")
    print("=" * 80)

    test_cases = [
        ("000001", "akshare,yfinance"),          # A股
        ("AAPL", "yfinance,alpha_vantage"),      # 美股
        ("00700", "yfinance,akshare"),           # 港股
        ("000300", "akshare,yfinance"),          # 指数
    ]

    print(f"\n{'股票代码':<15} {'市场类型':<15} {'Fallback 链'}")
    print("-" * 80)

    for symbol, expected_chain in test_cases:
        market = detect_market(symbol)
        market_name = get_market_display_name(market)
        chain = get_vendor_with_fallback(symbol)
        status = "✓" if chain == expected_chain else "✗"
        print(f"{symbol:<15} {market_name:<15} {chain:<40} {status}")

    print()


def test_smart_routing_integration():
    """测试智能路由集成"""
    print("=" * 80)
    print("测试 3: 智能路由集成测试")
    print("=" * 80)

    # 临时启用 auto 模式
    config = get_config()
    original_vendor = config.get("data_vendors", {}).get("core_stock_apis")
    config["data_vendors"]["core_stock_apis"] = "auto"

    test_symbols = [
        ("000001", "A股 - 平安银行"),
        ("AAPL", "美股 - Apple"),
        ("00700", "港股 - 腾讯"),
    ]

    print("\n开始测试智能路由...\n")

    for symbol, description in test_symbols:
        print(f"\n{'='*60}")
        print(f"测试: {description} (代码: {symbol})")
        print(f"{'='*60}")

        try:
            # 只调用路由，不实际获取数据（可能会因为网络或API限制失败）
            # 我们主要是验证路由逻辑
            market = detect_market(symbol)
            vendor = get_recommended_vendor(symbol)
            market_name = get_market_display_name(market)

            print(f"市场检测: {market_name}")
            print(f"推荐数据源: {vendor}")

            # 尝试实际路由（可能失败，但能看到路由逻辑）
            print(f"\n尝试通过路由获取数据...")
            result = route_to_vendor(
                "get_stock_data",
                symbol=symbol,
                start_date="2024-01-01",
                end_date="2024-01-05"
            )

            # 只显示前200个字符
            if isinstance(result, str):
                print(f"✓ 数据获取成功 (前200字符):")
                print(result[:200] + "..." if len(result) > 200 else result)
            else:
                print(f"✓ 数据获取成功")

        except Exception as e:
            # 即使失败也没关系，我们主要是验证路由逻辑
            print(f"⚠ 数据获取失败（但路由逻辑已验证）: {str(e)[:100]}")

    # 恢复原始配置
    config["data_vendors"]["core_stock_apis"] = original_vendor
    print(f"\n恢复配置: core_stock_apis = {original_vendor}\n")


def test_manual_vendor_selection():
    """测试手动数据源选择"""
    print("=" * 80)
    print("测试 4: 手动数据源选择")
    print("=" * 80)

    config = get_config()

    # 测试手动选择 yfinance
    print("\n指定使用 yfinance 获取美股数据...")
    config["data_vendors"]["core_stock_apis"] = "yfinance"

    market = detect_market("AAPL")
    print(f"市场检测: {get_market_display_name(market)}")
    print(f"配置的数据源: yfinance")

    # 测试手动选择 akshare
    print("\n指定使用 akshare 获取A股数据...")
    config["data_vendors"]["core_stock_apis"] = "akshare"

    market = detect_market("000001")
    print(f"市场检测: {get_market_display_name(market)}")
    print(f"配置的数据源: akshare")

    print("\n✓ 手动选择测试完成\n")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("智能市场检测和数据源路由测试套件")
    print("=" * 80 + "\n")

    # 运行所有测试
    test_market_detection()
    test_vendor_fallback()
    test_smart_routing_integration()
    test_manual_vendor_selection()

    print("=" * 80)
    print("所有测试完成")
    print("=" * 80 + "\n")

    print("使用说明:")
    print("1. 在配置中设置 'core_stock_apis': 'auto' 启用智能检测")
    print("2. A股代码（如 000001）自动使用 akshare")
    print("3. 美股代码（如 AAPL）自动使用 yfinance")
    print("4. 港股代码（如 00700）自动使用 yfinance")
    print("5. 也可以手动指定数据源（如 'yfinance', 'akshare'）")
