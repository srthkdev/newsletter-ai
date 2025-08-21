from portia import Portia, Config, LLMProvider
from portia.open_source_tools.registry import example_tool_registry
from app.core.config import settings
import os


# Initialize Portia configuration
def get_portia_config():
    """Get Portia configuration based on environment settings"""
    # Use Gemini as the default LLM provider
    google_api_key = os.getenv("GOOGLE_API_KEY")

    if google_api_key:
        config = Config.from_default(
            llm_provider=LLMProvider.GOOGLE,
            default_model="google/gemini-2.0-flash",
            google_api_key=google_api_key,
        )
    else:
        # Fallback to OpenAI if Google API key is not available
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            config = Config.from_default(
                llm_provider=LLMProvider.OPENAI,
                default_model="gpt-4",
                openai_api_key=openai_api_key,
            )
        else:
            # Create a minimal config without API keys for testing
            config = Config.from_default()

    return config


# Initialize Portia client
def get_portia_client():
    """Get configured Portia client instance"""
    try:
        config = get_portia_config()
        return Portia(config=config, tools=example_tool_registry)
    except Exception as e:
        print(f"Warning: Could not initialize Portia client: {e}")
        return None


# Agent configurations using Gemini models
AGENT_CONFIGS = {
    "research_agent": {
        "name": "NewsletterResearcher",
        "description": "Discovers and curates newsletter content using Tavily API",
        "model": "google/gemini-2.0-flash",
        "temperature": 0.7,
        "max_tokens": 2000,
    },
    "writing_agent": {
        "name": "NewsletterWriter",
        "description": "Generates engaging blog-style newsletter content",
        "model": "google/gemini-2.0-flash",
        "temperature": 0.8,
        "max_tokens": 3000,
    },
    "preference_agent": {
        "name": "PreferenceManager",
        "description": "Manages user preferences and personalization",
        "model": "google/gemini-2.0-flash",
        "temperature": 0.3,
        "max_tokens": 1000,
    },
    "custom_prompt_agent": {
        "name": "CustomPromptProcessor",
        "description": "Processes custom user prompts for newsletter generation",
        "model": "google/gemini-2.0-flash",
        "temperature": 0.6,
        "max_tokens": 2000,
    },
}
