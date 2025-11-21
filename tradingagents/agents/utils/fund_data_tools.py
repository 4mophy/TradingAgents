from langchain_core.tools import tool
from typing import Annotated
from tradingagents.dataflows.interface import route_to_vendor


@tool
def get_fund_data(
    symbol: Annotated[str, "fund code (基金代码), e.g. 000001"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve fund net value data (基金净值数据) for a given fund code.
    Uses the configured fund_data vendor (typically akshare for Chinese funds).

    Args:
        symbol (str): Fund code (基金代码), e.g. 000001 (华夏成长), 110022 (易方达消费)
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format

    Returns:
        str: A formatted dataframe containing the fund net value data for the specified fund code in the specified date range.
    """
    return route_to_vendor("get_fund_data", symbol, start_date, end_date)


@tool
def get_index_data(
    symbol: Annotated[str, "index code (指数代码), e.g. 000001, 399001"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """
    Retrieve index price data (指数行情数据) for a given index code.
    Uses the configured fund_data vendor (typically akshare for Chinese indices).

    Args:
        symbol (str): Index code (指数代码), e.g. 000001 (上证指数), 399001 (深证成指), 000300 (沪深300)
        start_date (str): Start date in yyyy-mm-dd format
        end_date (str): End date in yyyy-mm-dd format

    Returns:
        str: A formatted dataframe containing the index price data for the specified index code in the specified date range.
    """
    return route_to_vendor("get_index_data", symbol, start_date, end_date)
