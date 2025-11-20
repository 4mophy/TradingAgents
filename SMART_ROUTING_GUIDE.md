# 智能市场检测和数据源路由指南

## 概述

TradingAgents 现在支持**智能市场检测**功能，能够根据股票代码格式自动识别所属市场（A股、美股、港股），并智能选择最合适的数据源。

## 核心功能

### 1. 自动市场检测

系统会根据股票代码格式自动识别市场类型：

| 市场类型 | 代码格式 | 示例 | 推荐数据源 |
|---------|---------|------|-----------|
| **A股** | 6位数字（000xxx, 600xxx, 300xxx, 688xxx） | 000001, 600000, 300750 | akshare |
| **美股** | 1-5个字母 | AAPL, TSLA, MSFT | yfinance |
| **港股** | 5位数字或 .HK 后缀 | 00700, 09988 | yfinance |
| **指数** | 特定代码（000xxx, 399xxx） | 000001, 399001 | akshare |

### 2. 智能数据源选择

启用智能路由后，系统会：

1. **自动检测**股票代码所属市场
2. **智能选择**最适合的数据源
3. **自动 Fallback** 到备用数据源（如果主数据源失败）
4. **优化性能**：第一个数据源成功后立即返回（不再尝试其他数据源）

## 使用方法

### 方式一：启用智能路由（推荐）⭐

在 `tradingagents/default_config.py` 中设置：

```python
DEFAULT_CONFIG = {
    "data_vendors": {
        "core_stock_apis": "auto",  # 启用智能检测
    },
}
```

**效果：**
```python
from tradingagents.dataflows.interface import route_to_vendor

# A股 - 自动使用 akshare
result = route_to_vendor("get_stock_data", symbol="000001",
                        start_date="2024-01-01", end_date="2024-01-31")
# SMART_ROUTING: Detected '000001' as A股市场, using vendor chain: akshare,yfinance
# ✓ 使用 akshare 获取数据

# 美股 - 自动使用 yfinance
result = route_to_vendor("get_stock_data", symbol="AAPL",
                        start_date="2024-01-01", end_date="2024-01-31")
# SMART_ROUTING: Detected 'AAPL' as 美股市场, using vendor chain: yfinance,alpha_vantage
# ✓ 使用 yfinance 获取数据

# 港股 - 自动使用 yfinance
result = route_to_vendor("get_stock_data", symbol="00700",
                        start_date="2024-01-01", end_date="2024-01-31")
# SMART_ROUTING: Detected '00700' as 港股市场, using vendor chain: yfinance,akshare
# ✓ 使用 yfinance 获取数据
```

### 方式二：手动指定数据源

如果你只交易特定市场，可以手动指定数据源：

```python
# 只交易A股，使用 akshare
"core_stock_apis": "akshare"

# 只交易美股，使用 yfinance
"core_stock_apis": "yfinance"

# 多数据源 fallback（按优先级）
"core_stock_apis": "yfinance,akshare,alpha_vantage"
```

### 方式三：运行时动态切换

```python
from tradingagents.dataflows.config import get_config

config = get_config()

# 启用智能路由
config["data_vendors"]["core_stock_apis"] = "auto"

# 或手动指定
config["data_vendors"]["core_stock_apis"] = "akshare"
```

## 智能路由逻辑

### 市场检测规则

```python
from tradingagents.dataflows.market_detector import detect_market, get_market_display_name

# A股检测
market = detect_market("000001")  # 返回 "A_STOCK"
print(get_market_display_name(market))  # 输出: "A股市场"

# 美股检测
market = detect_market("AAPL")  # 返回 "US_STOCK"
print(get_market_display_name(market))  # 输出: "美股市场"

# 港股检测
market = detect_market("00700")  # 返回 "HK_STOCK"
print(get_market_display_name(market))  # 输出: "港股市场"
```

### 数据源 Fallback 链

智能路由会为每个市场生成最优的 fallback 链：

