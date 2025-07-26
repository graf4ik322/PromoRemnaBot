#!/usr/bin/env python3
"""
Remnawave Telegram Bot - Main Application
"""

import asyncio
import logging
import signal
import sys
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    ConversationHandler,
    MessageHandler,
    filters
)
from config import Config
from bot_handlers import BotHandlers, WAITING_TAG, WAITING_COUNT

# Configure logging
def setup_logging():
    """Setup logging configuration"""
    # Ensure logs directory exists with proper permissions
    import os
    import stat
    
    try:
        os.makedirs('logs', exist_ok=True)
        # Try to set permissions (may fail in some environments)
        try:
            os.chmod('logs', stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)  # 755
        except (OSError, PermissionError):
            pass  # Ignore permission errors
    except PermissionError:
        print("Warning: Cannot create logs directory, using stdout only")
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        return
    
    # Try to create log file handler, fall back to stdout only if fails
    handlers = [logging.StreamHandler(sys.stdout)]
    
    try:
        file_handler = logging.FileHandler('logs/bot.log')
        handlers.append(file_handler)
    except (PermissionError, OSError) as e:
        print(f"Warning: Cannot write to log file: {e}. Using stdout only.")
    
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
        handlers=handlers
    )

logger = logging.getLogger(__name__)

class RemnawaveBot:
    """Main bot application class"""
    
    def __init__(self):
        self.application = None
        self.handlers = BotHandlers()
        
    async def setup_bot(self):
        """Setup bot application and handlers"""
        try:
            # Validate configuration
            Config.validate()
            
            # Create application
            self.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
            
            # Setup conversation handler for promo creation
            promo_conv_handler = ConversationHandler(
                entry_points=[CallbackQueryHandler(self.handlers.create_promo_callback, pattern='^create_promo$')],
                states={
                    WAITING_TAG: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.handle_tag_input),
                        CallbackQueryHandler(self.handlers.main_menu_callback, pattern='^main_menu$')
                    ],
                    WAITING_COUNT: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.handle_count_input),
                        CallbackQueryHandler(self.handlers.main_menu_callback, pattern='^main_menu$')
                    ]
                },
                fallbacks=[
                    CommandHandler('cancel', self.handlers.cancel_command),
                    CallbackQueryHandler(self.handlers.main_menu_callback, pattern='^main_menu$')
                ],
                per_chat=True,
                allow_reentry=True
            )
            
            # Add handlers
            self.application.add_handler(CommandHandler('start', self.handlers.start_command))
            self.application.add_handler(CommandHandler('cancel', self.handlers.cancel_command))
            self.application.add_handler(promo_conv_handler)
            
            # Callback query handlers for main functions
            self.application.add_handler(CallbackQueryHandler(
                self.handlers.main_menu_callback, pattern='^main_menu$'
            ))
            self.application.add_handler(CallbackQueryHandler(
                self.handlers.handle_traffic_limit, pattern=r'^traffic_\d+$'
            ))
            self.application.add_handler(CallbackQueryHandler(
                self.handlers.confirm_create_callback, pattern='^confirm_create$'
            ))
            self.application.add_handler(CallbackQueryHandler(
                self.handlers.delete_used_callback, pattern='^delete_used$'
            ))
            self.application.add_handler(CallbackQueryHandler(
                self.handlers.delete_tag_callback, pattern='^delete_tag_'
            ))
            self.application.add_handler(CallbackQueryHandler(
                self.handlers.confirm_delete_callback, pattern='^confirm_delete_'
            ))
            self.application.add_handler(CallbackQueryHandler(
                self.handlers.stats_callback, pattern='^stats$'
            ))
            
            # Error handler
            self.application.add_error_handler(self.handlers.error_handler)
            
            logger.info("Bot setup completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup bot: {str(e)}")
            raise
    
    async def start_bot(self):
        """Start the bot"""
        try:
            logger.info("Starting Remnawave Telegram Bot...")
            
            # Initialize and start the application
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"]
            )
            
            logger.info("Bot started successfully! Press Ctrl+C to stop.")
            
            # Keep the bot running
            stop_event = asyncio.Event()
            
            def signal_handler(signum, frame):
                logger.info(f"Received signal {signum}. Stopping bot...")
                stop_event.set()
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            await stop_event.wait()
            
        except Exception as e:
            logger.error(f"Error running bot: {str(e)}")
            raise
        finally:
            await self.stop_bot()
    
    async def stop_bot(self):
        """Stop the bot gracefully"""
        if self.application:
            logger.info("Stopping bot...")
            try:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
                logger.info("Bot stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping bot: {str(e)}")

async def main():
    """Main function"""
    setup_logging()
    
    try:
        # Create and setup bot
        bot = RemnawaveBot()
        await bot.setup_bot()
        
        # Start bot
        await bot.start_bot()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)