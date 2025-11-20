from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_fundamentals, get_balance_sheet, get_cashflow, get_income_statement, get_insider_sentiment, get_insider_transactions
from tradingagents.dataflows.config import get_config
from tradingagents.utils.language import get_language_instruction


def create_fundamentals_analyst(llm):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        tools = [
            get_fundamentals,
            get_balance_sheet,
            get_cashflow,
            get_income_statement,
        ]

        system_message = (
            "你是一名研究员，负责分析公司过去一周的基本面信息。请撰写一份全面的报告，涵盖公司的基本面信息，例如财务文件、公司简介、基本财务数据和公司财务历史，以便为交易员提供公司基本面的完整视图。请尽可能包含详细信息。不要简单地说趋势是混合的，而是提供详细且精细的分析和见解，帮助交易员做出决策。"
            + " 确保在报告末尾附上一个 Markdown 表格，以组织报告中的关键点，使其条理清晰、易于阅读。"
            + " 使用可用的工具：`get_fundamentals` 用于全面的公司分析，`get_balance_sheet`、`get_cashflow` 和 `get_income_statement` 用于特定的财务报表。"
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
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
