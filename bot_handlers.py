"""
Telegram Bot Handlers Module
"""

import logging
import re
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import TelegramError
from remnawave_service import RemnawaveService
from config import Config

logger = logging.getLogger(__name__)

# Conversation states
(WAITING_TAG, WAITING_COUNT, WAITING_CONFIRM_DELETE, 
 SELECTING_TAG_DELETE, SHOWING_DELETE_PREVIEW) = range(5)

class BotHandlers:
    """Main bot handlers class"""
    
    def __init__(self):
        self.remnawave_service = RemnawaveService()
        self.user_sessions: Dict[int, Dict[str, Any]] = {}
    
    def _is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in Config.ADMIN_USER_IDS
    
    async def _delete_previous_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Delete previous bot messages if they exist"""
        if update.callback_query and update.callback_query.message:
            try:
                await update.callback_query.message.delete()
            except TelegramError:
                pass  # Message might be already deleted
    
    def _get_main_menu_keyboard(self) -> InlineKeyboardMarkup:
        """Get main menu inline keyboard"""
        keyboard = [
            [InlineKeyboardButton("🎁 Создать промо-кампанию", callback_data="create_promo")],
            [InlineKeyboardButton("🗑 Удалить использованные подписки", callback_data="delete_used")],
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def _get_back_to_main_keyboard(self) -> InlineKeyboardMarkup:
        """Get back to main menu keyboard"""
        keyboard = [[InlineKeyboardButton("⬅️ Назад в главное меню", callback_data="main_menu")]]
        return InlineKeyboardMarkup(keyboard)
    
    def _get_traffic_limit_keyboard(self) -> InlineKeyboardMarkup:
        """Get traffic limit selection keyboard"""
        keyboard = [
            [InlineKeyboardButton("15GB", callback_data="traffic_15")],
            [InlineKeyboardButton("30GB", callback_data="traffic_30")],
            [InlineKeyboardButton("50GB", callback_data="traffic_50")],
            [InlineKeyboardButton("100GB", callback_data="traffic_100")],
            [InlineKeyboardButton("⬅️ Назад в главное меню", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle /start command"""
        user_id = update.effective_user.id
        
        if not self._is_admin(user_id):
            await update.message.reply_text(
                "❌ У вас нет прав доступа к этому боту.",
                reply_markup=None
            )
            return ConversationHandler.END
        
        await update.message.reply_text(
            "🤖 *Добро пожаловать в Remnawave Promo Bot!*\n\n"
            "Выберите действие:",
            parse_mode='Markdown',
            reply_markup=self._get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    async def main_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle main menu callback"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "🤖 *Remnawave Promo Bot*\n\n"
            "Выберите действие:",
            parse_mode='Markdown',
            reply_markup=self._get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    async def create_promo_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start promo creation process"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        self.user_sessions[user_id] = {}
        
        await query.edit_message_text(
            "🏷 *Создание промо-кампании*\n\n"
            "Введите тег кампании:\n\n"
            "⚠️ *Требования к тегу:*\n"
            "• Только латинские буквы\n"
            "• Цифры, подчеркивания и дефисы разрешены\n"
            "• Пробелы заменяйте на подчеркивания (_)",
            parse_mode='Markdown',
            reply_markup=self._get_back_to_main_keyboard()
        )
        return WAITING_TAG
    
    async def handle_tag_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle tag input"""
        user_id = update.effective_user.id
        tag = update.message.text.strip()
        
        # Delete user message
        try:
            await update.message.delete()
        except TelegramError:
            pass
        
        # Validate tag
        if not self.remnawave_service._validate_tag(tag):
            # Send new message instead of trying to edit
            await update.effective_chat.send_message(
                text="❌ *Неверный формат тега!*\n\n"
                     "Введите тег кампании:\n\n"
                     "⚠️ *Требования к тегу:*\n"
                     "• Только латинские буквы\n"
                     "• Цифры, подчеркивания и дефисы разрешены\n"
                     "• Пробелы заменяйте на подчеркивания (_)",
                parse_mode='Markdown',
                reply_markup=self._get_back_to_main_keyboard()
            )
            return WAITING_TAG
        
        # Store tag and ask for traffic limit
        self.user_sessions[user_id]['tag'] = tag
        
        # Send new message for traffic limit selection
        await update.effective_chat.send_message(
            text=f"✅ *Тег:* `{tag}`\n\n"
                 "📊 Выберите лимит трафика:",
            parse_mode='Markdown',
            reply_markup=self._get_traffic_limit_keyboard()
        )
        
        return ConversationHandler.END
    
    async def handle_traffic_limit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle traffic limit selection"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        if user_id not in self.user_sessions:
            await query.edit_message_text(
                "❌ Сессия истекла. Начните заново.",
                reply_markup=self._get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        # Extract traffic limit from callback data
        traffic_map = {
            'traffic_15': 15,
            'traffic_30': 30,
            'traffic_50': 50,
            'traffic_100': 100
        }
        
        traffic_limit = traffic_map.get(query.data)
        if not traffic_limit:
            return ConversationHandler.END
        
        self.user_sessions[user_id]['traffic_limit'] = traffic_limit
        tag = self.user_sessions[user_id]['tag']
        
        await query.edit_message_text(
            f"✅ *Тег:* `{tag}`\n"
            f"📊 *Лимит трафика:* {traffic_limit}GB\n\n"
            f"🔢 Введите количество подписок (1-{Config.MAX_SUBSCRIPTIONS_PER_REQUEST}):",
            parse_mode='Markdown',
            reply_markup=self._get_back_to_main_keyboard()
        )
        return WAITING_COUNT
    
    async def handle_count_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle subscription count input"""
        user_id = update.effective_user.id
        
        # Delete user message
        try:
            await update.message.delete()
        except TelegramError:
            pass
        
        if user_id not in self.user_sessions:
            return ConversationHandler.END
        
        try:
            count = int(update.message.text.strip())
            
            if count < 1 or count > Config.MAX_SUBSCRIPTIONS_PER_REQUEST:
                raise ValueError("Invalid count")
                
        except ValueError:
            await update.effective_chat.send_message(
                text=f"❌ *Неверное количество!*\n\n"
                     f"Введите число от 1 до {Config.MAX_SUBSCRIPTIONS_PER_REQUEST}:",
                parse_mode='Markdown',
                reply_markup=self._get_back_to_main_keyboard()
            )
            return WAITING_COUNT
        
        # Store count and show confirmation
        self.user_sessions[user_id]['count'] = count
        tag = self.user_sessions[user_id]['tag']
        traffic_limit = self.user_sessions[user_id]['traffic_limit']
        
        confirm_keyboard = [
            [InlineKeyboardButton("✅ Подтвердить создание", callback_data="confirm_create")],
            [InlineKeyboardButton("❌ Отменить", callback_data="main_menu")]
        ]
        
        await update.effective_chat.send_message(
            text=f"📋 *Подтверждение создания:*\n\n"
                 f"🏷 **Тег:** `{tag}`\n"
                 f"📊 **Лимит трафика:** {traffic_limit}GB\n"
                 f"🔢 **Количество:** {count}\n\n"
                 f"Подтвердить создание {count} подписок?",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(confirm_keyboard)
        )
        
        return ConversationHandler.END
    
    async def confirm_create_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle creation confirmation"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        if user_id not in self.user_sessions:
            await query.edit_message_text(
                "❌ Сессия истекла. Начните заново.",
                reply_markup=self._get_main_menu_keyboard()
            )
            return ConversationHandler.END
        
        session_data = self.user_sessions[user_id]
        tag = session_data['tag']
        traffic_limit = session_data['traffic_limit']
        count = session_data['count']
        
        # Show progress message
        await query.edit_message_text(
            f"⏳ *Создание {count} подписок...*\n\n"
            f"🏷 Тег: `{tag}`\n"
            f"📊 Лимит: {traffic_limit}GB\n\n"
            f"⚠️ Не закрывайте бота, процесс может занять некоторое время.",
            parse_mode='Markdown'
        )
        
        try:
            # Create subscriptions
            subscription_links, file_url = await self.remnawave_service.create_promo_users(
                tag, traffic_limit, count
            )
            
            success_count = len(subscription_links)
            
            if success_count > 0:
                result_text = (
                    f"✅ *Промо-кампания создана успешно!*\n\n"
                    f"🏷 **Тег:** `{tag}`\n"
                    f"📊 **Лимит трафика:** {traffic_limit}GB\n"
                    f"✅ **Создано подписок:** {success_count}/{count}\n\n"
                )
                
                if file_url:
                    result_text += f"📁 **Файл с подписками:** [Скачать]({file_url})\n\n"
                
                # Show first few subscription links as examples
                if len(subscription_links) <= 5:
                    result_text += "🔗 **Ссылки на подписки:**\n"
                    for i, link in enumerate(subscription_links, 1):
                        result_text += f"`{link}`\n"
                else:
                    result_text += "🔗 **Примеры ссылок:**\n"
                    for i, link in enumerate(subscription_links[:3], 1):
                        result_text += f"`{link}`\n"
                    result_text += f"... и ещё {len(subscription_links) - 3}"
            else:
                result_text = (
                    f"❌ *Ошибка создания подписок!*\n\n"
                    f"Не удалось создать ни одной подписки.\n"
                    f"Проверьте логи для подробностей."
                )
            
            await query.edit_message_text(
                result_text,
                parse_mode='Markdown',
                reply_markup=self._get_back_to_main_keyboard(),
                disable_web_page_preview=True
            )
            
        except Exception as e:
            logger.error(f"Error creating promo campaign: {str(e)}")
            await query.edit_message_text(
                f"❌ *Ошибка при создании кампании:*\n\n"
                f"`{str(e)}`",
                parse_mode='Markdown',
                reply_markup=self._get_back_to_main_keyboard()
            )
        
        # Clean up session
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        
        return ConversationHandler.END
    
    async def delete_used_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start delete used subscriptions process"""
        query = update.callback_query
        await query.answer()
        
        # Show loading message
        await query.edit_message_text(
            "⏳ Загрузка списка тегов...",
            reply_markup=None
        )
        
        try:
            tags_with_stats = await self.remnawave_service.get_tags_with_stats()
            
            if not tags_with_stats:
                await query.edit_message_text(
                    "❌ Промо-кампании не найдены.",
                    reply_markup=self._get_back_to_main_keyboard()
                )
                return ConversationHandler.END
            
            # Create keyboard with tags
            keyboard = []
            for tag_info in tags_with_stats:
                tag = tag_info['tag']
                total = tag_info['total']
                used = tag_info['used']
                
                button_text = f"{tag} ({used}/{total} использовано)"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"delete_tag_{tag}")])
            
            keyboard.append([InlineKeyboardButton("⬅️ Назад в главное меню", callback_data="main_menu")])
            
            await query.edit_message_text(
                "🗑 *Выберите тег для удаления использованных подписок:*",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            logger.error(f"Error getting tags: {str(e)}")
            await query.edit_message_text(
                f"❌ Ошибка при загрузке тегов:\n`{str(e)}`",
                parse_mode='Markdown',
                reply_markup=self._get_back_to_main_keyboard()
            )
        
        return ConversationHandler.END
    
    async def delete_tag_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle tag selection for deletion"""
        query = update.callback_query
        await query.answer()
        
        # Extract tag from callback data
        tag = query.data.replace("delete_tag_", "")
        
        # Show loading message
        await query.edit_message_text(
            f"⏳ Загрузка статистики для тега `{tag}`...",
            parse_mode='Markdown'
        )
        
        try:
            stats = await self.remnawave_service.get_tag_preview_stats(tag)
            
            if stats['total'] == 0:
                await query.edit_message_text(
                    f"❌ Подписки с тегом `{tag}` не найдены.",
                    parse_mode='Markdown',
                    reply_markup=self._get_back_to_main_keyboard()
                )
                return ConversationHandler.END
            
            confirm_keyboard = [
                [InlineKeyboardButton("✅ Подтвердить удаление", callback_data=f"confirm_delete_{tag}")],
                [InlineKeyboardButton("❌ Отменить", callback_data="delete_used")],
                [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]
            ]
            
            await query.edit_message_text(
                f"📊 *Статистика тега:* `{tag}`\n\n"
                f"📈 **Всего подписок:** {stats['total']}\n"
                f"✅ **Активных:** {stats['active']}\n"
                f"❌ **Использованных:** {stats['used']}\n\n"
                f"⚠️ **Будет удалено:** {stats['used']} подписок\n\n"
                f"Подтвердить удаление использованных подписок?",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(confirm_keyboard)
            )
            
        except Exception as e:
            logger.error(f"Error getting tag stats: {str(e)}")
            await query.edit_message_text(
                f"❌ Ошибка при загрузке статистики:\n`{str(e)}`",
                parse_mode='Markdown',
                reply_markup=self._get_back_to_main_keyboard()
            )
        
        return ConversationHandler.END
    
    async def confirm_delete_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle deletion confirmation"""
        query = update.callback_query
        await query.answer()
        
        # Extract tag from callback data
        tag = query.data.replace("confirm_delete_", "")
        
        # Show progress message
        await query.edit_message_text(
            f"⏳ *Удаление использованных подписок...*\n\n"
            f"🏷 Тег: `{tag}`\n\n"
            f"⚠️ Не закрывайте бота, процесс может занять некоторое время.",
            parse_mode='Markdown'
        )
        
        try:
            deleted_count, total_count = await self.remnawave_service.delete_used_subscriptions(tag)
            
            await query.edit_message_text(
                f"✅ *Удаление завершено!*\n\n"
                f"🏷 **Тег:** `{tag}`\n"
                f"🗑 **Удалено:** {deleted_count}\n"
                f"📊 **Всего было:** {total_count}\n"
                f"✅ **Осталось активных:** {total_count - deleted_count}",
                parse_mode='Markdown',
                reply_markup=self._get_back_to_main_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Error deleting used subscriptions: {str(e)}")
            await query.edit_message_text(
                f"❌ *Ошибка при удалении:*\n\n"
                f"`{str(e)}`",
                parse_mode='Markdown',
                reply_markup=self._get_back_to_main_keyboard()
            )
        
        return ConversationHandler.END
    
    async def stats_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Show statistics"""
        query = update.callback_query
        await query.answer()
        
        # Show loading message
        await query.edit_message_text(
            "⏳ Загрузка статистики...",
            reply_markup=None
        )
        
        try:
            tags_with_stats = await self.remnawave_service.get_tags_with_stats()
            
            if not tags_with_stats:
                await query.edit_message_text(
                    "📊 *Статистика промо-кампаний*\n\n"
                    "❌ Промо-кампании не найдены.",
                    parse_mode='Markdown',
                    reply_markup=self._get_back_to_main_keyboard()
                )
                return ConversationHandler.END
            
            stats_text = "📊 *Статистика промо-кампаний:*\n\n"
            
            total_all = 0
            total_active = 0
            total_used = 0
            
            for tag_info in tags_with_stats:
                tag = tag_info['tag']
                total = tag_info['total']
                active = tag_info['active']
                used = tag_info['used']
                
                total_all += total
                total_active += active
                total_used += used
                
                stats_text += (
                    f"🏷 **{tag}:**\n"
                    f"  📈 Всего: {total}\n"
                    f"  ✅ Активных: {active}\n"
                    f"  ❌ Использованных: {used}\n\n"
                )
            
            stats_text += (
                f"📋 **Общая статистика:**\n"
                f"📈 Всего подписок: {total_all}\n"
                f"✅ Активных: {total_active}\n"
                f"❌ Использованных: {total_used}"
            )
            
            await query.edit_message_text(
                stats_text,
                parse_mode='Markdown',
                reply_markup=self._get_back_to_main_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            await query.edit_message_text(
                f"❌ Ошибка при загрузке статистики:\n`{str(e)}`",
                parse_mode='Markdown',
                reply_markup=self._get_back_to_main_keyboard()
            )
        
        return ConversationHandler.END
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle /cancel command"""
        user_id = update.effective_user.id
        
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        
        await update.message.reply_text(
            "❌ Операция отменена.",
            reply_markup=self._get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Произошла ошибка. Попробуйте еще раз.",
                    reply_markup=self._get_main_menu_keyboard()
                )
            except Exception:
                pass