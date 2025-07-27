from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from constants import *
from data_utils import load_data, save_data, send_full_report
from .common import start


async def enter_password_mentor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "🔙 Назад":
        context.user_data.clear()
        await update.message.reply_text(
            "Отмена ввода пароля. Выберите роль заново:",
            reply_markup=ReplyKeyboardMarkup(
                [["Ученик", "Наставник", "Админ"]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        return CHOOSE_ROLE

    if text == MENTOR_PASSWORD:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
        except:
            pass
        return await mentor_menu(update, context)

    else:
        keyboard = ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("❌ Неверный пароль. Попробуйте снова или нажмите «🔙 Назад» для отмены:",
                                        reply_markup=keyboard)
        return ENTER_PASSWORD_MENTOR


async def mentor_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📚 Теоретические материалы")],
        [KeyboardButton("🗂 Учебные планы")],
        [KeyboardButton("🧪 Практические задания")],
        [KeyboardButton("🔙 Назад")]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Вы в меню наставника. Выберите действие:", reply_markup=reply_markup)
    return MENTOR_MENU


async def handle_mentor_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()
    if choice == "🔙 Назад":
        context.user_data.clear()
        await update.message.reply_text(
            "Вы вернулись к выбору роли.",
            reply_markup=ReplyKeyboardMarkup(
                [["Ученик", "Наставник", "Админ"]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        return CHOOSE_ROLE
    elif choice == "📚 Теоретические материалы":
        file_path = "mentor_content/theory.txt"
    elif choice == "🗂 Учебные планы":
        file_path = "mentor_content/plans.txt"
    elif choice == "🧪 Практические задания":
        file_path = "mentor_content/practice.txt"
    else:
        await update.message.reply_text("Пожалуйста, выберите пункт из меню.")
        return MENTOR_MENU
