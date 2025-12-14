"""
Configuration settings for Multi-Agent Collaborative System using Qwen LLM
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for Qwen-based Multi-Agent System"""
    
    # Qwen API Configuration
    LLM_API_KEY: Optional[str] = os.getenv("QWEN_API_KEY", os.getenv("DASHSCOPE_API_KEY"))
    LLM_BASE_URL: str = os.getenv("QWEN_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
    
    # Model Configuration
    MODEL_NAME: str = os.getenv("QWEN_MODEL", "qwen3-coder-plus")  # Options: qwen3-coder-plus, qwen-plus, qwen-coder-turbo, qwen-turbo
    MODEL_TEMPERATURE: float = 0.1  # Low temperature for more deterministic code generation
    MODEL_MAX_TOKENS: int = 4096  # Increased for qwen3-coder-plus's enhanced capabilities
    
    # Agent Configuration
    MAX_RETRIES: int = 5
    TIMEOUT_SECONDS: int = 180
    
    # Project Configuration
    OUTPUT_DIR: str = os.path.join(os.path.dirname(__file__), "output")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Tool Configuration
    ENABLE_WEB_SEARCH: bool = True
    ENABLE_FILE_OPERATIONS: bool = True
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings"""
        if not cls.LLM_API_KEY:
            raise ValueError(
                "QWEN_API_KEY or DASHSCOPE_API_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )
        return True
    
    @classmethod
    def get_llm_config(cls) -> dict:
        """Get LLM configuration dictionary"""
        cls.validate()
        return {
            "api_key": cls.LLM_API_KEY,
            "base_url": cls.LLM_BASE_URL,
            "model": cls.MODEL_NAME,
            "temperature": cls.MODEL_TEMPERATURE,
            "max_tokens": cls.MODEL_MAX_TOKENS,
            "timeout": cls.TIMEOUT_SECONDS,
            "max_retries": cls.MAX_RETRIES
        }

# Example .env file content:
ENV_EXAMPLE = """
# Qwen API Configuration (新加坡地域)
DASHSCOPE_API_KEY=sk-your_api_key_here
# QWEN_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1  # 新加坡地域 (default)
# 北京地域请使用: QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# QWEN_MODEL=qwen3-coder-plus  # Options: qwen3-coder-plus (default), qwen-plus, qwen-coder-turbo, qwen-turbo

# Alternative for local deployment
# QWEN_BASE_URL=http://localhost:8000/v1
# DASHSCOPE_API_KEY=dummy_key_for_local

# Logging
LOG_LEVEL=INFO
"""