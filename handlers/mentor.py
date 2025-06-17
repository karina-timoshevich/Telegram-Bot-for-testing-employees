from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from constants import *
from data_utils import load_data, save_data
from .common import start


async def enter_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "🔙 Назад":
        context.user_data.clear()
        await update.message.reply_text(
            "Отмена ввода пароля. Выберите роль заново:",
            reply_markup=ReplyKeyboardMarkup(
                [["Сотрудник", "Наставник"]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        return CHOOSE_ROLE

    if text == MENTOR_PASSWORD:
        return await mentor_menu(update, context)
    else:
        keyboard = ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text("❌ Неверный пароль. Попробуйте снова или нажмите «🔙 Назад» для отмены:",
                                        reply_markup=keyboard)
        return ENTER_PASSWORD


async def choose_specialty_mentor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    specialty = update.message.text
    context.user_data['specialty'] = specialty
    await update.message.reply_text(f"📚 Отлично! Вы выбрали специальность: {specialty}.\nСкоро тут будут материалы и тесты.")
    return MENTOR_MENU


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


async def handle_mentor_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()
    if choice == "🔙 Назад":
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
        keyboard.append(["🔙 Назад"])
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