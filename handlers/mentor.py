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
        context.user_data['specialties_list'] = specialties
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
        attachments = data['specialties'][specialty].get('attachments', [])

        text_block = f"Текущие материалы по «{specialty}»:\n\n"
        if materials:
            text_block += materials + "\n\n"
        if attachments:
            text_block += "📎 Прикреплённые файлы:\n" + "\n".join(
                [f"{i + 1}. {f['file_name']}" for i, f in enumerate(attachments)]
            ) + "\n\n"

        text_block += "✍️ Введите новые материалы или нажмите кнопку ниже для отмены:"

        keyboard_buttons = [["🔙 Назад"]]
        if attachments:
            keyboard_buttons.insert(0, ["🗑 Удалить файл"])

        reply_markup = ReplyKeyboardMarkup(keyboard_buttons, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(text_block, reply_markup=reply_markup)

        return EDIT_MATERIALS_INPUT

    except ValueError:
        await update.message.reply_text("Некорректный номер. Пожалуйста, введите число из списка.")
        return CHOOSE_SPECIALTY_FOR_EDIT


async def save_edited_materials(update: Update, context: ContextTypes.DEFAULT_TYPE):
    specialty = context.user_data.get('edit_specialty')
    if not specialty:
        await update.message.reply_text("Произошла ошибка, попробуйте снова.")
        return MENTOR_MENU

    data = load_data()

    if update.message.document:
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name
        attachments = data['specialties'][specialty].setdefault("attachments", [])
        attachments.append({
            "file_id": file_id,
            "file_name": file_name
        })

        save_data(data)

        keyboard = [
            ["🗑 Удалить файл"],
            ["🔙 Назад"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            f"✅ Файл «{file_name}» добавлен к материалам.\n\n"
            f"Вы можете прикрепить ещё файл или удалить старые.",
            reply_markup=reply_markup
        )
        return EDIT_MATERIALS_INPUT

    new_text = update.message.text.strip()
    if new_text.lower() == "назад":
        return await mentor_menu(update, context)

    data['specialties'][specialty]['materials'] = new_text
    save_data(data)

    keyboard = [
        ["🗑 Удалить файл"],
        ["🔙 Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"✅ Материалы по «{specialty}» обновлены.\n\n"
        f"Вы можете прикрепить файл или удалить старые.",
        reply_markup=reply_markup
    )
    return EDIT_MATERIALS_INPUT


async def prompt_file_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    specialty = context.user_data.get('edit_specialty')
    data = load_data()
    attachments = data['specialties'][specialty].get("attachments", [])

    if not attachments:
        await update.message.reply_text("❌ Нет прикреплённых файлов.")
        return EDIT_MATERIALS_INPUT

    context.user_data['attachments'] = attachments
    file_list = "\n".join([f"{i + 1}. {file['file_name']}" for i, file in enumerate(attachments)])

    reply_markup = ReplyKeyboardMarkup(
        [["❌ Отмена"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        f"📂 Файлы по специальности «{specialty}»:\n\n{file_list}\n\n"
        "Введите номер файла для удаления или нажмите «❌ Отмена»:",
        reply_markup=reply_markup
    )
    return HANDLE_MENTOR_FILE_DELETE


async def handle_mentor_file_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    if text in ["отмена", "❌ отмена"]:
        keyboard = [
            ["🗑 Удалить файл"],
            ["🔙 Назад"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "❌ Удаление отменено.\n\nВы можете прикрепить файл или удалить старые.",
            reply_markup=reply_markup
        )
        return EDIT_MATERIALS_INPUT

    try:
        index = int(text) - 1
        attachments = context.user_data.get('attachments', [])
        if index < 0 or index >= len(attachments):
            raise ValueError

        deleted = attachments.pop(index)
        specialty = context.user_data.get('edit_specialty')
        data = load_data()
        data['specialties'][specialty]['attachments'] = attachments
        save_data(data)

        keyboard = [
            ["🗑 Удалить файл"],
            ["🔙 Назад"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            f"✅ Файл «{deleted['file_name']}» удалён.\n\n"
            f"Вы можете удалить ещё один файл или вернуться назад.",
            reply_markup=reply_markup
        )
        return EDIT_MATERIALS_INPUT


    except ValueError:
        await update.message.reply_text(
            "⚠️ Неверный номер. Введите номер файла или нажмите «❌ Отмена»:"
        )
        return HANDLE_MENTOR_FILE_DELETE


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

        return await show_questions_for_deletion(update, context)

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


async def handle_edit_type_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    if text == "вопрос":
        return await edit_question_text_prompt(update, context)
    elif text == "варианты":
        return await edit_question_options_prompt(update, context)
    elif text == "правильный":
        return await edit_question_correct_prompt(update, context)
    elif text == "🔙 назад":
        return await choose_question_to_edit(update, context)
    elif text == "🖼 изображение":
        return await edit_question_image_prompt(update, context)
    else:
        await update.message.reply_text("Выберите один из вариантов.")
        return CHOOSE_EDIT_TYPE


async def edit_question_image_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    specialty = context.user_data['edit_specialty']
    index = context.user_data['edit_index']
    data = load_data()
    question_data = data['specialties'][specialty]['tests'][index]
    current_image = question_data.get("image")

    if current_image:
        await update.message.reply_photo(
            photo=current_image,
            caption="Текущее изображение прикреплено к вопросу.\n\nОтправьте новое изображение или нажмите «Удалить» / «Оставить как есть».",
            reply_markup=ReplyKeyboardMarkup(
                [["Удалить", "Оставить как есть", "🔙 Назад"]],
                resize_keyboard=True
            )
        )
    else:
        await update.message.reply_text(
            "К этому вопросу не прикреплено изображение.\n\nОтправьте изображение или нажмите «🔙 Назад».",
            reply_markup=ReplyKeyboardMarkup(
                [["🔙 Назад"]],
                resize_keyboard=True
            )
        )

    return EDIT_QUESTION_IMAGE


async def handle_edit_question_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    specialty = context.user_data['edit_specialty']
    index = context.user_data['edit_index']
    data = load_data()
    question_data = data['specialties'][specialty]['tests'][index]

    if update.message.text == "Удалить":
        question_data['image'] = None
        save_data(data)
        await update.message.reply_text("✅ Изображение удалено.")
        return await show_test_edit_menu(update, context)

    elif update.message.text == "Оставить как есть":
        await update.message.reply_text("Изображение не изменено.")
        return await show_test_edit_menu(update, context)

    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        question_data['image'] = file_id
        save_data(data)
        await update.message.reply_text("✅ Изображение обновлено.")
        return await show_test_edit_menu(update, context)

    elif update.message.text == "🔙 Назад":
        return await choose_edit_type(update, context)

    else:
        await update.message.reply_text("Пожалуйста, отправьте изображение или выберите вариант.")
        return EDIT_QUESTION_IMAGE


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
        keyboard = [["Вопрос", "Варианты", "Правильный"],
                    ["🖼 Изображение"], ["🔙 Назад"]]

        await update.message.reply_text("Что хотите изменить?",
                                        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return CHOOSE_EDIT_TYPE
    except:
        await update.message.reply_text("Некорректный номер. Попробуйте снова или нажмите «🔙 Назад».")
        return EDIT_EXISTING_QUESTION


async def show_questions_for_deletion(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


async def delete_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    specialty = context.user_data.get('edit_specialty')
    data = load_data()
    tests = data['specialties'][specialty].get('tests', [])

    if text.lower() == "назад":
        return await show_test_edit_menu(update, context)

    try:
        index = int(text) - 1
        if index < 0 or index >= len(tests):
            raise ValueError
    except ValueError:
        await update.message.reply_text("Некорректный номер. Введите правильный номер вопроса или «Назад» для отмены.")
        return DELETE_QUESTION

    removed_question = tests.pop(index)
    save_data(data)

    await update.message.reply_text(f"✅ Вопрос №{index + 1} удалён.")
    return await show_test_edit_menu(update, context)


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

    context.user_data['new_correct'] = [i + 1 for i in indexes]
    await update.message.reply_text(
        "Хотите прикрепить изображение к вопросу? Отправьте картинку или нажмите «Пропустить».",
        reply_markup=ReplyKeyboardMarkup([["Пропустить"]], resize_keyboard=True)
    )
    return ADD_TEST_IMAGE


async def add_test_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Пропустить":
        image_id = None
    elif update.message.photo:
        image_id = update.message.photo[-1].file_id
    else:
        await update.message.reply_text("Пожалуйста, отправьте изображение или нажмите «Пропустить».")
        return ADD_TEST_IMAGE

    specialty = context.user_data['edit_specialty']
    data = load_data()
    tests = data['specialties'][specialty].get('tests', [])

    new_test = {
        "question": context.user_data['new_question'],
        "options": context.user_data['new_options'],
        "correct": context.user_data['new_correct'],
        "image": image_id
    }

    tests.append(new_test)
    data['specialties'][specialty]['tests'] = tests
    save_data(data)

    await update.message.reply_text("✅ Вопрос с изображением добавлен.")
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
