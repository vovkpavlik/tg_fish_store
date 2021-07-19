import os
from functools import partial

import telegram
import redis
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, CallbackQueryHandler, Updater)

from moltin_products import get_products_title


_database = None

MENU, INFO, BACK = range(3)


def start_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    text = "Приветствую тебя в магазине 'crazy_fish_store'!"

    keyboard = [[InlineKeyboardButton("Посмотреть меню", callback_data=str(MENU))]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=chat_id, 
        text=text,
        reply_markup=reply_markup      
    )
    return "LIST"


def price_list_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    text = "Нажми кнопку на интересующем тебя продукте, чтобы посмотреть информацию о нем"

    keyboard = [[InlineKeyboardButton("определенная рыбка", callback_data=str(INFO))]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text=text, reply_markup=reply_markup)

    return "INFO"


def product_info_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()   
    
    text = "Чтобы вернуться в меню, нажмите кнопку"

    keyboard = [[InlineKeyboardButton("Назад", callback_data=str(BACK))]]

    reply_markup = InlineKeyboardMarkup(keyboard)    
    
    query.edit_message_text(text=text, reply_markup=reply_markup)

    return "LIST"


def handle_users_reply(update: Update, context: CallbackContext):
    db = get_database_connection()

    user_reply = update.effective_message
    chat_id = update.effective_message.chat_id


    if user_reply == "/start":
        user_state = "START"
    else:
        user_state = db.get(chat_id)

    states_functions = {
        "START": start_handler,
        "LIST": price_list_handler,
        "INFO": product_info_handler,
    }

    state_handler = states_functions[user_state]

    try:
        next_state = state_handler
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)
    

def quit_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    chat_id = update.callback_query.message.chat_id
    
    text = "Что ж... Твоя жизнь, тебе решать.\nУвидимся!"
    context.bot.send_message(chat_id=chat_id, text=text)

    return ConversationHandler.END


def get_database_connection():
    global _database

    if _database is None:
        db_password = os.getenv("REDIS_PASSWORD")
        db_host = os.getenv("REDIS_HOST")
        db_port = os.getenv("REDIS_PORT")

        _database = redis.Redis(
            host = db_host,
            port = db_port,
            password = db_password,
            decode_responses=True,
            db=0
        )

    return _database


def main():
    load_dotenv()

    tg_token = os.getenv("TG_TOKEN")
    updater = Updater(token=tg_token)
    dp = updater.dispatcher

    # dp.add_handler(CallbackQueryHandler(handle_users_reply))
    dp.add_handler(CommandHandler('start', handle_users_reply))
    
    updater.start_polling()
    
if __name__ == "__main__":
    main()