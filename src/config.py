"""
Central configuration for LLM providers and env vars.
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic

load_dotenv()

# Try to import ChatGrok, fallback to requests implementation if unavailable
try:
    from langchain_xai import ChatGrok
    grok_available = True
except ImportError:
    grok_available = False
    print("Warning: langchain-xai not available. Grok integration will use requests fallback.")

def get_grok_llm():
    """Get Grok LLM instance with fallback handling."""
    if grok_available:
        return ChatGrok(api_key=os.getenv("GROK_API_KEY"), model="grok-beta")
    else:
        # Fallback to OpenAI since Grok integration has dependency conflicts
        print("Warning: Using OpenAI GPT-4o as fallback for Grok (dependency conflict)")
        return ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o")

def get_available_llms():
    """Get available LLM configurations based on environment variables."""
    llms = {}
    
    # OpenAI GPT-4o
    if os.getenv("OPENAI_API_KEY"):
        llms["gpt4o"] = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o")
    
    # Google Gemini
    if os.getenv("GOOGLE_API_KEY"):
        llms["gemini2.5"] = ChatGoogleGenerativeAI(
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            model="gemini-1.5-pro"
        )
    
    # Anthropic Claude
    if os.getenv("ANTHROPIC_API_KEY"):
        llms["claude3.5"] = ChatAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model="claude-3-5-sonnet-20240620"
        )
    
    # Grok (with fallback)
    llms["grok4"] = get_grok_llm()
    
    return llms

LLM_CONFIG = get_available_llms()

# Use available LLM as default
def get_default_llm():
    if "gpt4o" in LLM_CONFIG:
        return LLM_CONFIG["gpt4o"]
    elif "claude3.5" in LLM_CONFIG:
        return LLM_CONFIG["claude3.5"]
    elif "gemini2.5" in LLM_CONFIG:
        return LLM_CONFIG["gemini2.5"]
    elif "grok4" in LLM_CONFIG:
        return LLM_CONFIG["grok4"]
    else:
        raise ValueError("No LLM providers available. Please configure at least one API key.")

DEFAULT_LLM = get_default_llm()

# Configuration for different agent roles with fallbacks
def get_agent_llm_config():
    default = get_default_llm()
    return {
        "fetcher": LLM_CONFIG.get("gpt4o", default),
        "data_reviewer": LLM_CONFIG.get("claude3.5", default),
        "analyzer": LLM_CONFIG.get("gpt4o", default), 
        "analysis_reviewer": LLM_CONFIG.get("claude3.5", default),
        "synthesizer": LLM_CONFIG.get("gemini2.5", default),
        "final_reviewer": LLM_CONFIG.get("claude3.5", default)
    }

AGENT_LLM_CONFIG = get_agent_llm_config()