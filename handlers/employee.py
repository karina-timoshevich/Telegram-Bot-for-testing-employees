from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from constants import *
from data_utils import load_data
from handlers.test import ask_test_question


async def choose_specialty_prompt_employee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    specialties = list(data['specialties'].keys())

    if not specialties:
        await update.message.reply_text("На данный момент нет доступных специальностей.")
        return ConversationHandler.END

    specialties_text = "📋 Доступные специальности:\n\n" + \
                       "\n".join([f"{i + 1}. {spec}" for i, spec in enumerate(specialties)]) + \
                       "\n\nВведите номер специальности (или 'назад' для отмены):"

    await update.message.reply_text(specialties_text, reply_markup=ReplyKeyboardRemove())
    context.user_data['specialties_list'] = specialties
    return CHOOSE_SPECIALTY_EMPLOYEE


async def choose_specialty_employee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    specialties = context.user_data.get('specialties_list', [])

    if text.lower() == "назад":
        keyboard = [["Сотрудник", "Наставник"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Возвращаемся в главное меню. Выберите вашу роль:",
            reply_markup=reply_markup
        )
        return CHOOSE_ROLE

    try:
        index = int(text) - 1
        if index < 0 or index >= len(specialties):
            raise ValueError

        specialty = specialties[index]
        context.user_data['specialty'] = specialty
        data = load_data()
        tests = data['specialties'].get(specialty, {}).get('tests', [])
        materials = data['specialties'].get(specialty, {}).get('materials', "Материалы отсутствуют")

        context.user_data['tests'] = tests
        context.user_data['materials'] = materials

        keyboard = [
            ["📚 Получить материалы"],
            ["📝 Пройти аттестацию"],
            ["🔙 Назад"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            f"Вы выбрали специальность: {specialty}\n\nВыберите действие:",
            reply_markup=reply_markup
        )
        return CHOOSE_ACTION_AFTER_SPECIALTY

    except ValueError:
        await update.message.reply_text("Некорректный номер. Пожалуйста, введите число из списка.")
        return CHOOSE_SPECIALTY_EMPLOYEE


async def handle_action_after_specialty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip().lower()

    if choice == "🔙 назад":
        await update.message.reply_text("Возвращаемся к выбору специальности...")
        return await choose_specialty_prompt_employee(update, context)
    elif choice == "📚 получить материалы":
        materials = context.user_data.get('materials', "Материалы отсутствуют.")

        keyboard = [
            ["📝 Пройти аттестацию"],
            ["🔙 К выбору специальности"],
            ["🏠 В главное меню"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            materials,
            reply_markup=reply_markup
        )
        return CHOOSE_AFTER_MATERIALS
    elif choice == "📝 пройти аттестацию":
        tests = context.user_data.get('tests', [])
        if not tests:
            await update.message.reply_text(
                "❗️ Тестов по этой специальности пока нет.",
                reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True)
            )
            return CHOOSE_ACTION_AFTER_SPECIALTY

        context.user_data['test_index'] = 0
        context.user_data['correct_answers'] = 0
        return await ask_test_question(update.message, context)
    else:
        await update.message.reply_text("Пожалуйста, выберите действие из меню.")
        return CHOOSE_ACTION_AFTER_SPECIALTY


async def handle_after_materials(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip().lower()

    # Удаляем эмодзи и лишние пробелы для сравнения
    clean_choice = ''.join(c for c in choice if c.isalpha() or c.isspace()).strip().lower()
    print('CLEAN CHOICE ', clean_choice)
    if clean_choice == "пройти аттестацию":
        tests = context.user_data.get('tests', [])
        if not tests:
            await update.message.reply_text(
                "❗️ Тестов по этой специальности пока нет.",
                reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True)
            )
            return CHOOSE_AFTER_MATERIALS

        context.user_data['test_index'] = 0
        context.user_data['correct_answers'] = 0
        return await ask_test_question(update.message, context)

    elif clean_choice == "получить материалы":
        materials = context.user_data.get('materials', "Материалы отсутствуют.")

        keyboard = [
            ["📝 Пройти аттестацию"],
            ["🔙 К выбору специальности"],
            ["🏠 В главное меню"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            materials,
            reply_markup=reply_markup
        )
        return CHOOSE_AFTER_MATERIALS

    elif clean_choice == "к выбору специальности":
        return await choose_specialty_prompt_employee(update, context)

    elif clean_choice == "в главное меню":
        context.user_data.clear()
        from .common import start
        return await start(update, context)

    else:
        await update.message.reply_text("Пожалуйста, выберите действие из меню.")
        return CHOOSE_AFTER_MATERIALS
