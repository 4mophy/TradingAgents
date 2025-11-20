# AkShare 数据源集成指南

## 概述

本项目已集成 AkShare 数据源，用于获取A股、港股、基金和指数数据。AkShare 是一个专注于中国金融数据的开源工具，提供丰富的数据接口。

## 功能特性

### 已实现的功能

1. **股票历史数据** (`get_stock_data`)
   - 支持A股历史行情数据
   - 前复权数据
   - 包含：开盘、收盘、最高、最低、成交量、成交额、振幅、涨跌幅等

2. **基金数据** (`get_fund_data`)
   - 公募基金历史净值数据
   - 日增长率数据

3. **指数数据** (`get_index_data`)
   - A股指数历史数据
   - 支持上证、深证等主要指数

4. **股票实时信息** (`get_stock_info`)
   - 实时行情数据
   - 市盈率、市净率等指标

5. **财务报表** (`get_stock_financial_report`)
   - 利润表数据
   - 其他财务报表

## 配置方法

### 方式一：修改默认配置

编辑 `tradingagents/default_config.py`:

```python
DEFAULT_CONFIG = {
    "data_vendors": {
        "core_stock_apis": "akshare",       # 将 yfinance 改为 akshare
        "technical_indicators": "yfinance",  # 技术指标仍使用 yfinance
        "fundamental_data": "alpha_vantage",
        "news_data": "alpha_vantage",
        "fund_data": "akshare",              # 基金数据使用 akshare
    },
}
```

### 方式二：工具级别配置

如果只想为特定工具使用 akshare，可以在 `tool_vendors` 中配置：

```python
DEFAULT_CONFIG = {
    "tool_vendors": {
        "get_stock_data": "akshare",  # 只有股票数据使用 akshare
    },
}
```

### 方式三：运行时配置

在代码中动态修改配置：

```python
from tradingagents.dataflows.config import get_config

config = get_config()
config["data_vendors"]["core_stock_apis"] = "akshare"
```

## 使用示例

### 1. 获取股票数据

```python
from tradingagents.dataflows.interface import route_to_vendor

# 获取平安银行 (000001) 的历史数据
result = route_to_vendor(
    "get_stock_data",
    symbol="000001",           # 股票代码（6位数字）
    start_date="2024-01-01",   # 开始日期
    end_date="2024-01-31"      # 结束日期
)
print(result)
```

### 2. 获取基金数据

```python
from tradingagents.dataflows.interface import route_to_vendor

# 获取基金净值数据
result = route_to_vendor(
    "get_fund_data",
    symbol="000001",           # 基金代码
    start_date="2024-01-01",
    end_date="2024-01-31"
)
print(result)
```

### 3. 获取指数数据

```python
from tradingagents.dataflows.interface import route_to_vendor

# 获取上证指数数据
result = route_to_vendor(
    "get_index_data",
    symbol="000001",           # 上证指数代码
    start_date="2024-01-01",
    end_date="2024-01-31"
)
print(result)
```

### 4. 直接调用 AkShare 函数

```python
from tradingagents.dataflows.akshare_data import (
    get_stock_data,
    get_fund_data,
    get_index_data,
    get_stock_info
)

# 直接获取股票数据
data = get_stock_data("000001", "2024-01-01", "2024-01-31")
print(data)

# 获取实时信息
info = get_stock_info("000001")
print(info)
```

## 股票代码格式

### A股股票代码
- **深圳股票**: 000001 (平安银行), 000002 (万科A) 等
- **上海股票**: 600000 (浦发银行), 600036 (招商银行) 等
- **创业板**: 300xxx
- **科创板**: 688xxx

### 指数代码
- **上证指数**: 000001
- **深证成指**: 399001
- **创业板指**: 399006
- **科创50**: 000688

### 基金代码
- 6位数字，如: 000001 (华夏成长)

## 数据格式

### 股票数据输出格式 (CSV)

```csv
Date,股票代码,Open,Close,High,Low,Volume,Amount,Amplitude,Change_Pct,Change,Turnover
2024-01-02,000001,7.83,7.65,7.86,7.65,1158366,1075742252.45,2.68,-2.3,-0.18,0.6
2024-01-03,000001,7.63,7.64,7.66,7.59,733610,673673613.54,0.92,-0.13,-0.01,0.38
```

