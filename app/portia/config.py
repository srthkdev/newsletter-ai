from portia import Portia, Config, LLMProvider, StorageClass
from app.core.config import settings
import os


# Initialize Portia configuration
def get_portia_config():
    """Get Portia configuration based on environment settings"""
    # Check for Portia API key first
    portia_api_key = settings.PORTIA_API_KEY
    
    # Use Gemini as the default LLM provider
    google_api_key = settings.GOOGLE_API_KEY

    if google_api_key:
        config = Config.from_default(
            llm_provider=LLMProvider.GOOGLE,
            default_model="google/gemini-2.5-flash",
            google_api_key=google_api_key,
            storage_class=StorageClass.CLOUD,
            portia_api_key=portia_api_key,  # Add Portia API key for cloud storage
        )
    else:
        # Fallback to OpenAI if Google API key is not available
        openai_api_key = settings.OPENAI_API_KEY
        if openai_api_key:
            config = Config.from_default(
                llm_provider=LLMProvider.OPENAI,
                default_model="gpt-4",
                openai_api_key=openai_api_key,
                storage_class=StorageClass.CLOUD,
                portia_api_key=portia_api_key,  # Add Portia API key for cloud storage
            )
        else:
            # Create a minimal config with cloud storage for testing
            config = Config.from_default(
                storage_class=StorageClass.CLOUD,
                portia_api_key=portia_api_key,  # Add Portia API key for cloud storage
            )

    return config


# Initialize Portia client with Slack MCP integration
def get_portia_client():
    """Get configured Portia client instance with Slack MCP integration"""
    try:
        # Check if we have the required API keys
        google_api_key = settings.GOOGLE_API_KEY
        portia_api_key = settings.PORTIA_API_KEY
        
        # Only initialize if we have at least one API key
        if (google_api_key or portia_api_key) and portia_api_key:
            config = get_portia_config()
            
            # Initialize Portia client
            portia = Portia(config=config)
            
            # Add Slack MCP integration if Slack tokens are configured
            slack_bot_token = settings.SLACK_BOT_TOKEN
            slack_app_token = settings.SLACK_APP_TOKEN
            
            if slack_bot_token and slack_app_token:
                print("✅ Slack MCP integration available")
                # In a real implementation, we would integrate the Slack MCP tools here
                # For now, we'll just indicate that Slack integration is available
                pass
            
            return portia
        else:
            # Return None if no API keys are configured
            print("⚠️  Portia API key not configured. Plans will not be visible on app.portia.")
            return None
    except ImportError:
        # Portia SDK not installed
        print("Warning: Could not initialize Portia client: Please install portia-sdk-python to use this functionality.")
        return None
    except Exception as e:
        print(f"Warning: Could not initialize Portia client: {e}")
        return None


# Agent configurations using Gemini models
AGENT_CONFIGS = {
    "research_agent": {
        "name": "NewsletterResearcher",
        "description": "Discovers and curates newsletter content using Tavily API",
        "model": "google/gemini-2.5-flash",
        "temperature": 0.7,
        "max_tokens": 2000,
    },
    "writing_agent": {
        "name": "NewsletterWriter",
        "description": "Generates engaging blog-style newsletter content",
        "model": "google/gemini-2.5-flash",
        "temperature": 0.8,
        "max_tokens": 3000,
    },
    "preference_agent": {
        "name": "PreferenceManager",
        "description": "Manages user preferences and personalization",
        "model": "google/gemini-2.5-flash",
        "temperature": 0.3,
        "max_tokens": 1000,
    },
    "custom_prompt_agent": {
        "name": "CustomPromptProcessor",
        "description": "Processes custom user prompts for newsletter generation",
        "model": "google/gemini-2.5-flash",
        "temperature": 0.6,
        "max_tokens": 2000,
    },
    "mindmap_agent": {
        "name": "MindmapGenerator",
        "description": "Generates interactive mindmaps from newsletter content",
        "model": "google/gemini-2.5-flash",
        "temperature": 0.5,
        "max_tokens": 2500,
    },
}