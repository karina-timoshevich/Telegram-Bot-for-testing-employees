from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from constants import *
from data_utils import load_data, save_data


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(
        [["Ученик", "Наставник", "Админ"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await update.message.reply_text(
        "Здравствуйте! Выберите вашу роль:",
        reply_markup=reply_markup
    )
    return CHOOSE_ROLE


async def choose_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from handlers.employee import choose_specialty_prompt_employee

    role = update.message.text.lower()
    context.user_data['role'] = role

    if role == "админ":
        await update.message.reply_text(
            "Введите пароль для доступа к режиму администратора:",
            reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True, one_time_keyboard=True)
        )
        return ENTER_PASSWORD

    elif role == "наставник":
        await update.message.reply_text(
            "Введите пароль для доступа к режиму наставника:",
            reply_markup=ReplyKeyboardMarkup([["🔙 Назад"]], resize_keyboard=True, one_time_keyboard=True)
        )
        return ENTER_PASSWORD_MENTOR

    elif role == "ученик":
        return await choose_specialty_prompt_employee(update, context)

    else:
        await update.message.reply_text("Пожалуйста, выберите одну из ролей.")
        return CHOOSE_ROLE


async def choose_specialty_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, for_employee=True):
    data = load_data()
    specialties = filter_specialties_with_subtypes(data)
    reply_markup = ReplyKeyboardMarkup(
        [[spec] for spec in specialties],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await update.message.reply_text("Выберите вашу специальность:", reply_markup=reply_markup)
    return CHOOSE_SPECIALTY_EMPLOYEE if for_employee else CHOOSE_SPECIALTY_ADMIN


def filter_specialties_with_subtypes(data):
    specialties = list(data['specialties'].keys())

    base_with_subtypes = set()
    for spec in specialties:
        if "::" in spec:
            base = spec.split("::")[0]
            base_with_subtypes.add(base)

    result = []
    for spec in specialties:
        if "::" in spec:
            result.append(spec)
        else:
            if spec not in base_with_subtypes:
                result.append(spec)
    return result
