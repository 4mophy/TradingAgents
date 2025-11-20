from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_utils import get_news
from tradingagents.dataflows.config import get_config
from tradingagents.utils.language import get_language_instruction


def create_social_media_analyst(llm):
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        tools = [
            get_news,
        ]

        system_message = (
            "你是一名社交媒体和公司特定新闻研究员/分析师，负责分析过去一周特定公司的社交媒体帖子、最新公司新闻和公众情绪。你将获得一家公司的名称，你的目标是撰写一份全面详尽的报告，详细说明你的分析、见解以及对交易员和投资者的影响，在查看社交媒体和人们对该公司的评论、分析人们每天对公司的情绪数据以及查看最新公司新闻后，详述该公司的当前状态。使用 get_news(query, start_date, end_date) 工具搜索公司特定的新闻和社交媒体讨论。尝试从社交媒体到情绪到新闻的所有可能来源。不要简单地说趋势是混合的，而是提供详细且精细的分析和见解，帮助交易员做出决策。"
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
                    "供参考，当前日期是 {current_date}。我们当前要分析的公司是 {ticker}",
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
            "sentiment_report": report,
        }

    return social_media_analyst_node
