from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_stock_data, get_indicators, get_fund_data, get_index_data
from tradingagents.dataflows.config import get_config
from tradingagents.utils.language import get_language_instruction


def create_market_analyst(llm):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        tools = [
            get_stock_data,
            get_indicators,
            get_fund_data,
            get_index_data,
        ]

        system_message = (
            """你是一名交易助手，负责分析金融市场。你的角色是从以下列表中为给定的市场条件或交易策略选择**最相关的指标**。目标是选择最多 **8 个指标**，这些指标提供互补的见解而不冗余。类别和每个类别的指标如下：

移动平均线 (Moving Averages)：
- close_50_sma: 50 SMA：中期趋势指标。用途：识别趋势方向并作为动态支撑/阻力。提示：它滞后于价格；结合更快的指标以获得及时信号。
- close_200_sma: 200 SMA：长期趋势基准。用途：确认整体市场趋势并识别金叉/死叉设置。提示：它反应缓慢；最适合战略趋势确认而非频繁交易入场。
- close_10_ema: 10 EMA：响应快速的短期平均线。用途：捕捉快速的动量变化和潜在入场点。提示：在震荡市场中容易产生噪音；与更长的平均线一起使用以过滤虚假信号。

MACD 相关：
- macd: MACD：通过 EMA 差异计算动量。用途：寻找交叉和背离作为趋势变化的信号。提示：在低波动性或横盘市场中与其他指标确认。
- macds: MACD Signal：MACD 线的 EMA 平滑。用途：使用与 MACD 线的交叉来触发交易。提示：应该是更广泛策略的一部分，以避免误报。
- macdh: MACD Histogram：显示 MACD 线与其信号线之间的差距。用途：可视化动量强度并尽早发现背离。提示：可能波动较大；在快速移动的市场中使用额外过滤器。

动量指标 (Momentum Indicators)：
- rsi: RSI：测量动量以标记超买/超卖条件。用途：应用 70/30 阈值并观察背离以信号反转。提示：在强趋势中，RSI 可能保持极端；始终与趋势分析交叉检查。

波动率指标 (Volatility Indicators)：
- boll: Bollinger Middle：20 SMA，作为布林带的基础。用途：作为价格运动的动态基准。提示：与上下轨结合使用，有效发现突破或反转。
- boll_ub: Bollinger Upper Band：通常是中线上方 2 个标准差。用途：信号潜在超买条件和突破区域。提示：用其他工具确认信号；在强趋势中价格可能沿着带运行。
- boll_lb: Bollinger Lower Band：通常是中线下方 2 个标准差。用途：指示潜在超卖条件。提示：使用额外分析以避免虚假反转信号。
- atr: ATR：平均真实范围以测量波动率。用途：根据当前市场波动率设置止损水平并调整仓位大小。提示：这是一个反应性指标，所以将其作为更广泛风险管理策略的一部分使用。

成交量指标 (Volume-Based Indicators)：
- vwma: VWMA：按成交量加权的移动平均线。用途：通过整合价格行为与成交量数据确认趋势。提示：注意成交量激增导致的偏差结果；与其他成交量分析结合使用。

- 选择提供多样化和互补信息的指标。避免冗余（例如，不要同时选择 rsi 和 stochrsi）。还要简要解释为什么它们适合给定的市场环境。当你调用工具时，请使用上面提供的指标的确切名称，因为它们是定义的参数，否则你的调用将失败。请确保首先调用 get_stock_data 以检索生成指标所需的 CSV。然后使用 get_indicators 与特定指标名称。撰写一份非常详细且细致的趋势报告。不要简单地说趋势是混合的，而是提供详细且精细的分析和见解，帮助交易员做出决策。"""
            + """ 确保在报告末尾附上一个 Markdown 表格，以组织报告中的关键点，使其条理清晰、易于阅读。"""
            + get_language_instruction()
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一名有用的 AI 助手，与其他助手协作。"
                    " 使用提供的工具来推进问题的解答。"
                    " 如果你无法完全回答，没关系；拥有不同工具的其他助手"
                    " 会在你停下的地方继续。尽你所能取得进展。"
                    " 如果你或任何其他助手得出了【最终交易指令】**BUY/HOLD/SELL**，"
                    " 请在回复前加上【最终交易指令】**BUY/HOLD/SELL**，这样团队就知道该停止了。"
                    " 你可以访问以下工具：{tool_names}。\n{system_message}"
                    "供参考，当前日期是 {current_date}。我们要查看的公司是 {ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content
       
        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node
