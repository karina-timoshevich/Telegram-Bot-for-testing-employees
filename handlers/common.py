from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from constants import *
from data_utils import load_data, save_data


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(
        [["Сотрудник", "Наставник"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "Здравствуйте! Выберите вашу роль:",
        reply_markup=reply_markup
    )
    return CHOOSE_ROLE


async def choose_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    role = update.message.text.lower()
    context.user_data['role'] = role

    if role == "наставник":
        await update.message.reply_text(
            "Введите пароль для доступа к режиму наставника:",
            reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True, one_time_keyboard=True)
        )
        return ENTER_PASSWORD

    elif role == "сотрудник":
        return await choose_specialty_prompt(update, context, for_employee=True)

    else:
        await update.message.reply_text("Пожалуйста, выберите одну из ролей.")
        return CHOOSE_ROLE


async def choose_specialty_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, for_employee=True):
    data = load_data()
    specialties = list(data['specialties'].keys())
    reply_markup = ReplyKeyboardMarkup(
        [[spec] for spec in specialties],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await update.message.reply_text("Выберите вашу специальность:", reply_markup=reply_markup)
    return CHOOSE_SPECIALTY_EMPLOYEE if for_employee else CHOOSE_SPECIALTY_MENTOR