| 市场 | Fallback 链 | 说明 |
|-----|------------|------|
| A股 | `akshare → yfinance` | 优先 akshare（专业A股数据），失败则用 yfinance |
| 美股 | `yfinance → alpha_vantage` | 优先 yfinance（免费），失败则用 alpha_vantage |
| 港股 | `yfinance → akshare` | 优先 yfinance（国际数据），失败则用 akshare |
| 指数 | `akshare → yfinance` | 优先 akshare（中国指数专业数据） |

### 优化逻辑

**智能路由模式下的性能优化：**

- ✅ **第一个成功立即返回**：一旦第一个数据源成功获取数据，立即停止，不再尝试其他数据源
- ✅ **失败时自动 Fallback**：如果第一个数据源失败，自动尝试下一个
- ✅ **调试信息完整**：显示检测到的市场类型和使用的数据源链

**日志示例：**

```
SMART_ROUTING: Detected '000001' as A股市场, using vendor chain: akshare,yfinance
DEBUG: get_stock_data - Primary: [akshare → yfinance] | Full fallback order: [akshare → yfinance → alpha_vantage → local]
DEBUG: Attempting PRIMARY vendor 'akshare' for get_stock_data (attempt #1)
SUCCESS: Vendor 'akshare' succeeded - Got 1 result(s)
DEBUG: Stopping after successful vendor 'akshare' (smart routing mode)
FINAL: Method 'get_stock_data' completed with 1 result(s) from 1 vendor attempt(s)
```

## 代码示例

### 示例 1: 混合市场交易

```python
from tradingagents.dataflows.interface import route_to_vendor
from tradingagents.dataflows.config import get_config

# 启用智能路由
config = get_config()
config["data_vendors"]["core_stock_apis"] = "auto"

# 获取多个市场的数据
stocks = [
    ("000001", "2024-01-01", "2024-01-31"),  # A股
    ("AAPL", "2024-01-01", "2024-01-31"),    # 美股
    ("00700", "2024-01-01", "2024-01-31"),   # 港股
]

for symbol, start, end in stocks:
    data = route_to_vendor(
        "get_stock_data",
        symbol=symbol,
        start_date=start,
        end_date=end
    )
    print(f"获取 {symbol} 数据成功！")
    # 系统会自动为每个代码选择最佳数据源
```

### 示例 2: 直接使用市场检测器

```python
from tradingagents.dataflows.market_detector import (
    detect_market,
    get_recommended_vendor,
    get_vendor_with_fallback,
    get_market_display_name
)

symbol = "000001"

# 检测市场
market = detect_market(symbol)
print(f"市场类型: {get_market_display_name(market)}")  # A股市场

# 获取推荐数据源
vendor = get_recommended_vendor(symbol)
print(f"推荐数据源: {vendor}")  # akshare

# 获取 fallback 链
fallback = get_vendor_with_fallback(symbol)
print(f"Fallback 链: {fallback}")  # akshare,yfinance
```

### 示例 3: 批量检测

```python
from tradingagents.dataflows.market_detector import detect_market, get_recommended_vendor

symbols = ["000001", "600000", "AAPL", "TSLA", "00700", "09988"]

for symbol in symbols:
    market = detect_market(symbol)
    vendor = get_recommended_vendor(symbol)
    print(f"{symbol:10} → {market:15} → {vendor}")

# 输出:
# 000001     → A_STOCK        → akshare
# 600000     → A_STOCK        → akshare
# AAPL       → US_STOCK       → yfinance
# TSLA       → US_STOCK       → yfinance
# 00700      → HK_STOCK       → yfinance
# 09988      → HK_STOCK       → yfinance
```

## 测试

运行测试脚本验证功能：

```bash
# 测试市场检测和智能路由
uv run python test_smart_routing.py

# 测试 akshare 集成
uv run python test_akshare.py
```

## 配置对比

### 配置 1: 智能路由（推荐）⭐

```python
"data_vendors": {
    "core_stock_apis": "auto",
}
```

**优点：**
- ✅ 自动适配所有市场
- ✅ 最优数据源选择
- ✅ 无需手动切换
- ✅ 适合混合市场交易

