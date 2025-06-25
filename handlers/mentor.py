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
    await update.message.reply_text(f"📚 Отлично! Вы выбрали специальность: {specialty}.\nСкоро тут будут материалы и "
                                    f"тесты.")
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

        specialties_text = "📋 Список доступных специальностей:\n\n" + \
                           "\n".join([f"{i + 1}. {spec}" for i, spec in enumerate(specialties)]) + \
                           "\n\nВведите номер специальности для редактирования материалов:"

        keyboard = ReplyKeyboardMarkup(
            [["🔙 Назад"]],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await update.message.reply_text(specialties_text, reply_markup=keyboard)
        context.user_data['specialties_list'] = specialties
        return CHOOSE_SPECIALTY_FOR_EDIT

    elif choice == "📝 Редактировать тесты":
        data = load_data()
        specialties = list(data['specialties'].keys())
        if not specialties:
            await update.message.reply_text("Специальностей пока нет, сначала добавьте их.")
            return MENTOR_MENU

        specialties_text = "📋 Список доступных специальностей:\n\n" + \
                           "\n".join([f"{i + 1}. {spec}" for i, spec in enumerate(specialties)]) + \
                           "\n\nВведите номер специальности для редактирования тестов:"

        keyboard = ReplyKeyboardMarkup(
            [["🔙 Назад"]],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await update.message.reply_text(specialties_text, reply_markup=keyboard)
        context.user_data['specialties_list'] = specialties
        return CHOOSE_SPECIALTY_FOR_TEST_EDIT

    elif choice == "🔙 Выйти в главное меню":
        return await start(update, context)

    elif choice == "➕ Добавить специальность":
        return await add_specialty_start(update, context)

    else:
        await update.message.reply_text("Пожалуйста, выберите пункт из меню.")
        return MENTOR_MENU


async def add_specialty_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["➕ Новая специальность"], ["📂 Подвид существующей"], ["🔙 Назад"]]
    await update.message.reply_text("Вы хотите добавить новую специальность или подвид?",
                                    reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True,
                                                                     one_time_keyboard=True))
    return ADD_SPECIALTY_TYPE


async def add_specialty_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()
    if choice == "➕ Новая специальность":
        context.user_data["add_type"] = "main"
        await update.message.reply_text("Введите название новой специальности:", reply_markup=ReplyKeyboardRemove())
        return ADD_SPECIALTY_NAME
    elif choice == "📂 Подвид существующей":
        data = load_data()
        specialties = list(data['specialties'].keys())
        if not specialties:
            await update.message.reply_text("Нет существующих специальностей. Добавьте основную сначала.")
            return await mentor_menu(update, context)

        specialties_text = "📋 Список доступных специальностей:\n\n" + \
                           "\n".join([f"{i + 1}. {spec}" for i, spec in enumerate(specialties)]) + \
                           "\n\nВведите номер родительской специальности:"

        await update.message.reply_text(specialties_text, reply_markup=ReplyKeyboardRemove())
        context.user_data['specialties_list'] = specialties  # Сохраняем список для проверки
        return CHOOSE_PARENT_SPECIALTY

    elif choice == "🔙 Назад":
        return await mentor_menu(update, context)

    else:
        await update.message.reply_text("Выберите один из предложенных вариантов.")
        return ADD_SPECIALTY_TYPE


async def choose_parent_specialty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    specialties = context.user_data.get('specialties_list', [])

    if text.lower() == "назад":
        return await add_specialty_start(update, context)

    try:
        index = int(text) - 1
        if index < 0 or index >= len(specialties):
            raise ValueError

        parent = specialties[index]
        data = load_data()
        if parent not in data['specialties']:
            await update.message.reply_text("Такой специальности нет. Попробуйте снова.")
            return CHOOSE_PARENT_SPECIALTY

        context.user_data["add_type"] = "sub"
        context.user_data["parent"] = parent
        await update.message.reply_text(f"Введите название подвида для специальности «{parent}»:",
                                        reply_markup=ReplyKeyboardRemove())
        return ADD_SPECIALTY_NAME

    except ValueError:
        await update.message.reply_text("Некорректный номер. Пожалуйста, введите число из списка.")
        return CHOOSE_PARENT_SPECIALTY


