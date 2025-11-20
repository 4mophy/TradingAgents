"""
测试 AkShare 数据获取功能
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from tradingagents.dataflows.akshare_data import (
    get_stock_data,
    get_fund_data,
    get_stock_info,
    get_index_data
)


def test_stock_data():
    """测试股票数据获取"""
    print("=" * 60)
    print("测试 1: 获取平安银行 (000001) 股票数据")
    print("=" * 60)
    try:
        result = get_stock_data(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-10"
        )
        print(result[:500])  # 只打印前500个字符
        print("✓ 股票数据获取成功\n")
    except Exception as e:
        print(f"✗ 股票数据获取失败: {e}\n")


def test_fund_data():
    """测试基金数据获取"""
    print("=" * 60)
    print("测试 2: 获取华夏成长 (000001) 基金数据")
    print("=" * 60)
    try:
        result = get_fund_data(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-10"
        )
        print(result[:500])  # 只打印前500个字符
        print("✓ 基金数据获取成功\n")
    except Exception as e:
        print(f"✗ 基金数据获取失败: {e}\n")


def test_stock_info():
    """测试股票实时信息"""
    print("=" * 60)
    print("测试 3: 获取平安银行 (000001) 实时信息")
    print("=" * 60)
    try:
        result = get_stock_info(symbol="000001")
        print(result)
        print("✓ 股票信息获取成功\n")
    except Exception as e:
        print(f"✗ 股票信息获取失败: {e}\n")


def test_index_data():
    """测试指数数据获取"""
    print("=" * 60)
    print("测试 4: 获取上证指数 (000001) 数据")
    print("=" * 60)
    try:
        result = get_index_data(
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-10"
        )
        print(result[:500])  # 只打印前500个字符
        print("✓ 指数数据获取成功\n")
    except Exception as e:
        print(f"✗ 指数数据获取失败: {e}\n")


def test_interface_integration():
    """测试通过 interface 路由调用"""
    print("=" * 60)
    print("测试 5: 通过 interface 路由获取股票数据")
    print("=" * 60)
    try:
        from tradingagents.dataflows.interface import route_to_vendor
        from tradingagents.default_config import DEFAULT_CONFIG
        from tradingagents.dataflows.config import get_config

        # 临时修改配置使用 akshare
        config = get_config()
        original_vendor = config.get("data_vendors", {}).get("core_stock_apis")
        config["data_vendors"]["core_stock_apis"] = "akshare"

        result = route_to_vendor(
            "get_stock_data",
            symbol="000001",
            start_date="2024-01-01",
            end_date="2024-01-05"
        )

        # 恢复原始配置
        config["data_vendors"]["core_stock_apis"] = original_vendor

        print(result[:500])
        print("✓ Interface 路由测试成功\n")
    except Exception as e:
        print(f"✗ Interface 路由测试失败: {e}\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("AkShare 数据获取功能测试")
    print("=" * 60 + "\n")

    # 检查 akshare 是否安装
    try:
        import akshare
        print(f"✓ AkShare 版本: {akshare.__version__}\n")
    except ImportError:
        print("✗ AkShare 未安装，请运行: pip install akshare\n")
        sys.exit(1)

    # 运行测试
    test_stock_data()
    test_fund_data()
    test_stock_info()
    test_index_data()
    test_interface_integration()

    print("=" * 60)
    print("测试完成")
    print("=" * 60)
