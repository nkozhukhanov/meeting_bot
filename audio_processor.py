import os
import aiofiles
from typing import Optional
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from config import config
from logger import app_logger

class AudioProcessor:
    """Handles audio file processing and transcription using OpenAI Whisper."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.openai_api_key)
        self.max_file_size = config.max_file_size_mb * 1024 * 1024  # Convert to bytes
        self.whisper_max_size = 24 * 1024 * 1024  # 24 MB - safe limit for Whisper API
    
    def validate_audio_file(self, file_path: str, file_size: int) -> bool:
        """Validate audio file format and size."""
        if file_size > self.max_file_size:
            app_logger.warning(f"File too large: {file_size} bytes (max: {self.max_file_size})")
            return False
        
        if not file_path.lower().endswith('.m4a'):
            app_logger.warning(f"Invalid file format: {file_path}")
            return False
        
        return True
    
    def check_whisper_size_limit(self, file_size: int) -> bool:
        """Check if file is within Whisper API size limit."""
        if file_size > self.whisper_max_size:
            app_logger.warning(f"File too large for Whisper API: {file_size} bytes (max: {self.whisper_max_size})")
            return False
        return True
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def transcribe_audio(self, file_path: str) -> Optional[str]:
        """Transcribe audio file using OpenAI Whisper API."""
        try:
            app_logger.info(f"Starting transcription for: {file_path}")
            
            # Check file size before processing
            file_size = os.path.getsize(file_path)
            app_logger.info(f"File size: {file_size} bytes ({file_size / 1024 / 1024:.2f} MB)")
            
            if not self.check_whisper_size_limit(file_size):
                raise ValueError(f"File size {file_size / 1024 / 1024:.2f} MB exceeds Whisper API limit of 24 MB")
            
            async with aiofiles.open(file_path, 'rb') as audio_file:
                audio_data = await audio_file.read()
            
            # Create a temporary file-like object for OpenAI API
            import io
            audio_buffer = io.BytesIO(audio_data)
            audio_buffer.name = os.path.basename(file_path)
            
            app_logger.info(f"Sending {len(audio_data)} bytes to Whisper API")
            
            response = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_buffer,
                language="auto"  # Auto-detect language (supports Russian and English)
            )
            
            transcript = response.text
            app_logger.info(f"Transcription completed successfully. Length: {len(transcript)} chars")
            
            return transcript
            
        except Exception as e:
            app_logger.error(f"Transcription failed for {file_path}: {str(e)}")
            raise
    
    async def cleanup_file(self, file_path: str) -> None:
        """Remove temporary audio file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                app_logger.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            app_logger.error(f"Failed to cleanup file {file_path}: {str(e)}")