from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from constants import *
from data_utils import load_data
from handlers.common import filter_specialties_with_subtypes
from handlers.test import ask_test_question


async def choose_specialty_prompt_employee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    specialties = filter_specialties_with_subtypes(data)

    if not specialties:
        await update.message.reply_text("На данный момент нет доступных специальностей.")
        return ConversationHandler.END

    specialties_text = "📋 Доступные специальности:\n\n" + \
                       "\n".join([f"{i + 1}. {spec}" for i, spec in enumerate(specialties)]) + \
                       "\n\nВыберите номер специальности или нажмите «🔙 Назад»:"

    keyboard = ReplyKeyboardMarkup(
        [["🔙 Назад"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(specialties_text, reply_markup=keyboard)
    context.user_data['specialties_list'] = specialties
    return CHOOSE_SPECIALTY_EMPLOYEE


async def choose_specialty_employee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    specialties = context.user_data.get('specialties_list', [])

    if text == "🔙 Назад":
        keyboard = [["Ученик", "Наставник", "Админ"]]
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
            ["🧪 TWI – производственное обучение"],
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
    choice = update.message.text.strip()

    if choice == "🔙 Назад":
        await update.message.reply_text("Возвращаемся к выбору специальности...",
                                     reply_markup=ReplyKeyboardRemove())
        return await choose_specialty_prompt_employee(update, context)

    elif choice == "📚 Получить материалы":
        materials = context.user_data.get('materials', "Материалы отсутствуют.")
        specialty = context.user_data.get('specialty')
        data = load_data()
        attachments = data['specialties'][specialty].get("attachments", [])

        text_to_send = materials.strip() if materials.strip() else "Материалы"
        await update.message.reply_text(text_to_send)

        if attachments:
            for doc in attachments:
                await update.message.reply_document(doc["file_id"], filename=doc["file_name"])
        else:
            await update.message.reply_text("📭 Прикрепленные файлы пока отсутствуют.")

        keyboard = [
            ["🧪 TWI – производственное обучение"],
            ["📝 Пройти аттестацию"],
            ["🔙 К выбору специальности"],
            ["🏠 В главное меню"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)
        return CHOOSE_AFTER_MATERIALS

    elif choice == "🧪 TWI – производственное обучение":
        specialty = context.user_data.get("specialty")
        data = load_data()
        attachments = data['specialties'].get(specialty, {}).get("twi_attachments", [])

        if attachments:
            await update.message.reply_text(f"📂 TWI материалы по специальности: {specialty}")
            for doc in attachments:
                await update.message.reply_document(doc["file_id"], filename=doc["file_name"])
        else:
            await update.message.reply_text("📭 TWI материалы отсутствуют.")

        keyboard = [
            ["📚 Получить материалы"],
            ["🧪 TWI – производственное обучение"],
            ["📝 Пройти аттестацию"],
            ["🔙 К выбору специальности"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Выберите следующее действие:", reply_markup=reply_markup)
        return CHOOSE_ACTION_AFTER_SPECIALTY

    elif choice == "📝 Пройти аттестацию":
        tests = context.user_data.get('tests', [])
        if not tests:
            keyboard = [
                ["📚 Получить материалы"],
                ["📝 Пройти аттестацию"],
                ["🧪 TWI – производственное обучение"],
                ["🔙 К выбору специальности"],
                ["🏠 В главное меню"]
            ]
            await update.message.reply_text(
                "❗️ Тестов по этой специальности пока нет.\n\nВыберите другое действие:",
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )
            return CHOOSE_ACTION_AFTER_SPECIALTY
        return await ask_employee_fio(update, context)

    elif choice == "🔙 К выбору специальности":
        if 'materials_sent' in context.user_data:
            del context.user_data['materials_sent']
        return await choose_specialty_prompt_employee(update, context)

    elif choice == "🏠 В главное меню":
        context.user_data.clear()
        from .common import start
        return await start(update, context)

    else:
        await update.message.reply_text("Пожалуйста, выберите действие из меню.")
        return CHOOSE_ACTION_AFTER_SPECIALTY


async def handle_after_materials(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()

    if choice == "📝 Пройти аттестацию":
        tests = context.user_data.get('tests', [])
        if not tests:
            keyboard = [
                ["📚 Получить материалы"],
                ["🧪 TWI – производственное обучение"],
                ["📝 Пройти аттестацию"],
                ["🔙 К выбору специальности"],
                ["🏠 В главное меню"]
            ]
            await update.message.reply_text(
                "❗️ Тестов по этой специальности пока нет.\n\nВыберите другое действие:",
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )
            return CHOOSE_ACTION_AFTER_SPECIALTY
        return await ask_employee_fio(update, context)

    elif choice == "📚 Получить материалы":
        materials = context.user_data.get('materials', "Материалы отсутствуют.")
        specialty = context.user_data.get('specialty')
        data = load_data()
        attachments = data['specialties'][specialty].get("attachments", [])

        text_to_send = materials.strip() if materials.strip() else "Материалы"
        await update.message.reply_text(text_to_send)

        if attachments:
            for doc in attachments:
                await update.message.reply_document(doc["file_id"], filename=doc["file_name"])
        else:
            await update.message.reply_text("📭 Прикрепленные файлы пока отсутствуют.")

        keyboard = [
            ["🧪 TWI – производственное обучение"],
            ["📝 Пройти аттестацию"],
            ["🔙 К выбору специальности"],
            ["🏠 В главное меню"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)
        return CHOOSE_AFTER_MATERIALS

    elif choice == "🧪 TWI – производственное обучение":
        specialty = context.user_data.get("specialty")
        data = load_data()
        attachments = data['specialties'].get(specialty, {}).get("twi_attachments", [])

        if attachments:
            await update.message.reply_text(f"📂 TWI материалы по специальности: {specialty}")
            for doc in attachments:
                await update.message.reply_document(doc["file_id"], filename=doc["file_name"])
        else:
            await update.message.reply_text("📭 TWI материалы отсутствуют.")

        keyboard = [
            ["📚 Получить материалы"],
            ["🧪 TWI – производственное обучение"],
            ["📝 Пройти аттестацию"],
            ["🔙 К выбору специальности"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Выберите следующее действие:", reply_markup=reply_markup)
        return CHOOSE_AFTER_MATERIALS

    elif choice == "🔙 К выбору специальности":
        if 'materials_sent' in context.user_data:
            del context.user_data['materials_sent']
        return await choose_specialty_prompt_employee(update, context)

    elif choice == "🏠 В главное меню":
        context.user_data.clear()
        from .common import start
        return await start(update, context)

    else:
        await update.message.reply_text("Пожалуйста, выберите действие из меню.")
        return CHOOSE_AFTER_MATERIALS


async def ask_employee_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🔙 Назад"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(
        "Пожалуйста, введите ваше ФИО для начала теста (или нажмите «🔙 Назад»):",
        reply_markup=reply_markup
    )
    return ENTER_EMPLOYEE_NAME


async def receive_employee_fio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "🔙 Назад":
        keyboard = [
            ["📚 Получить материалы"],
            ["🧪 TWI – производственное обучение"],
            ["📝 Пройти аттестацию"],
            ["🔙 К выбору специальности"],
            ["🏠 В главное меню"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)
        return CHOOSE_AFTER_MATERIALS

    if not text:
        await update.message.reply_text("ФИО не может быть пустым, введите, пожалуйста, корректно.")
        return ENTER_EMPLOYEE_NAME

    context.user_data['employee_fio'] = text
    context.user_data['telegram_username'] = update.message.from_user.username or "—"
    context.user_data['telegram_id'] = update.message.from_user.id

    context.user_data['test_index'] = 0
    context.user_data['correct_answers'] = 0

    await update.message.reply_text(f"Спасибо, {text}. Начинаем тестирование!", reply_markup=ReplyKeyboardRemove())
    from handlers.test import ask_test_question
    return await ask_test_question(update.message, context)

