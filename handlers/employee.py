from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from constants import *
from data_utils import load_data
from handlers.test import ask_test_question


async def choose_specialty_employee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    specialty = update.message.text
    context.user_data['specialty'] = specialty
    data = load_data()
    tests = data['specialties'].get(specialty, {}).get('tests', [])
    materials = data['specialties'].get(specialty, {}).get('materials', "Материалы отсутствуют")
    context.user_data['tests'] = tests
    context.user_data['materials'] = materials

    keyboard = [["📚 Получить материалы", "📝 Пройти аттестацию"]]
    await update.message.reply_text(
        f"Вы выбрали специальность «{specialty}». Что хотите сделать дальше?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )

    return CHOOSE_ACTION_AFTER_SPECIALTY


async def handle_action_after_specialty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text

    if choice == "📚 Получить материалы":
        materials = context.user_data.get('materials', "Материалы отсутствуют.")
        await update.message.reply_text(materials, reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return ConversationHandler.END

    elif choice == "📝 Пройти аттестацию":
        tests = context.user_data.get('tests', [])
        if not tests:
            await update.message.reply_text("❗️ Тестов по этой специальности пока нет.",
                                            reply_markup=ReplyKeyboardRemove())
            context.user_data.clear()
            return await ask_test_question(update.message, context)

        context.user_data['test_index'] = 0
        context.user_data['correct_answers'] = 0
        return await ask_test_question(update.message, context)

    else:
        await update.message.reply_text("Пожалуйста, выберите вариант из меню.")
        return CHOOSE_ACTION_AFTER_SPECIALTY
