import os
import locale


def _detect_system_language():
    """Detect system language and return appropriate language code.

    Returns:
        str: 'zh' for Chinese systems, 'en' for others
    """
    try:
        # Try to get system locale using the recommended method
        system_locale = locale.getlocale()[0]
        if system_locale:
            # Check if it's a Chinese locale (zh_CN, zh_TW, zh_HK, etc.)
            if system_locale.lower().startswith('zh'):
                return 'zh'
    except Exception:
        # If locale detection fails, fall back to 'en'
        pass

    # Default to English for non-Chinese systems or if detection fails
    return 'en'


DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": "openai",
    "deep_think_llm": "o4-mini",
    "quick_think_llm": "gpt-4o-mini",
    "backend_url": "https://api.openai.com/v1",
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Language settings (default to Chinese, can be overridden by TRADINGAGENTS_LANGUAGE env var)
    "language": os.getenv("TRADINGAGENTS_LANGUAGE", "zh"),  # Options: zh (Chinese), en (English)
    # Data vendor configuration
    # Category-level configuration (default for all tools in category)
    "data_vendors": {
        "core_stock_apis": "auto",           # Options: auto (智能检测), yfinance, akshare, alpha_vantage, local
                                             # auto: A股→akshare, 美股→yfinance, 港股→yfinance
        "technical_indicators": "yfinance",  # Options: yfinance, alpha_vantage, local
        "fundamental_data": "alpha_vantage", # Options: openai, alpha_vantage, local
        "news_data": "alpha_vantage",        # Options: openai, alpha_vantage, google, local
        "fund_data": "akshare",              # Options: akshare (基金和指数数据)
    },
    # Tool-level configuration (takes precedence over category-level)
    "tool_vendors": {
        # Example: "get_stock_data": "alpha_vantage",  # Override category default
        # Example: "get_news": "openai",               # Override category default
    },
}
