"""
AkShare 数据获取模块
支持A股、港股、基金等数据获取
"""
from typing import Annotated
from datetime import datetime
import pandas as pd

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("WARNING: akshare is not installed. Please install it with: pip install akshare")


def get_stock_data(
    symbol: Annotated[str, "股票代码，如 '000001' (平安银行) 或 '600000' (浦发银行)"],
    start_date: Annotated[str, "开始日期，格式: YYYY-MM-DD"],
    end_date: Annotated[str, "结束日期，格式: YYYY-MM-DD"],
) -> str:
    """
    获取A股历史行情数据

    参数:
        symbol: 股票代码（6位数字）
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)

    返回:
        CSV格式的股票数据字符串，包含：日期、开盘、收盘、最高、最低、成交量、成交额、振幅、涨跌幅等
    """
    if not AKSHARE_AVAILABLE:
        raise ImportError("akshare is not installed")

    # 验证日期格式
    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")

    try:
        # 使用 akshare 获取股票历史数据
        # stock_zh_a_hist: 获取A股历史行情数据（前复权）
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",  # 日线数据
            start_date=start_date.replace("-", ""),  # akshare 需要 YYYYMMDD 格式
            end_date=end_date.replace("-", ""),
            adjust="qfq"  # 前复权
        )

        if df.empty:
            return f"未找到股票代码 '{symbol}' 在 {start_date} 到 {end_date} 之间的数据"

        # 重命名列以符合标准格式
        column_mapping = {
            '日期': 'Date',
            '开盘': 'Open',
            '收盘': 'Close',
            '最高': 'High',
            '最低': 'Low',
            '成交量': 'Volume',
            '成交额': 'Amount',
            '振幅': 'Amplitude',
            '涨跌幅': 'Change_Pct',
            '涨跌额': 'Change',
            '换手率': 'Turnover'
        }

        df = df.rename(columns=column_mapping)

        # 设置日期为索引
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')

        # 数值列保留2位小数
        numeric_columns = ['Open', 'High', 'Low', 'Close']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].round(2)

        # 转换为CSV字符串
        csv_string = df.to_csv()

        # 添加头部信息
        header = f"# 股票 {symbol} 从 {start_date} 到 {end_date} 的历史数据 (AkShare)\n"
        header += f"# 总记录数: {len(df)}\n"
        header += f"# 数据获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f"# 复权方式: 前复权 (qfq)\n\n"

        return header + csv_string

    except Exception as e:
        return f"获取股票 {symbol} 数据时出错: {str(e)}"


def get_fund_data(
    symbol: Annotated[str, "基金代码，如 '000001' (华夏成长)"],
    start_date: Annotated[str, "开始日期，格式: YYYY-MM-DD"],
    end_date: Annotated[str, "结束日期，格式: YYYY-MM-DD"],
) -> str:
    """
    获取公募基金历史净值数据

    参数:
        symbol: 基金代码（6位数字）
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)

    返回:
        CSV格式的基金净值数据字符串
    """
    if not AKSHARE_AVAILABLE:
        raise ImportError("akshare is not installed")

    # 验证日期格式
    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")

    try:
        # 获取基金历史净值数据
        df = ak.fund_open_fund_info_em(fund=symbol, indicator="单位净值走势")

        if df.empty:
            return f"未找到基金代码 '{symbol}' 的数据"

        # 重命名列
        column_mapping = {
            '净值日期': 'Date',
            '单位净值': 'NAV',
            '日增长率': 'Daily_Return'
        }

        # 只保留需要的列
        df = df.rename(columns=column_mapping)

        # 转换日期格式
        df['Date'] = pd.to_datetime(df['Date'])

        # 过滤日期范围
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        df = df[(df['Date'] >= start) & (df['Date'] <= end)]

        if df.empty:
            return f"未找到基金 '{symbol}' 在 {start_date} 到 {end_date} 之间的数据"

        # 设置日期为索引
        df = df.set_index('Date')

        # 转换为CSV字符串
        csv_string = df.to_csv()

        # 添加头部信息
        header = f"# 基金 {symbol} 从 {start_date} 到 {end_date} 的净值数据 (AkShare)\n"
        header += f"# 总记录数: {len(df)}\n"
        header += f"# 数据获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        return header + csv_string

    except Exception as e:
        return f"获取基金 {symbol} 数据时出错: {str(e)}"


