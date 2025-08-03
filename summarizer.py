from typing import Optional
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from config import config
from logger import app_logger

class MeetingSummarizer:
    """Handles meeting transcript summarization using GPT."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.openai_api_key)
        self.model = config.openai_model
        self.system_prompt = config.system_prompt
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def create_summary(self, transcript: str) -> Optional[str]:
        """Create meeting summary from transcript using GPT."""
        try:
            app_logger.info(f"Creating summary for transcript of {len(transcript)} characters")
            
            # Truncate transcript if too long (GPT-4 context limit)
            max_transcript_length = 12000  # Conservative limit for GPT-4o-mini
            if len(transcript) > max_transcript_length:
                transcript = transcript[:max_transcript_length]
                app_logger.warning(f"Transcript truncated to {max_transcript_length} characters")
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Создай саммари для следующей транскрипции встречи:\n\n{transcript}"}
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent summaries
                max_tokens=1500   # Reasonable limit for summary length
            )
            
            summary = response.choices[0].message.content
            app_logger.info(f"Summary created successfully. Length: {len(summary)} chars")
            
            return summary
            
        except Exception as e:
            app_logger.error(f"Summary creation failed: {str(e)}")
            raise
    
    def format_summary_message(self, summary: str) -> str:
        """Format summary for Telegram message."""
        # Add header and footer to make the message more professional
        formatted_message = f"""🎯 **Саммари встречи**

{summary}

---
_Создано автоматически с помощью Meeting Summary Bot_
"""
        return formatted_message