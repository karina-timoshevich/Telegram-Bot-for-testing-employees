import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
from dotenv import load_dotenv
import os

import json

DATA_FILE = 'data.json'


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
CHOOSE_SPECIALTY_FOR_TEST_EDIT = 9
EDIT_TEST_MENU = 10
ADD_TEST_QUESTION = 11
ADD_TEST_OPTIONS = 12
ADD_TEST_CORRECT = 13
EDIT_EXISTING_QUESTION = 14
CHOOSE_EDIT_TYPE = 15
EDIT_QUESTION_TEXT = 16
EDIT_QUESTION_OPTIONS = 17
EDIT_QUESTION_CORRECT = 18
DELETE_QUESTION = 19


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
    if choice == "🔙 Назад":
        # Сбрасываем роль и возвращаемся к выбору роли
        context.user_data.clear()
        await update.message.reply_text(
            "Вы вернулись к выбору роли.",
            reply_markup=ReplyKeyboardMarkup(
                [["Сотрудник", "Наставник"]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        return CHOOSE_ROLE

    elif choice == "📚 Редактировать материалы":
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

    elif choice == "📝 Редактировать тесты":
        data = load_data()
        specialties = list(data['specialties'].keys())
        if not specialties:
            await update.message.reply_text("Специальностей пока нет, сначала добавьте их.")
            return MENTOR_MENU

        keyboard = [[spec] for spec in specialties]
        keyboard.append(["🔙 Назад"])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("Выберите специальность для редактирования тестов:", reply_markup=reply_markup)
        return CHOOSE_SPECIALTY_FOR_TEST_EDIT

    elif choice == "🔙 Выйти в главное меню":
        return await start(update, context)

    elif choice == "➕ Добавить специальность":
        return await add_specialty_start(update, context)

    else:
        await update.message.reply_text("Пожалуйста, выберите пункт из меню.")
        return MENTOR_MENU


async def handle_test_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()

    if choice == "➕ Добавить вопрос":
        await update.message.reply_text("✍️ Введите текст вопроса:")
        return ADD_TEST_QUESTION

    elif choice == "✏️ Редактировать вопрос":
        return await choose_question_to_edit(update, context)

    elif choice == "🗑 Удалить вопрос":
        specialty = context.user_data['edit_specialty']
        data = load_data()
        tests = data['specialties'][specialty].get('tests', [])

        if not tests:
            await update.message.reply_text("Нет вопросов для удаления.")
            return await show_test_edit_menu(update, context)

        await update.message.reply_text("Введите номер вопроса, который хотите удалить:")
        return DELETE_QUESTION

    elif choice == "🔙 Назад в меню наставника":
        return await mentor_menu(update, context)

    else:
        await update.message.reply_text("Пожалуйста, выберите действие.")
        return EDIT_TEST_MENU


async def choose_question_to_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    specialty = context.user_data['edit_specialty']
    data = load_data()
    tests = data['specialties'][specialty].get('tests', [])

    try:
        if not tests:
            await update.message.reply_text("Нет вопросов для редактирования.")
            return await show_test_edit_menu(update, context)

        await update.message.reply_text("Введите номер вопроса, который хотите отредактировать:")
        return EDIT_EXISTING_QUESTION
    except Exception as e:
        await update.message.reply_text("Ошибка при выборе вопроса.")
        return EDIT_TEST_MENU


async def choose_edit_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        index = int(update.message.text.strip()) - 1
        specialty = context.user_data['edit_specialty']
        data = load_data()
        tests = data['specialties'][specialty]['tests']
        if index < 0 or index >= len(tests):
            raise ValueError

        context.user_data['edit_index'] = index
        keyboard = [["Вопрос", "Варианты", "Правильный"], ["🔙 Назад"]]
        await update.message.reply_text("Что хотите изменить?",
                                        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return CHOOSE_EDIT_TYPE
    except:
        await update.message.reply_text("Некорректный номер. Попробуйте снова.")
        return EDIT_EXISTING_QUESTION


async def delete_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "🔙 Назад в меню наставника":
        return await show_test_edit_menu(update, context)

    try:
        index = int(text) - 1
        specialty = context.user_data['edit_specialty']
        data = load_data()
        tests = data['specialties'][specialty]['tests']

        if index < 0 or index >= len(tests):
            raise ValueError

        deleted = tests.pop(index)
        save_data(data)

        await update.message.reply_text(f"✅ Вопрос «{deleted['question']}» удалён.")
        return await show_test_edit_menu(update, context)

    except ValueError:
        await update.message.reply_text("Некорректный номер. Попробуйте снова.")
        return DELETE_QUESTION


async def edit_question_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    specialty = context.user_data['edit_specialty']
    index = context.user_data['edit_index']
    data = load_data()
    data['specialties'][specialty]['tests'][index]['question'] = text
    save_data(data)
    await update.message.reply_text("✅ Вопрос обновлён.")
    return await show_test_edit_menu(update, context)


async def edit_question_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().split('\n')
    if len(text) < 2:
        await update.message.reply_text("Минимум два варианта.")
        return EDIT_QUESTION_OPTIONS

    specialty = context.user_data['edit_specialty']
    index = context.user_data['edit_index']
    data = load_data()
    data['specialties'][specialty]['tests'][index]['options'] = text
    save_data(data)
    await update.message.reply_text("✅ Варианты обновлены.")
    return await show_test_edit_menu(update, context)


async def edit_question_correct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        correct = int(update.message.text.strip())
        specialty = context.user_data['edit_specialty']
        index = context.user_data['edit_index']
        options = load_data()['specialties'][specialty]['tests'][index]['options']
        if correct < 1 or correct > len(options):
            raise ValueError

        data = load_data()
        data['specialties'][specialty]['tests'][index]['correct'] = correct
        save_data(data)
        await update.message.reply_text("✅ Правильный ответ обновлён.")
        return await show_test_edit_menu(update, context)
    except:
        await update.message.reply_text("Некорректный номер.")
        return EDIT_QUESTION_CORRECT


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


async def show_test_edit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    specialty = context.user_data['edit_specialty']
    data = load_data()
    tests = data['specialties'][specialty].get('tests', [])

    if not tests:
        text = "🔹 Пока нет ни одного теста."
    else:
        text = "📝 Список текущих вопросов:\n"
        for i, q in enumerate(tests, 1):
            text += f"{i}. {q['question']} (Правильный: {q['correct']})\n"

    keyboard = [
        ["➕ Добавить вопрос", "✏️ Редактировать вопрос", "🗑 Удалить вопрос"],
        ["🔙 Назад в меню наставника"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(text, reply_markup=reply_markup)
    return EDIT_TEST_MENU


async def choose_specialty_for_test_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    specialty = update.message.text.strip()

    if specialty == "🔙 Назад":
        return await mentor_menu(update, context)

    data = load_data()
    if specialty not in data['specialties']:
        await update.message.reply_text("Специальность не найдена. Попробуйте снова.")
        return CHOOSE_SPECIALTY_FOR_TEST_EDIT

    context.user_data['edit_specialty'] = specialty
    context.user_data['test_edit_index'] = None
    return await show_test_edit_menu(update, context)


async def add_test_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_question'] = update.message.text.strip()
    await update.message.reply_text("Введите варианты ответов, разделённые новой строкой (по одному на строку):")
    return ADD_TEST_OPTIONS


async def add_test_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    options = update.message.text.strip().split('\n')
    if len(options) < 2:
        await update.message.reply_text("Минимум два варианта ответа. Попробуйте снова.")
        return ADD_TEST_OPTIONS

    context.user_data['new_options'] = options
    reply_markup = ReplyKeyboardMarkup([[str(i + 1)] for i in range(len(options))], resize_keyboard=True)
    await update.message.reply_text("Выберите номер правильного варианта:", reply_markup=reply_markup)
    return ADD_TEST_CORRECT


async def add_test_correct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        correct_index = int(update.message.text.strip()) - 1
        options = context.user_data['new_options']
        if not (0 <= correct_index < len(options)):
            raise ValueError
    except ValueError:
        await update.message.reply_text("Некорректный номер. Попробуйте снова.")
        return ADD_TEST_CORRECT

    specialty = context.user_data['edit_specialty']
    data = load_data()
    tests = data['specialties'][specialty].get('tests', [])

    new_test = {
        "question": context.user_data['new_question'],
        "options": options,
        "correct": correct_index + 1
    }
    tests.append(new_test)
    data['specialties'][specialty]['tests'] = tests
    save_data(data)

    await update.message.reply_text("✅ Вопрос успешно добавлен!", reply_markup=ReplyKeyboardRemove())
    return await show_test_edit_menu(update, context)


async def edit_question_text_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите новый текст вопроса:")
    return EDIT_QUESTION_TEXT


async def edit_question_options_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите новые варианты ответа, по одному на строку:")
    return EDIT_QUESTION_OPTIONS


async def edit_question_correct_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    specialty = context.user_data['edit_specialty']
    index = context.user_data['edit_index']
    data = load_data()
    options = data['specialties'][specialty]['tests'][index]['options']
    keyboard = ReplyKeyboardMarkup([[str(i + 1)] for i in range(len(options))], resize_keyboard=True)
    await update.message.reply_text("Выберите номер правильного варианта:", reply_markup=keyboard)
    return EDIT_QUESTION_CORRECT


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_role)],
            ENTER_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_password)],
            CHOOSE_SPECIALTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_specialty)],
            MENTOR_MENU: [ MessageHandler(filters.Regex("^🔙 Назад$"), handle_mentor_menu),MessageHandler(filters.TEXT & ~filters.COMMAND, handle_mentor_menu)],
            ADD_SPECIALTY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_specialty_name)],
            CHOOSE_SPECIALTY_FOR_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_specialty_for_edit)],
            EDIT_MATERIALS_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_edited_materials)],
            CHOOSE_SPECIALTY_FOR_TEST_EDIT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, choose_specialty_for_test_edit)],
            EDIT_TEST_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_test_menu)],
            ADD_TEST_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_test_question)],
            ADD_TEST_OPTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_test_options)],
            ADD_TEST_CORRECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_test_correct)],
            EDIT_EXISTING_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_edit_type)],
            CHOOSE_EDIT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: {
                "вопрос": edit_question_text_prompt,
                "варианты": edit_question_options_prompt,
                "правильный": edit_question_correct_prompt
            }.get(u.message.text.strip().lower(), lambda *_: u.message.reply_text("Выберите один из вариантов."))(u, c))],
            EDIT_QUESTION_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_question_text)],
            EDIT_QUESTION_OPTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_question_options)],
            EDIT_QUESTION_CORRECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_question_correct)],
            DELETE_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_question)],

        },
        fallbacks=[],
    )

    app.add_handler(conv_handler)

    print("Бот запущен!")
    app.run_polling()


if __name__ == '__main__':
    main()
