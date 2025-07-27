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
(WAITING_TAG, WAITING_TRAFFIC, WAITING_COUNT, WAITING_CONFIRMATION, WAITING_CONFIRM_DELETE, 
 SELECTING_TAG_DELETE, SHOWING_DELETE_PREVIEW) = range(7)

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
    
    async def _delete_previous_bot_messages(self, chat_id: int, context: ContextTypes.DEFAULT_TYPE, user_session: dict):
        """Delete previous bot messages using stored message IDs"""
        if 'last_message_id' in user_session:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=user_session['last_message_id'])
                del user_session['last_message_id']
            except TelegramError:
                pass
    
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
            "🤖 <b>Добро пожаловать в Remnawave Promo Bot!</b>\n\n"
            "Выберите действие:",
            parse_mode='HTML',
            reply_markup=self._get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    async def main_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle main menu callback"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "🤖 <b>Remnawave Promo Bot</b>\n\n"
            "Выберите действие:",
            parse_mode='HTML',
            reply_markup=self._get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    async def create_promo_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start promo creation process"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        self.user_sessions[user_id] = {}
        
        # Store the message ID for future editing/deletion
        if query.message:
            self.user_sessions[user_id]['last_message_id'] = query.message.message_id
        
        await query.edit_message_text(
            "🏷 <b>Создание промо-кампании</b>\n\n"
            "Введите тег кампании:\n\n"
            "⚠️ <b>Требования к тегу:</b>\n"
            "• Только латинские буквы\n"
            "• Цифры, подчеркивания и дефисы разрешены\n"
            "• Пробелы заменяйте на подчеркивания",
            parse_mode='HTML',
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
        
        # Delete previous bot messages
        if user_id in self.user_sessions:
            await self._delete_previous_bot_messages(update.effective_chat.id, context, self.user_sessions[user_id])
        
        # Normalize tag to meet API requirements
        normalized_tag = self.remnawave_service._normalize_tag(tag)
        
        # Validate normalized tag
        if not self.remnawave_service._validate_tag(normalized_tag):
            # Send new message
            last_bot_message = await update.effective_chat.send_message(
                text="❌ <b>Неверный формат тега!</b>\n\n"
                     "Введите тег кампании:\n\n"
                     "⚠️ <b>Требования к тегу:</b>\n"
                     "• Только ЗАГЛАВНЫЕ латинские буквы\n"
                     "• Цифры и подчеркивания разрешены\n"
                     "• Пробелы будут заменены на подчеркивания\n"
                     "• Строчные буквы будут преобразованы в заглавные",
                parse_mode='HTML',
                reply_markup=self._get_back_to_main_keyboard()
            )
            # Store message for future deletion
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {}
            self.user_sessions[user_id]['last_message_id'] = last_bot_message.message_id
            return WAITING_TAG
        
        # Store normalized tag and ask for traffic limit  
        self.user_sessions[user_id]['tag'] = normalized_tag
        
        # Try to edit the previous message (from create_promo_callback)
        # If we can't edit, send a new message
        if tag != normalized_tag:
            message_text = f"✅ <b>Тег нормализован:</b> <code>{tag}</code> → <code>{normalized_tag}</code>\n\n📊 Выберите лимит трафика:"
        else:
            message_text = f"✅ <b>Тег:</b> <code>{normalized_tag}</code>\n\n📊 Выберите лимит трафика:"
        
        try:
            if 'last_message_id' in self.user_sessions[user_id]:
                # Try to edit existing message
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=self.user_sessions[user_id]['last_message_id'],
                    text=message_text,
                    parse_mode='HTML',
                    reply_markup=self._get_traffic_limit_keyboard()
                )
            else:
                # Send new message and store its ID
                last_bot_message = await update.effective_chat.send_message(
                    text=message_text,
                    parse_mode='HTML',
                    reply_markup=self._get_traffic_limit_keyboard()
                )
                self.user_sessions[user_id]['last_message_id'] = last_bot_message.message_id
        except Exception as e:
            logger.error(f"Failed to update message: {e}")
            # Fallback: send new message
            last_bot_message = await update.effective_chat.send_message(
                text=message_text,
                parse_mode='HTML',
                reply_markup=self._get_traffic_limit_keyboard()
            )
            self.user_sessions[user_id]['last_message_id'] = last_bot_message.message_id
        
        return WAITING_TRAFFIC
    
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
            f"✅ <b>Тег:</b> <code>{tag}</code>\n"
            f"📊 <b>Лимит трафика:</b> {traffic_limit}GB\n\n"
            f"🔢 Введите количество подписок (1-{Config.MAX_SUBSCRIPTIONS_PER_REQUEST}):",
            parse_mode='HTML',
            reply_markup=self._get_back_to_main_keyboard()
        )
        # Message ID stays the same since we're editing
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
            # Try to edit the existing message
            try:
                if 'last_message_id' in self.user_sessions[user_id]:
                    await context.bot.edit_message_text(
                        chat_id=update.effective_chat.id,
                        message_id=self.user_sessions[user_id]['last_message_id'],
                        text=f"❌ <b>Неверное количество!</b>\n\n"
                             f"Введите число от 1 до {Config.MAX_SUBSCRIPTIONS_PER_REQUEST}:",
                        parse_mode='HTML',
                        reply_markup=self._get_back_to_main_keyboard()
                    )
                else:
                    # Fallback: send new message
                    last_bot_message = await update.effective_chat.send_message(
                        text=f"❌ <b>Неверное количество!</b>\n\n"
                             f"Введите число от 1 до {Config.MAX_SUBSCRIPTIONS_PER_REQUEST}:",
                        parse_mode='HTML',
                        reply_markup=self._get_back_to_main_keyboard()
                    )
                    self.user_sessions[user_id]['last_message_id'] = last_bot_message.message_id
            except Exception as e:
                logger.error(f"Failed to edit message for count validation: {e}")
            return WAITING_COUNT
        
        # Store count and show confirmation
        self.user_sessions[user_id]['count'] = count
        tag = self.user_sessions[user_id]['tag']
        traffic_limit = self.user_sessions[user_id]['traffic_limit']
        
        confirm_keyboard = [
            [InlineKeyboardButton("✅ Подтвердить создание", callback_data="confirm_create")],
            [InlineKeyboardButton("❌ Отменить", callback_data="main_menu")]
        ]
        
        confirmation_text = (f"📋 <b>Подтверждение создания:</b>\n\n"
                            f"🏷 <b>Тег:</b> <code>{tag}</code>\n"
                            f"📊 <b>Лимит трафика:</b> {traffic_limit}GB\n"
                            f"🔢 <b>Количество:</b> {count}\n\n"
                            f"Подтвердить создание {count} подписок?")
        
        # Try to edit existing message first
        try:
            if 'last_message_id' in self.user_sessions[user_id]:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=self.user_sessions[user_id]['last_message_id'],
                    text=confirmation_text,
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup(confirm_keyboard)
                )
            else:
                # Fallback: send new message
                last_bot_message = await update.effective_chat.send_message(
                    text=confirmation_text,
                    parse_mode='HTML',
                    reply_markup=InlineKeyboardMarkup(confirm_keyboard)
                )
                self.user_sessions[user_id]['last_message_id'] = last_bot_message.message_id
        except Exception as e:
            logger.error(f"Failed to edit confirmation message: {e}")
            # Fallback: send new message
            last_bot_message = await update.effective_chat.send_message(
                text=confirmation_text,
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup(confirm_keyboard)
            )
            self.user_sessions[user_id]['last_message_id'] = last_bot_message.message_id
        
        return WAITING_CONFIRMATION
    
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
            f"⏳ <b>Создание {count} подписок...</b>\n\n"
            f"🏷 Тег: <code>{tag}</code>\n"
            f"📊 Лимит: {traffic_limit}GB\n\n"
            f"⚠️ Не закрывайте бота, процесс может занять некоторое время.",
            parse_mode='HTML'
        )
        
        try:
            # Create subscriptions
            subscription_links, file_url = await self.remnawave_service.create_promo_users(
                tag, traffic_limit, count
            )
            
            success_count = len(subscription_links)
            
            if success_count > 0:
                result_text = (
                    f"✅ <b>Промо-кампания создана успешно!</b>\n\n"
                    f"🏷 <b>Тег:</b> <code>{tag}</code>\n"
                    f"📊 <b>Лимит трафика:</b> {traffic_limit}GB\n"
                    f"✅ <b>Создано подписок:</b> {success_count}/{count}\n\n"
                )
                
                if file_url:
                    result_text += f"📁 <b>Файл с подписками:</b> <a href='{file_url}'>Скачать</a>\n\n"
                
                # Show first few subscription links as examples
                if len(subscription_links) <= 5:
                    result_text += "🔗 <b>Ссылки на подписки:</b>\n"
                    for i, link in enumerate(subscription_links, 1):
                        result_text += f"<code>{link}</code>\n"
                else:
                    result_text += "🔗 <b>Примеры ссылок:</b>\n"
                    for i, link in enumerate(subscription_links[:3], 1):
                        result_text += f"<code>{link}</code>\n"
                    result_text += f"... и ещё {len(subscription_links) - 3}"
            else:
                result_text = (
                    f"❌ <b>Ошибка создания подписок!</b>\n\n"
                    f"Не удалось создать ни одной подписки.\n"
                    f"Проверьте логи для подробностей."
                )
            
            await query.edit_message_text(
                result_text,
                parse_mode='HTML',
                reply_markup=self._get_back_to_main_keyboard(),
                disable_web_page_preview=True
            )
            
        except Exception as e:
            logger.error(f"Error creating promo campaign: {str(e)}")
            await query.edit_message_text(
                f"❌ <b>Ошибка при создании кампании:</b>\n\n"
                f"<code>{str(e)}</code>",
                parse_mode='HTML',
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
                "🗑 <b>Выберите тег для удаления использованных подписок:</b>",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        except Exception as e:
            logger.error(f"Error getting tags: {str(e)}")
            await query.edit_message_text(
                f"❌ Ошибка при загрузке тегов:\n<code>{str(e)}</code>",
                parse_mode='HTML',
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
            f"⏳ Загрузка статистики для тега <code>{tag}</code>...",
            parse_mode='HTML'
        )
        
        try:
            stats = await self.remnawave_service.get_tag_preview_stats(tag)
            
            if stats['total'] == 0:
                await query.edit_message_text(
                    f"❌ Подписки с тегом <code>{tag}</code> не найдены.",
                    parse_mode='HTML',
                    reply_markup=self._get_back_to_main_keyboard()
                )
                return ConversationHandler.END
            
            confirm_keyboard = [
                [InlineKeyboardButton("✅ Подтвердить удаление", callback_data=f"confirm_delete_{tag}")],
                [InlineKeyboardButton("❌ Отменить", callback_data="delete_used")],
                [InlineKeyboardButton("⬅️ Главное меню", callback_data="main_menu")]
            ]
            
            await query.edit_message_text(
                f"📊 <b>Статистика тега:</b> <code>{tag}</code>\n\n"
                f"📈 <b>Всего подписок:</b> {stats['total']}\n"
                f"✅ <b>Активных:</b> {stats['active']}\n"
                f"❌ <b>Использованных:</b> {stats['used']}\n\n"
                f"⚠️ <b>Будет удалено:</b> {stats['used']} подписок\n\n"
                f"Подтвердить удаление использованных подписок?",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup(confirm_keyboard)
            )
            
        except Exception as e:
            logger.error(f"Error getting tag stats: {str(e)}")
            await query.edit_message_text(
                f"❌ Ошибка при загрузке статистики:\n<code>{str(e)}</code>",
                parse_mode='HTML',
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
            f"⏳ <b>Удаление использованных подписок...</b>\n\n"
            f"🏷 Тег: <code>{tag}</code>\n\n"
            f"⚠️ Не закрывайте бота, процесс может занять некоторое время.",
            parse_mode='HTML'
        )
        
        try:
            deleted_count, total_count = await self.remnawave_service.delete_used_subscriptions(tag)
            
            await query.edit_message_text(
                f"✅ <b>Удаление завершено!</b>\n\n"
                f"🏷 <b>Тег:</b> <code>{tag}</code>\n"
                f"🗑 <b>Удалено:</b> {deleted_count}\n"
                f"📊 <b>Всего было:</b> {total_count}\n"
                f"✅ <b>Осталось активных:</b> {total_count - deleted_count}",
                parse_mode='HTML',
                reply_markup=self._get_back_to_main_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Error deleting used subscriptions: {str(e)}")
            await query.edit_message_text(
                f"❌ <b>Ошибка при удалении:</b>\n\n"
                f"<code>{str(e)}</code>",
                parse_mode='HTML',
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
                    "📊 <b>Статистика промо-кампаний</b>\n\n"
                    "❌ Промо-кампании не найдены.",
                    parse_mode='HTML',
                    reply_markup=self._get_back_to_main_keyboard()
                )
                return ConversationHandler.END
            
            stats_text = "📊 <b>Статистика промо-кампаний:</b>\n\n"
            
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
                    f"🏷 <b>{tag}:</b>\n"
                    f"  📈 Всего: {total}\n"
                    f"  ✅ Активных: {active}\n"
                    f"  ❌ Использованных: {used}\n\n"
                )
            
            stats_text += (
                f"📋 <b>Общая статистика:</b>\n"
                f"📈 Всего подписок: {total_all}\n"
                f"✅ Активных: {total_active}\n"
                f"❌ Использованных: {total_used}"
            )
            
            await query.edit_message_text(
                stats_text,
                parse_mode='HTML',
                reply_markup=self._get_back_to_main_keyboard()
            )
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            await query.edit_message_text(
                f"❌ Ошибка при загрузке статистики:\n<code>{str(e)}</code>",
                parse_mode='HTML',
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
        error_msg = str(context.error)
        logger.error(f"Update {update} caused error {context.error}")
        
        # Check for specific errors
        if "can't parse entities" in error_msg.lower():
            logger.error("Telegram parsing error - likely formatting issue")
        elif "bad request" in error_msg.lower():
            logger.error("Telegram Bad Request - check message formatting")
        
        if update and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Произошла ошибка. Попробуйте еще раз.",
                    reply_markup=self._get_main_menu_keyboard(),
                    parse_mode=None  # Don't use any parsing to avoid errors
                )
            except Exception as e:
                logger.error(f"Failed to send error message: {e}")