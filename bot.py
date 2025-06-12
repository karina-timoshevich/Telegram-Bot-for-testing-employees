import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
from dotenv import load_dotenv
import os

import json

DATA_FILE = 'data.json'  # имя файла с данными


def load_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"specialties": {}}
    except json.JSONDecodeError:
        return {"specialties": {}}


def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
MENTOR_PASSWORD = os.getenv("ADMIN_PASSWORD")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

CHOOSE_ROLE, ENTER_PASSWORD, CHOOSE_SPECIALTY, MENTOR_MENU, EDIT_MATERIALS, EDIT_TESTS = range(6)
ADD_SPECIALTY_NAME = 6
CHOOSE_SPECIALTY_FOR_EDIT = 7
EDIT_MATERIALS_INPUT = 8


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(
        [["Сотрудник", "Наставник"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await update.message.reply_text(
        "Привет! Выберите вашу роль:",
        reply_markup=reply_markup
    )
    return CHOOSE_ROLE


async def choose_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = update.message.text.lower()
    context.user_data['role'] = role

    if role == "наставник":
        await update.message.reply_text(
            "Введите пароль для доступа к режиму наставника:",
            reply_markup=ReplyKeyboardRemove()
        )
        return ENTER_PASSWORD
    elif role == "сотрудник":
        return await choose_specialty_prompt(update, context)
    else:
        await update.message.reply_text("Пожалуйста, выберите одну из ролей.")
        return CHOOSE_ROLE


async def enter_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    if password == MENTOR_PASSWORD:
        return await mentor_menu(update, context)
    else:
        await update.message.reply_text("❌ Неверный пароль. Попробуйте снова:")
        return ENTER_PASSWORD


async def choose_specialty_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    specialties = ["Продажи", "Маркетинг", "IT"]
    reply_markup = ReplyKeyboardMarkup(
        [[spec] for spec in specialties],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await update.message.reply_text(
        "Выберите вашу специальность:",
        reply_markup=reply_markup
    )
    return CHOOSE_SPECIALTY


async def choose_specialty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    specialty = update.message.text
    context.user_data['specialty'] = specialty
    await update.message.reply_text(
        f"📚 Отлично! Вы выбрали специальность: {specialty}.\nСкоро тут будут материалы и тесты.")
    return ConversationHandler.END


async def mentor_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📚 Редактировать материалы")],
        [KeyboardButton("📝 Редактировать тесты")],
        [KeyboardButton("➕ Добавить специальность")],
        [KeyboardButton("🔙 Назад")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Вы в меню наставника. Выберите действие:", reply_markup=reply_markup)
    return MENTOR_MENU


async def choose_specialty_for_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    specialty = update.message.text.strip()

    if specialty == "🔙 Назад":
        return await mentor_menu(update, context)

    data = load_data()
    if specialty not in data['specialties']:
        await update.message.reply_text("Специальность не найдена. Попробуйте еще раз.")
        return CHOOSE_SPECIALTY_FOR_EDIT

    context.user_data['edit_specialty'] = specialty
    materials = data['specialties'][specialty].get('materials', '')
    await update.message.reply_text(
        f"Текущие материалы по «{specialty}»:\n\n{materials if materials else 'Материалы отсутствуют.'}\n\n"
        "✍️ Введите новые материалы (или нажмите «🔙 Назад», чтобы отменить редактирование):",
        reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True)
    )
    return EDIT_MATERIALS_INPUT


async def save_edited_materials(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_text = update.message.text.strip()

    if new_text == "🔙 Назад":
        await update.message.reply_text("Редактирование отменено.")

        data = load_data()
        specialties = list(data['specialties'].keys())
        keyboard = [[spec] for spec in specialties]
        keyboard.append(["🔙 Назад"])  # Не забудь кнопку назад
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(
            "Выберите специальность для редактирования материалов:",
            reply_markup=reply_markup
        )
        return CHOOSE_SPECIALTY_FOR_EDIT

    specialty = context.user_data.get('edit_specialty')
    if not specialty:
        await update.message.reply_text("Произошла ошибка, попробуйте снова.")
        return MENTOR_MENU

    data = load_data()
    data['specialties'][specialty]['materials'] = new_text
    save_data(data)

    await update.message.reply_text(f"✅ Материалы по «{specialty}» успешно обновлены!",
                                    reply_markup=ReplyKeyboardRemove())
    return await mentor_menu(update, context)


async def handle_mentor_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()

    if choice == "📚 Редактировать материалы":
        data = load_data()
        specialties = list(data['specialties'].keys())
        if not specialties:
            await update.message.reply_text("Специальностей пока нет, добавьте их сначала.")
            return MENTOR_MENU

        keyboard = [[spec] for spec in specialties]
        keyboard.append(["🔙 Назад"])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Выберите специальность для редактирования материалов:",
                                        reply_markup=reply_markup)
        return CHOOSE_SPECIALTY_FOR_EDIT

    elif choice == "❓ Редактировать тесты":
        await update.message.reply_text("🛠 Скоро тут будет редактирование тестов (тоже заглушка).")
        return MENTOR_MENU

    elif choice == "🔙 Выйти в главное меню":
        return await start(update, context)

    elif choice == "➕ Добавить специальность":
        return await add_specialty_start(update, context)

    else:
        await update.message.reply_text("Пожалуйста, выберите пункт из меню.")
        return MENTOR_MENU


async def add_specialty_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите название новой специальности:", reply_markup=ReplyKeyboardRemove())
    return ADD_SPECIALTY_NAME


async def add_specialty_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    specialty_name = update.message.text.strip()
    data = load_data()

    if specialty_name in data['specialties']:
        await update.message.reply_text("Такая специальность уже существует, попробуйте другое название.")
        return ADD_SPECIALTY_NAME

    data['specialties'][specialty_name] = {
        "materials": "",
        "tests": []
    }
    save_data(data)
    await update.message.reply_text(f"Специальность «{specialty_name}» успешно добавлена! ✅")
    return await mentor_menu(update, context)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_role)],
            ENTER_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_password)],
            CHOOSE_SPECIALTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_specialty)],
            MENTOR_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mentor_menu)],
            ADD_SPECIALTY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_specialty_name)],
            CHOOSE_SPECIALTY_FOR_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_specialty_for_edit)],
            EDIT_MATERIALS_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_edited_materials)],
        },
        fallbacks=[],
    )

    app.add_handler(conv_handler)

    print("Бот запущен!")
    app.run_polling()


if __name__ == '__main__':
    main()
