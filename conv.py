import os
from functools import partial

import telegram
import redis
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, CallbackQueryHandler, Updater)

from moltin_products import get_products_title


MENU, INFO = range(2)
BUT_MENU, BUT_INFO = range(2)


def start_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    text = "Приветствую тебя в магазине 'crazy_fish_store'!"

    keyboard = [[InlineKeyboardButton("Посмотреть меню", callback_data=str(BUT_MENU))]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=chat_id, 
        text=text,
        reply_markup=reply_markup      
    )
    return MENU


def menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    text = "Нажми кнопку на интересующем тебя продукте, чтобы посмотреть информацию о нем"

    keyboard = [[InlineKeyboardButton("определенная рыбка", callback_data=str(BUT_INFO))]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text=text, reply_markup=reply_markup, per_message=True)

    return INFO


def product_info_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()   
    
    text = "Чтобы вернуться в меню, нажмите кнопку"

    keyboard = [[InlineKeyboardButton("Назад", callback_data=str(BUT_MENU))]]

    reply_markup = InlineKeyboardMarkup(keyboard)    
    
    query.edit_message_text(text=text, reply_markup=reply_markup)

    return MENU
    

def quit_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    chat_id = update.callback_query.message.chat_id
    
    text = "Что ж... Твоя жизнь, тебе решать.\nУвидимся!"
    context.bot.send_message(chat_id=chat_id, text=text)

    return ConversationHandler.END


def main():
    load_dotenv()

    tg_token = os.getenv("TG_TOKEN")
    updater = Updater(token=tg_token)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_handler)],

        states = {
            MENU: [CallbackQueryHandler(menu_handler, str(BUT_MENU))],

            INFO: [CallbackQueryHandler(product_info_handler, str(BUT_INFO))]
      
        },

        fallbacks=[]

    )
    
    dp.add_handler(conv_handler)
 
    updater.start_polling()
    
if __name__ == "__main__":
    main()