import os
from functools import partial

import telegram
import redis
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, CallbackQueryHandler, Updater)

from moltin_products import get_products_title


MENU, INFO, CART = range(3)


menu_fish = [
    [InlineKeyboardButton("рыбка 1", callback_data="fish_1")],
    [InlineKeyboardButton("рыбка 2", callback_data="fish_2")],
    [InlineKeyboardButton("рыбка 3", callback_data="fish_3")],
    [InlineKeyboardButton("рыбка 4", callback_data="fish_4")]
]
keyboard_fish = InlineKeyboardMarkup(menu_fish)


def start_handler(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    text = "Приветствую тебя в магазине 'crazy_fish_store'!"

    keyboard = [[InlineKeyboardButton("Посмотреть меню", callback_data="menu")]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=chat_id, 
        text=text,
        reply_markup=reply_markup      
    )
    return MENU


def menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    
    text = "Нажми кнопку на интересующем тебя продукте, чтобы посмотреть информацию о нем"

    query.edit_message_text(text=text, reply_markup=keyboard_fish)

    return INFO


def product_info_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    
    text = "Сделайте свой выбор"

    keyboard = [
        [InlineKeyboardButton("Купить", callback_data="purchase")],
        [InlineKeyboardButton("Назад", callback_data="back")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)    
    
    query.edit_message_text(text=text, reply_markup=reply_markup)

    return CART
    

def add_to_cart(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = update.effective_message.chat_id

    if query.data == "back":
        text = "Нажми кнопку на интересующем тебя продукте, чтобы посмотреть информацию о нем"
        query.edit_message_text(text=text, reply_markup=keyboard_fish)
        return INFO

    text = "Здесь будет выбор количества"

    context.bot.send_message(
        chat_id=chat_id, 
        text=text,   
    )

    return INFO


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
            MENU: [CallbackQueryHandler(menu_handler)],

            INFO: [CallbackQueryHandler(product_info_handler)],

            CART: [CallbackQueryHandler(add_to_cart)]
      
        },

        fallbacks=[]

    )
    
    dp.add_handler(conv_handler)
 
    updater.start_polling()
    
if __name__ == "__main__":
    main()