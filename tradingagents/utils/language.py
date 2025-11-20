"""Language configuration utilities for TradingAgents.

This module provides utilities to manage language settings for agent prompts
and ensure consistent output language across all agents.
"""

from tradingagents.dataflows.config import get_config


def get_language_instruction() -> str:
    """Get the language instruction to append to agent prompts.

    Returns:
        str: A clear instruction for the LLM to respond in the configured language.
    """
    config = get_config()
    language = config.get("language", "zh")

    if language == "zh":
        return "\n\n**重要提示：请务必使用简体中文回答所有内容。**"
    elif language == "en":
        return "\n\n**IMPORTANT: Please respond in English for all content.**"
    else:
        # Default to Chinese if unknown language is specified
        return "\n\n**重要提示：请务必使用简体中文回答所有内容。**"


def get_language() -> str:
    """Get the current language setting.

    Returns:
        str: The language code ('zh' for Chinese, 'en' for English).
    """
    config = get_config()
    return config.get("language", "zh")


def format_prompt_with_language(prompt: str) -> str:
    """Format a prompt with language instruction.

    Args:
        prompt: The original prompt text.

    Returns:
        str: The prompt with language instruction appended.
    """
    return prompt + get_language_instruction()
