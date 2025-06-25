from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from constants import *
from data_utils import load_data, save_data


async def ask_test_question(message, context):
    index = context.user_data.get('test_index', 0)
    tests = context.user_data['tests']

    if index >= len(tests):
        return await show_test_result(message, context)

    question_data = tests[index]
    options = question_data['options']
    selected = context.user_data.get('selected_options', set())

    keyboard = []
    for i, option in enumerate(options):
        prefix = "✅ " if i in selected else ""
        keyboard.append([InlineKeyboardButton(f"{prefix}{i + 1}) {option}", callback_data=f"toggle_{i}")])
    keyboard.append([InlineKeyboardButton("Готово", callback_data="done")])

    await message.reply_text(
        f"❓ Вопрос {index + 1}:\n{question_data['question']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return HANDLE_TEST_ANSWER


async def handle_test_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    selected = context.user_data.get('selected_options', set())

    if data.startswith("toggle_"):
        option_index = int(data.split("_")[1])
        if option_index in selected:
            selected.remove(option_index)
        else:
            selected.add(option_index)
        context.user_data['selected_options'] = selected
        index = context.user_data['test_index']
        question_data = context.user_data['tests'][index]
        options = question_data['options']

        keyboard = []
        for i, option in enumerate(options):
            prefix = "✅ " if i in selected else ""
            keyboard.append([InlineKeyboardButton(f"{prefix}{i + 1}) {option}", callback_data=f"toggle_{i}")])
        keyboard.append([InlineKeyboardButton("Готово", callback_data="done")])

        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))

        return HANDLE_TEST_ANSWER

    elif data == "done":
        index = context.user_data['test_index']
        tests = context.user_data['tests']
        question_data = tests[index]

        correct_indices = set(i - 1 for i in question_data['correct'])
        selected = context.user_data.get('selected_options', set())

        if selected == correct_indices:
            context.user_data['correct_answers'] = context.user_data.get('correct_answers', 0) + 1
            feedback = "✅ Верно!"
        else:
            correct_opts = ", ".join([f"{i + 1}) {question_data['options'][i]}" for i in correct_indices])
            feedback = f"❌ Неверно! Правильные ответы: {correct_opts}"

        context.user_data['selected_options'] = set()
        context.user_data['test_index'] = index + 1

        await query.edit_message_text(feedback)
        await ask_test_question(query.message, context)
        return HANDLE_TEST_ANSWER


async def show_test_result(message, context):
    total = len(context.user_data['tests'])
    correct = context.user_data['correct_answers']
    incorrect = total - correct

    keyboard = [
        ["📚 Получить материалы"],
        ["📝 Пройти аттестацию"],
        ["🔙 К выбору специальности"],
        ["🏠 В главное меню"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    msg = f"Тест завершён!\nПравильных ответов: {correct} из {total}."
    if incorrect > 2:
        msg += "\n❗️ Количество неправильных ответов больше 2 — пересдача."

    await message.reply_text(
        msg,
        reply_markup=reply_markup  # Use the keyboard we created
    )

    return CHOOSE_AFTER_MATERIALS
