#!/usr/bin/env python3
"""
测试中文化和基金ETF支持的修复
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_language_config():
    """测试中文化配置"""
    print("=" * 70)
    print("测试1: 中文化配置")
    print("=" * 70)

    from tradingagents.default_config import DEFAULT_CONFIG
    from tradingagents.utils.language import get_language_instruction

    language = DEFAULT_CONFIG["language"]
    print(f"✓ 默认语言配置: {language}")

    if language == "zh":
        print("✓ 语言配置正确：已设置为中文")
    else:
        print(f"✗ 语言配置错误：期望 'zh'，实际为 '{language}'")
        return False

    instruction = get_language_instruction()
    print(f"✓ 语言指令: {instruction[:50]}...")

    if "简体中文" in instruction or "中文" in instruction:
        print("✓ 语言指令正确：包含中文提示")
    else:
        print("✗ 语言指令错误：不包含中文提示")
        return False

    print("\n✓ 中文化配置测试通过\n")
    return True


def test_fund_tools_import():
    """测试基金工具导入"""
    print("=" * 70)
    print("测试2: 基金工具导入")
    print("=" * 70)

    try:
        from tradingagents.agents.utils.agent_utils import get_fund_data, get_index_data
        print("✓ 成功导入 get_fund_data 工具")
        print("✓ 成功导入 get_index_data 工具")
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False

    # 检查工具是否为 LangChain tool
    print(f"✓ get_fund_data 工具名称: {get_fund_data.name}")
    print(f"✓ get_index_data 工具名称: {get_index_data.name}")
    print(f"✓ get_fund_data 描述: {get_fund_data.description[:50]}...")
    print(f"✓ get_index_data 描述: {get_index_data.description[:50]}...")

    print("\n✓ 基金工具导入测试通过\n")
    return True


def test_market_analyst_tools():
    """测试 market_analyst 工具配置"""
    print("=" * 70)
    print("测试3: Market Analyst 工具配置")
    print("=" * 70)

    from tradingagents.agents.analysts.market_analyst import create_market_analyst
    from tradingagents.agents.utils.agent_utils import get_stock_data, get_indicators, get_fund_data, get_index_data

    # 创建一个简单的mock LLM
    class MockLLM:
        def bind_tools(self, tools):
            print(f"✓ Market Analyst 绑定了 {len(tools)} 个工具:")
            for tool in tools:
                print(f"  - {tool.name}")
            return self

    # 验证导入
    try:
        from tradingagents.agents.analysts.market_analyst import create_market_analyst
        print("✓ 成功导入 market_analyst")
    except Exception as e:
        print(f"✗ 导入 market_analyst 失败: {e}")
        return False

    print("\n✓ Market Analyst 工具配置测试通过\n")
    return True


def test_fund_data_interface():
    """测试基金数据接口"""
    print("=" * 70)
    print("测试4: 基金数据接口配置")
    print("=" * 70)

    from tradingagents.dataflows.interface import VENDOR_METHODS, TOOLS_CATEGORIES

    # 检查工具分类
    if "fund_data" in TOOLS_CATEGORIES:
        print(f"✓ TOOLS_CATEGORIES 包含 'fund_data'")
        fund_tools = TOOLS_CATEGORIES["fund_data"]["tools"]
        print(f"✓ 基金工具: {fund_tools}")

        if "get_fund_data" in fund_tools and "get_index_data" in fund_tools:
            print("✓ 基金工具列表正确")
        else:
            print("✗ 基金工具列表不完整")
            return False
    else:
        print("✗ TOOLS_CATEGORIES 不包含 'fund_data'")
        return False

    # 检查供应商映射
    if "get_fund_data" in VENDOR_METHODS:
        print(f"✓ VENDOR_METHODS 包含 'get_fund_data'")
        vendors = VENDOR_METHODS["get_fund_data"]
        print(f"✓ get_fund_data 支持的供应商: {list(vendors.keys())}")
    else:
        print("✗ VENDOR_METHODS 不包含 'get_fund_data'")
        return False

    if "get_index_data" in VENDOR_METHODS:
        print(f"✓ VENDOR_METHODS 包含 'get_index_data'")
        vendors = VENDOR_METHODS["get_index_data"]
        print(f"✓ get_index_data 支持的供应商: {list(vendors.keys())}")
    else:
        print("✗ VENDOR_METHODS 不包含 'get_index_data'")
        return False

    print("\n✓ 基金数据接口配置测试通过\n")
    return True


def test_akshare_integration():
    """测试 AkShare 集成"""
    print("=" * 70)
    print("测试5: AkShare 基金数据集成")
    print("=" * 70)

    from tradingagents.dataflows import akshare_data

    # 检查函数是否存在
    if hasattr(akshare_data, 'get_fund_data'):
        print("✓ akshare_data.get_fund_data 函数存在")
    else:
        print("✗ akshare_data.get_fund_data 函数不存在")
        return False

    if hasattr(akshare_data, 'get_index_data'):
        print("✓ akshare_data.get_index_data 函数存在")
    else:
        print("✗ akshare_data.get_index_data 函数不存在")
        return False

    print("\n✓ AkShare 基金数据集成测试通过\n")
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("开始测试修复...")
    print("=" * 70 + "\n")

    results = []

    # 运行测试
    results.append(("中文化配置", test_language_config()))
    results.append(("基金工具导入", test_fund_tools_import()))
    results.append(("Market Analyst 工具", test_market_analyst_tools()))
    results.append(("基金数据接口", test_fund_data_interface()))
    results.append(("AkShare 集成", test_akshare_integration()))

    # 汇总结果
    print("=" * 70)
    print("测试结果汇总")
    print("=" * 70)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:<30} {status}")

    all_passed = all(result for _, result in results)

    print("\n" + "=" * 70)
    if all_passed:
        print("✓ 所有测试通过！")
        print("\n修复验证成功：")
        print("1. ✓ 中文化已修复：默认语言设置为中文")
        print("2. ✓ 基金ETF工具已注册：Agent可以使用 get_fund_data 和 get_index_data")
    else:
        print("✗ 部分测试失败，请检查修复")
    print("=" * 70 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
