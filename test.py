import os

import telegram
from dotenv import load_dotenv
from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, CallbackQueryHandler, Updater)


FIRST, SECOND = range(2)


def start_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    keyboard = [
        [InlineKeyboardButton("Первый стейт", callback_data="first_state")],
        [InlineKeyboardButton("Выйти", callback_data="exit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "Приветствую тебя в магазине 'crazy_fish_store'!\nНажми кнопку"


    context.bot.send_message(
        chat_id=chat_id, 
        text=text,
        reply_markup=reply_markup  
    )
    return FIRST


def first_handler_one(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    if query.data == "exit":
        return SECOND
    text = "first_handler_one!\nА теперь перейди ко второму!"
    query.edit_message_text(text=text, reply_markup=reply_markup)

    return FIRST


def first_handler_two(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    keyboard = [[InlineKeyboardButton("Второй стейт", callback_data="second_state")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = "first_handler_two!\nА теперь перейди ко второму!"
    query.edit_message_text(text=text, reply_markup=reply_markup)

    return SECOND


def second_handler(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()
    
    text = "Ты просто БОГ!"
    query.edit_message_text(text=text)

    return ConversationHandler.END



def main():
    load_dotenv()

    tg_token = os.getenv("TG_TOKEN")
    updater = Updater(token=tg_token)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_handler)],

        states = {
            FIRST: [
                CallbackQueryHandler(first_handler_one, "first_state_1"),
                CallbackQueryHandler(first_handler_two, "first_state_2")
            ],
            SECOND: [CallbackQueryHandler(second_handler, "second_state")],
      
        },

        fallbacks=[],

    )
    
    dp.add_handler(conv_handler)
 
    updater.start_polling()
    
if __name__ == "__main__":
    main()