def get_stock_info(
    symbol: Annotated[str, "股票代码"]
) -> str:
    """
    获取股票基本信息

    参数:
        symbol: 股票代码

    返回:
        股票基本信息的文本描述
    """
    if not AKSHARE_AVAILABLE:
        raise ImportError("akshare is not installed")

    try:
        # 获取实时行情数据
        df = ak.stock_zh_a_spot_em()

        # 筛选指定股票
        stock_info = df[df['代码'] == symbol]

        if stock_info.empty:
            return f"未找到股票代码 '{symbol}' 的信息"

        # 转换为易读格式
        info = stock_info.iloc[0]
        result = f"# 股票 {symbol} 实时信息\n\n"
        result += f"名称: {info.get('名称', 'N/A')}\n"
        result += f"最新价: {info.get('最新价', 'N/A')}\n"
        result += f"涨跌幅: {info.get('涨跌幅', 'N/A')}%\n"
        result += f"涨跌额: {info.get('涨跌额', 'N/A')}\n"
        result += f"成交量: {info.get('成交量', 'N/A')}\n"
        result += f"成交额: {info.get('成交额', 'N/A')}\n"
        result += f"振幅: {info.get('振幅', 'N/A')}%\n"
        result += f"换手率: {info.get('换手率', 'N/A')}%\n"
        result += f"市盈率: {info.get('市盈率-动态', 'N/A')}\n"
        result += f"市净率: {info.get('市净率', 'N/A')}\n"

        return result

    except Exception as e:
        return f"获取股票 {symbol} 信息时出错: {str(e)}"


def get_stock_financial_report(
    symbol: Annotated[str, "股票代码"],
) -> str:
    """
    获取股票财务报表数据

    参数:
        symbol: 股票代码

    返回:
        CSV格式的财务报表数据
    """
    if not AKSHARE_AVAILABLE:
        raise ImportError("akshare is not installed")

    try:
        # 获取利润表
        df_income = ak.stock_financial_report_sina(stock=symbol, symbol="利润表")

        if df_income.empty:
            return f"未找到股票 '{symbol}' 的财务报表数据"

        # 转换为CSV
        csv_string = df_income.to_csv(index=False)

        header = f"# 股票 {symbol} 利润表数据 (AkShare)\n"
        header += f"# 数据获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        return header + csv_string

    except Exception as e:
        return f"获取股票 {symbol} 财务报表时出错: {str(e)}"


def get_index_data(
    symbol: Annotated[str, "指数代码，如 '000001' (上证指数), '399001' (深证成指)"],
    start_date: Annotated[str, "开始日期，格式: YYYY-MM-DD"],
    end_date: Annotated[str, "结束日期，格式: YYYY-MM-DD"],
) -> str:
    """
    获取A股指数历史数据

    参数:
        symbol: 指数代码
        start_date: 开始日期
        end_date: 结束日期

    返回:
        CSV格式的指数数据
    """
    if not AKSHARE_AVAILABLE:
        raise ImportError("akshare is not installed")

    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")

    try:
        # 获取指数数据
        df = ak.stock_zh_index_daily(symbol=f"sh{symbol}")

        if df.empty:
            # 尝试深圳指数
            df = ak.stock_zh_index_daily(symbol=f"sz{symbol}")

        if df.empty:
            return f"未找到指数 '{symbol}' 的数据"

        # 转换日期
        df['date'] = pd.to_datetime(df['date'])

        # 过滤日期范围
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        df = df[(df['date'] >= start) & (df['date'] <= end)]

        if df.empty:
            return f"未找到指数 '{symbol}' 在 {start_date} 到 {end_date} 之间的数据"

        # 重命名列
        df = df.rename(columns={
            'date': 'Date',
            'open': 'Open',
            'close': 'Close',
            'high': 'High',
            'low': 'Low',
            'volume': 'Volume'
        })

        df = df.set_index('Date')

        csv_string = df.to_csv()

        header = f"# 指数 {symbol} 从 {start_date} 到 {end_date} 的历史数据 (AkShare)\n"
        header += f"# 总记录数: {len(df)}\n"
        header += f"# 数据获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        return header + csv_string

    except Exception as e:
        return f"获取指数 {symbol} 数据时出错: {str(e)}"


# 为了兼容现有系统，提供别名
get_YFin_data_online = get_stock_data  # 股票数据的别名
