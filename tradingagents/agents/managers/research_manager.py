import time
import json


def create_research_manager(llm, memory):
    def research_manager_node(state) -> dict:
        history = state["investment_debate_state"].get("history", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        investment_debate_state = state["investment_debate_state"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""作为投资组合经理和辩论主持人，你的角色是批判性地评估这一轮辩论，并做出明确的决定：支持空头分析师、多头分析师，或仅在基于所提出的论点有充分理由时选择持有 (Hold)。

简洁地总结双方的关键点，重点关注最有说服力的证据或推理。你的建议——买入 (Buy)、卖出 (Sell) 或持有 (Hold)——必须清晰且可操作。不要仅仅因为双方都有合理的观点就默认选择持有；承诺基于辩论中最有力论据的立场。

此外，为交易员制定详细的投资计划。这应包括：

你的建议：由最有说服力的论据支持的明确立场。
理由：解释为什么这些论据导致你的结论。
战略行动：实施建议的具体步骤。
考虑你在类似情况下的过去错误。利用这些见解来完善你的决策，并确保你在学习和改进。以对话方式呈现你的分析，就像自然地说话一样，不需要特殊格式。

以下是你对过去错误的反思：
\"{past_memory_str}\"

以下是辩论内容：
辩论历史：
{history}"""
        response = llm.invoke(prompt)

        new_investment_debate_state = {
            "judge_decision": response.content,
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": response.content,
            "count": investment_debate_state["count"],
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": response.content,
        }

    return research_manager_node
