from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from constants import *
from data_utils import load_data, save_data
from handlers.reports import send_full_report
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
        [KeyboardButton("🗂 УПД")],
        [KeyboardButton("🧪 TWI – производственное обучение")],
        [KeyboardButton("📊 Сводный отчёт")],
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
        return await choose_specialty_for_mentor_file(update, context, file_key="attachments", display_name="материалы")
    elif choice == "🗂 УПД":
        return await choose_specialty_for_mentor_file(update, context, file_key="upd_attachments", display_name="УПД")
    elif choice == "🧪 TWI – производственное обучение":
        return await choose_specialty_for_mentor_file(update, context, file_key="twi_attachments", display_name="TWI")
    elif choice == "📊 Сводный отчёт":
        context.user_data.pop("in_specialty_correction", None)
        return await send_full_report(update, context, role="mentor")
    else:
        await update.message.reply_text("Пожалуйста, выберите пункт из меню.")
        return MENTOR_MENU

async def choose_specialty_for_mentor_file(update: Update, context: ContextTypes.DEFAULT_TYPE, file_key: str, display_name: str):
    data = load_data()
    specialties = list(data["specialties"].keys())

    if not specialties:
        await update.message.reply_text("❌ Нет доступных специальностей.")
        return MENTOR_MENU

    text = f"📋 Доступные специальности для {display_name}:\n\n" + \
           "\n".join([f"{i + 1}. {spec}" for i, spec in enumerate(specialties)]) + \
           "\n\nВведите номер специальности или нажмите «🔙 Назад»."

    keyboard = ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True, one_time_keyboard=True)

    context.user_data['specialties_list'] = specialties
    context.user_data['mentor_file_key'] = file_key
    context.user_data['mentor_display_name'] = display_name

    await update.message.reply_text(text, reply_markup=keyboard)
    return CHOOSE_SPECIALTY_FOR_MENTOR_FILE


async def send_files_for_specialty_to_mentor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "🔙 Назад":
        return await mentor_menu(update, context)

    specialties = context.user_data.get("specialties_list", [])
    try:
        index = int(text) - 1
        if index < 0 or index >= len(specialties):
            raise ValueError

        specialty = specialties[index]
        file_key = context.user_data.get("mentor_file_key")
        display_name = context.user_data.get("mentor_display_name")

        data = load_data()
        attachments = data["specialties"].get(specialty, {}).get(file_key, [])

        if not attachments:
            await update.message.reply_text(f"📭 Для специальности «{specialty}» нет файлов {display_name}.")
        else:
            await update.message.reply_text(f"📂 {display_name} для «{specialty}»:")
            for doc in attachments:
                await update.message.reply_document(doc["file_id"], filename=doc["file_name"])

        return await mentor_menu(update, context)

    except ValueError:
        await update.message.reply_text("Неверный номер. Попробуйте ещё раз.")
        return CHOOSE_SPECIALTY_FOR_MENTOR_FILE
