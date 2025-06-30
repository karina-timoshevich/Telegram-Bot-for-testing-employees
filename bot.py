import logging
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
)
from dotenv import load_dotenv
from handlers.mentor import *
from handlers.common import start, choose_role
from handlers.employee import choose_specialty_employee, handle_action_after_specialty, handle_after_materials, \
    receive_employee_fio
from handlers.test import handle_test_answer
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MENTOR_PASSWORD = os.getenv("ADMIN_PASSWORD")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


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
                                               MessageHandler(filters.TEXT & filters.Regex("^🗑 Удалить файл$"),
                                                              prompt_file_deletion),
                                               MessageHandler(filters.Regex("^🔙 Назад$"), mentor_menu),
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, save_edited_materials),
                                               MessageHandler(filters.Document.ALL, save_edited_materials)
                                           ],
                                           HANDLE_MENTOR_FILE_DELETE: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND,
                                                              handle_mentor_file_delete)
                                           ],
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
                                           EDIT_QUESTION_IMAGE: [
                                               MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND,
                                                              handle_edit_question_image)
                                           ],
                                           ADD_TEST_IMAGE: [
                                               MessageHandler(filters.PHOTO, add_test_image),
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, add_test_image)
                                           ],
                                           RENAME_SPECIALTY_SELECT: [
                                               MessageHandler(filters.Regex("^🔙 Назад$"), mentor_menu),
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, rename_specialty),
                                           ],
                                           RENAME_SPECIALTY_INPUT: [
                                               MessageHandler(filters.Regex("^🔙 Назад$"), mentor_menu),
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, apply_specialty_rename),
                                           ],
                                           DELETE_SPECIALTY_SELECT: [
                                               MessageHandler(filters.TEXT & filters.Regex("^🔙 Назад$"), mentor_menu),
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, delete_specialty)
                                           ],
                                           ENTER_EMPLOYEE_NAME: [
                                               MessageHandler(filters.TEXT & ~filters.COMMAND, receive_employee_fio)],

                                       },
                                       fallbacks=[],
                                       )

    app.add_handler(conv_handler)

    print("Бот запущен!")
    app.run_polling()


if __name__ == '__main__':
    main()