字段说明：
- **Date**: 日期
- **Open**: 开盘价
- **Close**: 收盘价
- **High**: 最高价
- **Low**: 最低价
- **Volume**: 成交量（手）
- **Amount**: 成交额（元）
- **Amplitude**: 振幅（%）
- **Change_Pct**: 涨跌幅（%）
- **Change**: 涨跌额（元）
- **Turnover**: 换手率（%）

### 指数数据输出格式 (CSV)

```csv
Date,Open,High,Low,Close,Volume
2024-01-02,2972.775,2976.268,2962.276,2962.276,30414179300
2024-01-03,2957.112,2971.283,2953.29,2967.247,28545594500
```

## 多数据源 Fallback 机制

系统支持多数据源自动切换，配置示例：

```python
"data_vendors": {
    "core_stock_apis": "akshare,yfinance,alpha_vantage"  # 按优先级排列
}
```

数据获取流程：
1. 首先尝试使用 akshare
2. 如果失败，自动切换到 yfinance
3. 如果仍失败，切换到 alpha_vantage
4. 如果所有数据源都失败，抛出异常

调试信息示例：
```
DEBUG: get_stock_data - Primary: [akshare] | Full fallback order: [akshare → yfinance → alpha_vantage]
DEBUG: Attempting PRIMARY vendor 'akshare' for get_stock_data (attempt #1)
SUCCESS: Vendor 'akshare' succeeded - Got 1 result(s)
```

## 测试

运行测试脚本验证集成：

```bash
# 使用 uv 运行测试
uv run python test_akshare.py

# 或使用 Python 直接运行
python test_akshare.py
```

测试内容包括：
- ✓ 股票历史数据获取
- ✓ 基金数据获取
- ✓ 指数数据获取
- ✓ 股票实时信息
- ✓ Interface 路由测试

## 注意事项

1. **数据延迟**: AkShare 提供的是免费数据，可能存在一定延迟
2. **请求频率**: 建议合理控制请求频率，避免被限流
3. **数据质量**: 数据质量依赖于 AkShare 的上游数据源
4. **日期格式**: 统一使用 `YYYY-MM-DD` 格式
5. **股票代码**: 使用6位数字代码，无需添加市场前缀（如 sh/sz）

## 技术指标计算

AkShare 主要提供原始数据，技术指标计算仍建议使用现有的 `stockstats` 库：

```python
from tradingagents.dataflows.stockstats_utils import StockstatsUtils

# 计算技术指标
indicators = get_stock_stats_indicators_window(
    symbol="000001",
    indicator="close_50_sma",  # 50日均线
    curr_date="2024-01-31",
    look_back_days=100
)
```

支持的指标：
- 移动平均: `close_50_sma`, `close_200_sma`, `close_10_ema`
- MACD: `macd`, `macds`, `macdh`
- RSI: `rsi`
- 布林带: `boll`, `boll_ub`, `boll_lb`
- ATR: `atr`
- 成交量指标: `vwma`, `mfi`

## 相关文件

- **数据获取模块**: `tradingagents/dataflows/akshare_data.py`
- **数据路由**: `tradingagents/dataflows/interface.py`
- **配置文件**: `tradingagents/default_config.py`
- **测试脚本**: `test_akshare.py`

## 常见问题

### Q: 如何同时使用 akshare 和 yfinance？

A: 可以为不同的工具配置不同的数据源：

```python
"data_vendors": {
    "core_stock_apis": "akshare",  # A股使用 akshare
},
"tool_vendors": {
    "get_stock_data": "yfinance",  # 特定工具使用 yfinance（覆盖默认）
}
```

### Q: AkShare 支持美股数据吗？

A: AkShare 主要专注于中国市场数据（A股、港股、基金等），美股数据建议使用 yfinance。

### Q: 如何获取实时数据？

A: 使用 `get_stock_info()` 函数可以获取实时行情数据。

### Q: 数据获取失败怎么办？

A: 系统会自动尝试 fallback 到其他数据源。如果所有数据源都失败，请检查：
1. 网络连接是否正常
2. akshare 库是否正确安装
3. 股票代码是否正确

## 更新日志

- **2025-11-20**: 集成 AkShare 数据源
  - 添加股票、基金、指数数据获取功能
  - 支持多数据源 fallback 机制
  - 完善配置和测试

## 参考资料

- [AkShare 官方文档](https://akshare.akfamily.xyz/)
- [AkShare GitHub](https://github.com/akfamily/akshare)
- [TradingAgents 项目文档](./README.md)
