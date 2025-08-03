import asyncio
import os
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from config import config
from logger import app_logger
from audio_processor import AudioProcessor
from summarizer import MeetingSummarizer
from file_manager import FileManager

class MeetingBot:
    """Main Telegram bot class for meeting summarization."""
    
    def __init__(self):
        if not config.validate():
            raise ValueError("Missing required configuration. Check TELEGRAM_BOT_TOKEN and OPENAI_API_KEY")
        
        self.audio_processor = AudioProcessor()
        self.summarizer = MeetingSummarizer()
        self.file_manager = FileManager()
        
        # Create application
        self.application = Application.builder().token(config.telegram_bot_token).build()
        
        # Add handlers
        self._setup_handlers()
        
        app_logger.info("Meeting Bot initialized successfully")
    
    def _setup_handlers(self):
        """Setup bot command and message handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Audio file handler
        self.application.add_handler(
            MessageHandler(filters.AUDIO | filters.Document.AUDIO, self.handle_audio)
        )
        
        # Fallback for other messages
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text)
        )
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome_message = """
🎯 **Meeting Summary Bot**

Привет! Я помогу создать саммари ваших встреч.

**Как пользоваться:**
1. Отправьте мне аудиофайл записи встречи в формате .m4a
2. Подождите, пока я обработаю запись
3. Получите структурированное саммари встречи

**Ограничения:**
• Только .m4a файлы
• Максимальный размер: 100 МБ
• Поддержка русского и английского языков

Отправьте /help для получения дополнительной информации.
        """
        
        await update.message.reply_text(
            welcome_message, 
            parse_mode=ParseMode.MARKDOWN
        )
        app_logger.info(f"Start command from user {update.effective_user.id}")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = """
📖 **Помощь - Meeting Summary Bot**

**Поддерживаемые форматы:**
• .m4a аудиофайлы (до 100 МБ)

**Процесс обработки:**
1. Транскрипция с помощью OpenAI Whisper
2. Создание саммари с помощью GPT-4
3. Автоматическое удаление файлов через 24 часа

**Структура саммари:**
• Основные темы обсуждения
• Принятые решения
• Action items
• Ключевые моменты и инсайты
• Next steps

**Время обработки:**
Обычно 1-3 минуты в зависимости от длительности записи.

По вопросам и проблемам обращайтесь к администратору.
        """
        
        await update.message.reply_text(
            help_message, 
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle audio file uploads."""
        try:
            app_logger.info(f"Audio file received from user {update.effective_user.id}")
            
            # Get file info
            file = await context.bot.get_file(update.message.audio.file_id)
            file_size = update.message.audio.file_size
            filename = update.message.audio.file_name or "audio.m4a"
            
            # Validate file
            if not self.audio_processor.validate_audio_file(filename, file_size):
                await update.message.reply_text(
                    "❌ Неподдерживаемый файл. Пожалуйста, отправьте .m4a файл размером до 100 МБ."
                )
                return
            
            # Send processing message
            processing_msg = await update.message.reply_text(
                "🔄 Обрабатываю запись встречи...\n"
                "⏳ Это может занять несколько минут."
            )
            
            # Download and save file
            file_data = await file.download_as_bytearray()
            file_path = await self.file_manager.save_audio_file(file_data, filename)
            
            try:
                # Update status
                await processing_msg.edit_text(
                    "🔄 Создаю транскрипцию...\n"
                    "⏳ Это может занять несколько минут."
                )
                
                # Transcribe audio
                transcript = await self.audio_processor.transcribe_audio(file_path)
                
                if not transcript:
                    await processing_msg.edit_text(
                        "❌ Не удалось создать транскрипцию. Попробуйте еще раз."
                    )
                    return
                
                # Update status
                await processing_msg.edit_text(
                    "🔄 Создаю саммари встречи...\n"
                    "⏳ Почти готово!"
                )
                
                # Create summary
                summary = await self.summarizer.create_summary(transcript)
                
                if not summary:
                    await processing_msg.edit_text(
                        "❌ Не удалось создать саммари. Попробуйте еще раз."
                    )
                    return
                
                # Send summary
                formatted_summary = self.summarizer.format_summary_message(summary)
                await processing_msg.edit_text(
                    formatted_summary,
                    parse_mode=ParseMode.MARKDOWN
                )
                
                app_logger.info(f"Successfully processed audio for user {update.effective_user.id}")
                
            finally:
                # Cleanup file
                await self.audio_processor.cleanup_file(file_path)
                
        except Exception as e:
            app_logger.error(f"Error processing audio: {str(e)}")
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке файла. Пожалуйста, попробуйте еще раз."
            )
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages."""
        await update.message.reply_text(
            "📁 Пожалуйста, отправьте .m4a аудиофайл записи встречи для создания саммари.\n\n"
            "Используйте /help для получения дополнительной информации."
        )
    
    async def create_health_server(self):
        """Create a simple health check server for Railway."""
        async def health_check(request):
            return web.Response(text="OK", status=200)
        
        app = web.Application()
        app.router.add_get('/health', health_check)
        app.router.add_get('/', health_check)
        
        return app

    async def run(self):
        """Start the bot."""
        app_logger.info("Starting Meeting Bot...")
        
        import signal
        
        # Start health check server for Railway
        health_app = await self.create_health_server()
        runner = web.AppRunner(health_app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', config.port)
        await site.start()
        app_logger.info(f"Health check server started on port {config.port}")
        
        # Start file cleanup scheduler
        asyncio.create_task(self.file_manager.start_cleanup_scheduler())
        
        # Start the bot
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(drop_pending_updates=True)
        
        app_logger.info("Meeting Bot is running!")
        
        # Keep the bot running
        stop_event = asyncio.Event()
        
        def signal_handler(sig, frame):
            stop_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        await stop_event.wait()

async def main():
    """Main entry point."""
    try:
        bot = MeetingBot()
        await bot.run()
    except KeyboardInterrupt:
        app_logger.info("Bot stopped by user")
    except Exception as e:
        app_logger.error(f"Bot crashed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())