import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from constants import *
from data_utils import load_data, save_data, add_result


async def ask_test_question(message, context):
    index = context.user_data.get('test_index', 0)
    tests = context.user_data['tests']

    if index >= len(tests):
        return await show_test_result(message, context)

    older_msg_id = context.user_data.pop('older_question_message_id', None)
    if older_msg_id:
        try:
            await context.bot.delete_message(chat_id=message.chat.id, message_id=older_msg_id)
        except:
            pass

    question_data = tests[index]
    options = question_data['options']
    selected = context.user_data.get('selected_options', set())

    keyboard = [[InlineKeyboardButton(f"{'✅ ' if i in selected else ''}{i + 1}) {opt}", callback_data=f"toggle_{i}")]
                for i, opt in enumerate(options)]
    keyboard.append([InlineKeyboardButton("Готово", callback_data="done")])
    markup = InlineKeyboardMarkup(keyboard)

    if question_data.get('image'):
        sent = await context.bot.send_photo(
            chat_id=message.chat.id,
            photo=question_data['image'],
            caption=f"❓ Вопрос {index + 1}:\n{question_data['question']}",
            reply_markup=markup
        )
    else:
        sent = await context.bot.send_message(
            chat_id=message.chat.id,
            text=f"❓ Вопрос {index + 1}:\n{question_data['question']}",
            reply_markup=markup
        )

    context.user_data['older_question_message_id'] = context.user_data.get('last_question_message_id')
    context.user_data['last_question_message_id'] = sent.message_id
    context.user_data['last_question_has_image'] = bool(question_data.get('image'))
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
            feedback = f"❌ Неверно!\nПравильные ответы: {correct_opts}"

        context.user_data['selected_options'] = set()
        context.user_data['test_index'] = index + 1
        message_id = context.user_data.get('last_question_message_id')
        has_image = context.user_data.get('last_question_has_image', False)
        full_text = f"❓ Вопрос {index + 1}:\n{question_data['question']}\n\n{feedback}"

        try:
            if has_image:
                await context.bot.edit_message_caption(
                    chat_id=query.message.chat.id,
                    message_id=message_id,
                    caption=full_text,
                    reply_markup=None
                )
            else:
                await context.bot.edit_message_text(
                    chat_id=query.message.chat.id,
                    message_id=message_id,
                    text=full_text,
                    reply_markup=None
                )
        except:
            pass

        return await ask_test_question(query.message, context)


async def show_test_result(message, context):
    for key in ['last_question_message_id', 'older_question_message_id']:
        msg_id = context.user_data.get(key)
        if msg_id:
            try:
                await context.bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except:
                pass

    total = len(context.user_data['tests'])
    correct = context.user_data['correct_answers']
    incorrect = total - correct

    fio = context.user_data.get("employee_fio", "Неизвестный сотрудник")
    specialty = context.user_data.get("specialty", "Неизвестная специальность")
    username = context.user_data.get("telegram_username", "—")
    user_id = context.user_data.get("telegram_id", "—")

    add_result(fio, specialty, correct, total, username=username, user_id=user_id)

    keyboard = [
        ["📚 Получить материалы"],
        ["📝 Пройти аттестацию"],
        ["🔙 К выбору специальности"],
        ["🏠 В главное меню"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    msg = f"Тест завершён!\nПравильных ответов: {correct} из {total}."
    if incorrect > 2:
        msg += "\n❗️ Неправильных ответов больше двух — нужна пересдача."

    await message.reply_text(msg, reply_markup=reply_markup)
    return CHOOSE_AFTER_MATERIALS