async def add_specialty_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    data = load_data()

    if context.user_data.get("add_type") == "sub":
        parent = context.user_data["parent"]
        full_name = f"{parent}::{name}"
    else:
        full_name = name

    if full_name in data['specialties']:
        await update.message.reply_text("Такая специальность уже существует. Введите другое название.")
        return ADD_SPECIALTY_NAME

    data['specialties'][full_name] = {
        "materials": "",
        "tests": []
    }

    save_data(data)
    await update.message.reply_text(f"✅ Специальность «{full_name}» успешно добавлена!")
    return await mentor_menu(update, context)


async def choose_specialty_for_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    specialties = context.user_data.get('specialties_list', [])

    if text == "🔙 Назад":
        return await mentor_menu(update, context)

    try:
        index = int(text) - 1
        if index < 0 or index >= len(specialties):
            raise ValueError

        specialty = specialties[index]
        data = load_data()
        if specialty not in data['specialties']:
            await update.message.reply_text("Специальность не найдена. Попробуйте еще раз.")
            return CHOOSE_SPECIALTY_FOR_EDIT

        context.user_data['edit_specialty'] = specialty
        materials = data['specialties'][specialty].get('materials', '')
        await update.message.reply_text(
            f"Текущие материалы по «{specialty}»:\n\n{materials if materials else 'Материалы отсутствуют.'}\n\n"
            "✍️ Введите новые материалы или нажмите кнопку ниже для отмены:",
            reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True, one_time_keyboard=True)
        )

        return EDIT_MATERIALS_INPUT

    except ValueError:
        await update.message.reply_text("Некорректный номер. Пожалуйста, введите число из списка.")
        return CHOOSE_SPECIALTY_FOR_EDIT


