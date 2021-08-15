import os
from functools import partial

from dotenv import load_dotenv
from email_validator import EmailNotValidError, validate_email
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

from keyboards import send_cart_keyboard, send_showcase_keyboard
from moltin import (add_to_cart, create_customer, delete_cart_item,
                    get_actual_token, get_img_url, get_product_info)
from redis_persistence import RedisPersistence


MENU, PRODUCT_INFO, CART, WAITING_EMAIL = range(4)


def start_handler(redis_conn, moltin_secret, moltin_id, update: Update, context: CallbackContext):
    moltin_token = get_actual_token(redis_conn, moltin_secret, moltin_id)

    chat_id = update.effective_message.chat_id
    
    context.bot.send_message(
        chat_id=chat_id,
        text="Приветствую тебя в магазине 'Crazy Fish Store!'"     
    )

    send_showcase_keyboard(moltin_token, update, context)
    
    return MENU


def menu_handler(redis_conn, moltin_secret, moltin_id, update: Update, context: CallbackContext):
    moltin_token = get_actual_token(redis_conn, moltin_secret, moltin_id)

    chat_id = update.effective_message.chat_id
    query = update.callback_query

    if query.data == "go_to_cart":
        send_cart_keyboard(moltin_token, update, context)
        return CART 

    product_data = get_product_info(moltin_token, query.data)

    img_url = get_img_url(
        moltin_token, 
        product_data["relationships"]["main_image"]["data"]["id"]
    )
    
    product_name = product_data["name"]
    product_description = product_data["description"]
    product_price = product_data["price"][0]["amount"] / 100

    text = f"""
        Все, что вам нужно знать об экземпляре {product_name}: \n\n
        Во-первых: {product_description}\n
        Во-вторых: цена вопроса - $ {product_price} за одну особь.
    """

    keyboard = [
        [
            InlineKeyboardButton("Взять 1 шт.", callback_data=f"1/{query.data}"), 
            InlineKeyboardButton("Взять 10 шт.", callback_data=f"10/{query.data}"),
            InlineKeyboardButton("Взять 20 шт.", callback_data=f"20/{query.data}")
        ],
        [InlineKeyboardButton("Вернуться в меню", callback_data="back_to_menu")],
        [InlineKeyboardButton("Перейти в корзину", callback_data="go_to_cart")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_photo(chat_id, 
        img_url, 
        reply_markup=reply_markup, 
        caption=text
    )
    context.bot.delete_message(
        chat_id,
        message_id=update.effective_message.message_id
    )

    return PRODUCT_INFO
    

def product_info_handler(redis_conn, moltin_secret, moltin_id, update: Update, context: CallbackContext):
    moltin_token = get_actual_token(redis_conn, moltin_secret, moltin_id)
    
    query = update.callback_query
    chat_id = update.effective_message.chat_id

    if query.data == "back_to_menu":
        send_showcase_keyboard(moltin_token, update, context)
        return MENU
    if query.data == "go_to_cart":
        send_cart_keyboard(moltin_token, update, context)
        return CART

    quantity, product_id = query.data.split("/")    
    product_data = get_product_info(moltin_token, product_id)
    product_name = product_data["name"]
    sku = product_data["sku"]
    
    add_to_cart(moltin_token, chat_id, sku, int(quantity))
    query.answer(f"Добавлено {quantity} шт. товара {product_name}.")

    return PRODUCT_INFO


def cart_info_handler(redis_conn, moltin_secret, moltin_id, update: Update, context: CallbackContext):
    moltin_token = get_actual_token(redis_conn, moltin_secret, moltin_id) 
    
    query = update.callback_query
    chat_id = update.effective_message.chat_id
    
    if query.data == "back_to_menu":
        send_showcase_keyboard(moltin_token, update, context)
        return MENU    
    if query.data =="purchase":       
        context.bot.send_message(
            chat_id=chat_id,
            text="Напишите адрес своей электронной почты, чтобы мы могли прислать вам подробности"     
        )
        return WAITING_EMAIL    

    item_id, product_name = query.data.split("/")

    delete_cart_item(moltin_token, chat_id, item_id)

    send_cart_keyboard(moltin_token, update, context)
    query.answer(f"Товар {product_name} удален.")
    
    return CART

    
def get_email_handler(redis_conn, moltin_secret, moltin_id, update: Update, context: CallbackContext):
    moltin_token = get_actual_token(redis_conn, moltin_secret, moltin_id)        
    
    chat_id = update.effective_message.chat_id
    users_message = update.effective_message.text
    
    try:
        valid = validate_email(users_message)
        email = valid.email
        create_customer(moltin_token, chat_id, email)
        text = f"Получена почта: {users_message}\nБлагодарю за покупки :)"
 
    except EmailNotValidError:         
        text="Введите реальный адрес"
        context.bot.send_message(
            chat_id=chat_id,
            text=text  
        )
        return WAITING_EMAIL
    
    context.bot.send_message(
        chat_id=chat_id,
        text=text  
    ) 

    return ConversationHandler.END


def main():
    load_dotenv()
  
    persistence = RedisPersistence(
        host=os.getenv('REDIS_HOST'),
        port=int(os.getenv('REDIS_PORT')),
        password=os.getenv('REDIS_PASSWORD')
    )
    redis_conn = persistence.get_redis_connection()

    moltin_id = os.getenv("MOLTIN_ID")
    moltin_secret = os.getenv("MOLTIN_SECRET")   
    
    tg_token = os.getenv("TG_TOKEN")

    updater = Updater(token=tg_token, persistence=persistence)
    dp = updater.dispatcher

    partial_start_handler = partial(start_handler, redis_conn, moltin_secret, moltin_id,)
    partial_menu_handler = partial(menu_handler,  redis_conn, moltin_secret, moltin_id)
    partial_product_info_handler = partial(product_info_handler, redis_conn, moltin_secret, moltin_id)
    partial_cart_info_handler= partial(cart_info_handler, redis_conn, moltin_secret, moltin_id)
    partial_get_email_handler= partial(get_email_handler, redis_conn, moltin_secret, moltin_id)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', partial_start_handler)],

        states = {
            MENU: [CallbackQueryHandler(partial_menu_handler)],

            PRODUCT_INFO: [CallbackQueryHandler(partial_product_info_handler)],

            CART: [CallbackQueryHandler(partial_cart_info_handler)],

            WAITING_EMAIL: [MessageHandler(Filters.text, partial_get_email_handler)]
      
        },

        fallbacks=[],
    
        name = "bloblo",
        persistent = True
    )

    dp.add_handler(conv_handler)

    updater.start_polling()

if __name__ == "__main__":
    main()