**缺点：**
- ⚠️ 需要安装多个数据源库（akshare, yfinance）

### 配置 2: 固定单一数据源

```python
"data_vendors": {
    "core_stock_apis": "akshare",  # 或 "yfinance"
}
```

**优点：**
- ✅ 配置简单
- ✅ 只需安装一个库

**缺点：**
- ❌ 只能支持特定市场（如 akshare 只支持中国市场）
- ❌ 跨市场交易需要手动切换

### 配置 3: 多数据源 Fallback

```python
"data_vendors": {
    "core_stock_apis": "yfinance,akshare,alpha_vantage",
}
```

**优点：**
- ✅ 高可靠性（多重备份）
- ✅ 支持所有市场

**缺点：**
- ❌ 不会智能选择最佳数据源
- ❌ 可能使用不适合的数据源（如用 yfinance 获取A股）

## 常见问题

### Q1: 智能路由支持哪些市场？

**A:** 目前支持：
- ✅ A股（沪深主板、创业板、科创板）
- ✅ 美股（纳斯达克、纽交所）
- ✅ 港股
- ✅ 中国指数（上证、深证等）

### Q2: 如何知道系统使用了哪个数据源？

**A:** 启用智能路由后，系统会输出详细日志：

```
SMART_ROUTING: Detected '000001' as A股市场, using vendor chain: akshare,yfinance
DEBUG: Attempting PRIMARY vendor 'akshare' for get_stock_data (attempt #1)
SUCCESS: Vendor 'akshare' succeeded - Got 1 result(s)
```

### Q3: 如果主数据源失败会怎样？

**A:** 系统会自动 fallback 到备用数据源：

```
DEBUG: Attempting PRIMARY vendor 'akshare' for get_stock_data (attempt #1)
FAILED: akshare failed: Network error
DEBUG: Attempting FALLBACK vendor 'yfinance' for get_stock_data (attempt #2)
SUCCESS: Vendor 'yfinance' succeeded - Got 1 result(s)
```

### Q4: 可以强制使用特定数据源吗？

**A:** 可以，有两种方式：

**方式1：全局配置**
```python
config["data_vendors"]["core_stock_apis"] = "akshare"
```

**方式2：工具级别配置**
```python
config["tool_vendors"]["get_stock_data"] = "yfinance"
```

### Q5: 智能路由会影响性能吗？

**A:** 不会，反而更快！
- 智能路由在第一个数据源成功后立即返回
- 减少了不必要的数据源尝试
- 避免了使用不适合的数据源（如用 yfinance 获取A股可能失败或数据不全）

### Q6: 技术指标也支持智能路由吗？

**A:** 目前智能路由只支持 `get_stock_data`，技术指标仍使用配置的数据源。

### Q7: 如何添加自定义市场检测规则？

**A:** 编辑 `tradingagents/dataflows/market_detector.py`，修改 `detect_market()` 函数：

```python
def detect_market(symbol: str) -> MarketType:
    symbol = symbol.strip().upper()

    # 添加你的自定义规则
    if symbol.startswith("MY_PREFIX"):
        return "MY_CUSTOM_MARKET"

    # ... 现有规则 ...
```

## 相关文件

- **市场检测器**: `tradingagents/dataflows/market_detector.py`
- **数据路由**: `tradingagents/dataflows/interface.py`
- **AkShare 集成**: `tradingagents/dataflows/akshare_data.py`
- **配置文件**: `tradingagents/default_config.py`
- **测试脚本**: `test_smart_routing.py`, `test_akshare.py`

## 总结

智能市场检测功能让 TradingAgents 能够：

✅ **自动识别**股票代码所属市场（A股、美股、港股）
✅ **智能选择**最适合的数据源
✅ **自动 Fallback**确保数据获取成功
✅ **优化性能**第一个成功立即返回
✅ **简化配置**一个 `"auto"` 配置适配所有市场

**推荐配置：**
```python
"data_vendors": {
    "core_stock_apis": "auto",  # 启用智能路由，支持所有市场
}
```

Happy Trading! 🚀