async def save_edited_materials(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_text = update.message.text.strip()

    if new_text.lower() == "назад":
        await update.message.reply_text("Редактирование отменено.")

        data = load_data()
        specialties = list(data['specialties'].keys())
        specialties_text = "📋 Список доступных специальностей:\n\n" + \
                           "\n".join([f"{i + 1}. {spec}" for i, spec in enumerate(specialties)]) + \
                           "\n\nВведите номер специальности для редактирования материалов:"

        keyboard = ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(specialties_text, reply_markup=keyboard)
        context.user_data['specialties_list'] = specialties
        return CHOOSE_SPECIALTY_FOR_EDIT

    specialty = context.user_data.get('edit_specialty')
    if not specialty:
        await update.message.reply_text("Произошла ошибка, попробуйте снова.")
        return MENTOR_MENU

    data = load_data()
    data['specialties'][specialty]['materials'] = new_text
    save_data(data)

    await update.message.reply_text(f"✅ Материалы по «{specialty}» успешно обновлены!")
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

    if not tests:
        await update.message.reply_text("Нет вопросов для редактирования.")
        return await show_test_edit_menu(update, context)

    questions_text = "📝 Список вопросов для редактирования:\n\n"
    for i, q in enumerate(tests):
        question = f"{i + 1}. {q['question']}\n"
        options = "\n".join([f"   {j + 1}) {opt}" for j, opt in enumerate(q['options'])])
        correct = q['correct']
        correct_str = ", ".join(str(c) for c in correct) if isinstance(correct, list) else str(correct)
        block = f"{question}{options}\n   ✅ Правильные: {correct_str}\n\n"
        questions_text += block

    questions_text += "Введите номер вопроса, который хотите отредактировать:"
    keyboard = ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(questions_text, reply_markup=keyboard)
    return EDIT_EXISTING_QUESTION


async def choose_edit_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "🔙 Назад":
        return await mentor_menu(update, context)

    try:
        index = int(text) - 1
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
        await update.message.reply_text("Некорректный номер. Попробуйте снова или нажмите «🔙 Назад».")
        return EDIT_EXISTING_QUESTION


async def delete_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    specialty = context.user_data['edit_specialty']
    data = load_data()
    tests = data['specialties'][specialty].get('tests', [])

    if not tests:
        await update.message.reply_text("Нет вопросов для удаления.")
        return await show_test_edit_menu(update, context)

    text = "🗑 Список вопросов для удаления:\n\n"
    for i, q in enumerate(tests):
        question = f"{i + 1}. {q['question']}\n"
        options = "\n".join([f"   {j + 1}) {opt}" for j, opt in enumerate(q['options'])])
        correct = q['correct']
        correct_str = ", ".join(str(c) for c in correct) if isinstance(correct, list) else str(correct)
        text += f"{question}{options}\n   ✅ Правильные: {correct_str}\n\n"

    text += "Введите номер вопроса, который хотите удалить:"
    await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
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
        raw = update.message.text.strip()
        indexes = [int(x.strip()) - 1 for x in raw.replace(',', ' ').split()]
        specialty = context.user_data['edit_specialty']
        index = context.user_data['edit_index']
        options = load_data()['specialties'][specialty]['tests'][index]['options']

        if any(i < 0 or i >= len(options) for i in indexes):
            raise ValueError

        data = load_data()
        data['specialties'][specialty]['tests'][index]['correct'] = [i + 1 for i in indexes]
        save_data(data)

        await update.message.reply_text("✅ Правильные ответы обновлены.")
        return await show_test_edit_menu(update, context)

    except:
        await update.message.reply_text("Некорректный ввод. Введите номера через пробел или запятую.")
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
            correct_answers = q['correct']
            if isinstance(correct_answers, list):
                correct_text = ", ".join(str(c) for c in correct_answers)
            else:
                correct_text = str(correct_answers)
            text += f"{i}. {q['question']} (Правильные: {correct_text})\n"

    keyboard = [
        ["➕ Добавить вопрос", "✏️ Редактировать вопрос", "🗑 Удалить вопрос"],
        ["🔙 Назад в меню наставника"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(text, reply_markup=reply_markup)
    return EDIT_TEST_MENU


async def choose_specialty_for_test_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    specialties = context.user_data.get('specialties_list', [])

    if text == "🔙 Назад":
        return await mentor_menu(update, context)

    try:
        index = int(text) - 1
        if index < 0 or index >= len(specialties):
            raise ValueError

        specialty = specialties[index]
        data = load_data()
        if specialty not in data['specialties']:
            await update.message.reply_text("Специальность не найдена. Попробуйте еще раз.")
            return CHOOSE_SPECIALTY_FOR_TEST_EDIT

        context.user_data['edit_specialty'] = specialty
        context.user_data['test_edit_index'] = None
        return await show_test_edit_menu(update, context)

    except ValueError:
        await update.message.reply_text("Некорректный номер. Пожалуйста, введите число из списка.")
        return CHOOSE_SPECIALTY_FOR_TEST_EDIT


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
    await update.message.reply_text(
        "Введите номера правильных ответов через пробел или запятую (например: `1 3` или `2,4`):",
        reply_markup=ReplyKeyboardRemove()
    )
    return ADD_TEST_CORRECT



async def add_test_correct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        raw = update.message.text.strip()
        indexes = [int(x.strip()) - 1 for x in raw.replace(',', ' ').split()]
        options = context.user_data['new_options']

        if any(i < 0 or i >= len(options) for i in indexes):
            raise ValueError
    except ValueError:
        await update.message.reply_text("Некорректный ввод. Введите номера через пробел или запятую.")
        return ADD_TEST_CORRECT

    specialty = context.user_data['edit_specialty']
    data = load_data()
    tests = data['specialties'][specialty].get('tests', [])

    new_test = {
        "question": context.user_data['new_question'],
        "options": options,
        "correct": [i + 1 for i in indexes]
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
    await update.message.reply_text(
        "Введите номера правильных ответов через пробел или запятую:",
        reply_markup=ReplyKeyboardRemove()
    )

    return EDIT_QUESTION_CORRECT
