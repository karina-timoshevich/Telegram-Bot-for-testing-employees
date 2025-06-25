import logging
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
)
from dotenv import load_dotenv
from handlers.mentor import *
from handlers.common import start, choose_role
from handlers.employee import choose_specialty_employee, handle_action_after_specialty, handle_after_materials
from handlers.test import handle_test_answer
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MENTOR_PASSWORD = os.getenv("ADMIN_PASSWORD")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

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
    else:
        await update.message.reply_text("Выберите один из вариантов.")
        return CHOOSE_EDIT_TYPE


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(allow_reentry=True,
                                       entry_points=[CommandHandler("start", start)],
                                       states={

                                           CHOOSE_ROLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_role)],
                                           ENTER_PASSWORD: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, enter_password)],
                                           CHOOSE_SPECIALTY_MENTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_specialty_mentor)],
                                           MENTOR_MENU: [MessageHandler(filters.Regex("^🔙 Назад$"), handle_mentor_menu),
                                                         MessageHandler(filters.TEXT & ~filters.COMMAND,
                                                                        handle_mentor_menu)],
                                           ADD_SPECIALTY_NAME: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, add_specialty_name)],
                                           CHOOSE_SPECIALTY_FOR_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                                                                      choose_specialty_for_edit)],
                                           EDIT_MATERIALS_INPUT: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, save_edited_materials)],
                                           CHOOSE_SPECIALTY_FOR_TEST_EDIT: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND,
                                                              choose_specialty_for_test_edit)],
                                           EDIT_TEST_MENU: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, handle_test_menu)],
                                           ADD_TEST_QUESTION: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, add_test_question)],
                                           ADD_TEST_OPTIONS: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, add_test_options)],
                                           ADD_TEST_CORRECT: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, add_test_correct)],
                                           EDIT_EXISTING_QUESTION: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, choose_edit_type)],
                                           CHOOSE_EDIT_TYPE: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, handle_edit_type_choice)
                                           ],
                                           EDIT_QUESTION_TEXT: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, edit_question_text)],
                                           EDIT_QUESTION_OPTIONS: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, edit_question_options)],
                                           EDIT_QUESTION_CORRECT: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, edit_question_correct)],
                                           DELETE_QUESTION: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, delete_question)],
                                           CHOOSE_SPECIALTY_EMPLOYEE: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                                                                      choose_specialty_employee)],

                                           CHOOSE_ACTION_AFTER_SPECIALTY: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND,
                                                              handle_action_after_specialty)],
                                           HANDLE_TEST_ANSWER: [
                                               CallbackQueryHandler(handle_test_answer),
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, handle_after_materials),
                                           ],

                                           ADD_SPECIALTY_TYPE: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, add_specialty_type)
                                           ],
                                           CHOOSE_PARENT_SPECIALTY: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, choose_parent_specialty)
                                           ],
                                           CHOOSE_AFTER_MATERIALS: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, handle_after_materials)],
                                       },
                                       fallbacks=[],
                                       )

    app.add_handler(conv_handler)

    print("Бот запущен!")
    app.run_polling()


if __name__ == '__main__':
    main()
