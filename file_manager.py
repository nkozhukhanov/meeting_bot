import os
import asyncio
import aiofiles
from datetime import datetime, timedelta
from typing import Optional
from config import config
from logger import app_logger

class FileManager:
    """Handles temporary file storage and cleanup."""
    
    def __init__(self):
        self.storage_path = config.storage_path
        self.retention_hours = config.file_retention_hours
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self):
        """Create storage directory if it doesn't exist."""
        os.makedirs(self.storage_path, exist_ok=True)
        app_logger.info(f"Storage directory ready: {self.storage_path}")
    
    async def save_audio_file(self, file_data: bytes, filename: str) -> str:
        """Save audio file to temporary storage."""
        try:
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(self.storage_path, unique_filename)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_data)
            
            app_logger.info(f"File saved: {file_path} ({len(file_data)} bytes)")
            return file_path
            
        except Exception as e:
            app_logger.error(f"Failed to save file {filename}: {str(e)}")
            raise
    
    async def cleanup_old_files(self):
        """Remove files older than retention period."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
            cleaned_count = 0
            
            for filename in os.listdir(self.storage_path):
                file_path = os.path.join(self.storage_path, filename)
                
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        cleaned_count += 1
                        app_logger.info(f"Cleaned up old file: {filename}")
            
            if cleaned_count > 0:
                app_logger.info(f"Cleanup completed: {cleaned_count} files removed")
            
        except Exception as e:
            app_logger.error(f"Cleanup failed: {str(e)}")
    
    async def start_cleanup_scheduler(self):
        """Start background task for periodic file cleanup."""
        while True:
            await asyncio.sleep(3600)  # Run every hour
            await self.cleanup_old_files()