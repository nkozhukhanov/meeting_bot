import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    # Telegram Configuration
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # System Prompt
    system_prompt: str = os.getenv(
        "SYSTEM_PROMPT",
        """Ты профессиональный помощник для анализа записей встреч. Твоя задача - создать структурированное саммари встречи на основе транскрипции. 

Саммари должно включать:
1) **Основные темы обсуждения** - краткое перечисление главных вопросов
2) **Принятые решения** - конкретные решения, принятые на встрече
3) **Action items** - задачи с ответственными (если указаны) и дедлайнами
4) **Ключевые моменты и инсайты** - важные выводы и открытия
5) **Next steps** - следующие шаги и планы

Используй четкую структуру с заголовками и bullet points. Отвечай на русском языке. Если встреча на английском, переведи основные моменты на русский."""
    )
    
    # Redis Configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # File Storage Configuration
    storage_path: str = os.getenv("STORAGE_PATH", "./temp_files")
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "20"))  # Reduced to match Telegram limit
    file_retention_hours: int = int(os.getenv("FILE_RETENTION_HOURS", "24"))
    
    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    logtail_source_token: str = os.getenv("LOGTAIL_SOURCE_TOKEN", "")
    
    # Server Configuration
    port: int = int(os.getenv("PORT", "8000"))
    
    def validate(self) -> bool:
        """Validate required configuration parameters."""
        required_fields = [
            self.telegram_bot_token,
            self.openai_api_key
        ]
        return all(field.strip() for field in required_fields)

config = Config()