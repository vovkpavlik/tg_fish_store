import os
from functools import partial

from dotenv import load_dotenv
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, CallbackQueryHandler, Updater)

from redis_persistence import RedisPersistence
from moltin import (get_moltin_token, get_products, get_product_info, get_img_url,
                    add_to_cart, get_cart_info, get_cart_items, delete_cart_item)


MENU, PRODUCT_INFO, CART, WAITING_EMAIL = range(4)

def send_showcase_keyboard(moltin_token, update: Update, context: CallbackContext):
    chat_id = update.effective_message.chat_id

    text = "Сделай свой выбор."    
    keyboard = []
    
    for product in get_products(moltin_token)["data"]:
        product_button = [InlineKeyboardButton(product["name"], callback_data=product["id"])]

        keyboard.append(product_button)
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.delete_message(
        chat_id,
        message_id=update.effective_message.message_id
    )
    context.bot.send_message(
        chat_id,
        text=text,
        reply_markup=reply_markup      
    )


def send_cart_keyboard(moltin_token, update: Update, context: CallbackContext):
    chat_id = update.effective_message.chat_id
    
    cart_items = get_cart_items(moltin_token, chat_id)
    cart_info = get_cart_info(moltin_token, chat_id)
    cart_total_price = cart_info["meta"]["display_price"]["with_tax"]["amount"] / 100
    
    keyboard = [
        [InlineKeyboardButton("Вернуться в меню", callback_data="back_to_menu")],
    ]
    message_text = f"* Товаров в корзине на сумму $ {cart_total_price}*\n"
    for item in cart_items:
        item_id = item["id"]
        product_name = item["name"]
        product_description = item["description"]
        item_price = item["unit_price"]["amount"] / 100
        item_count = item["quantity"]
        item_total_price = item_count * item_price
        
        product_button = [
            InlineKeyboardButton(f"Убрать из корзины {item['name']}", 
            callback_data=f"{item_id}/{product_name}")
        ]

        keyboard.append(product_button)

        text = f"""
        *{product_name}*
        {product_description}
        $ {item_price} за шт.
        Всего {item_count} шт. на сумму *$ {item_total_price}*.\n
        """       
        message_text += text       

    if not cart_items:
        message_text = "Ваша корзина пуста"
    else:
        keyboard.append(
            [InlineKeyboardButton("Перейти к оплате", callback_data="purchase")]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.bot.delete_message(
        chat_id,
        message_id=update.effective_message.message_id
    )
    context.bot.send_message(
        chat_id,
        text=message_text,
        parse_mode=telegram.ParseMode.MARKDOWN,
        reply_markup=reply_markup      
    )


def start_handler(moltin_token, update: Update, context: CallbackContext):
    chat_id = update.effective_message.chat_id
    
    context.bot.send_message(
        chat_id=chat_id,
        text="Приветствую тебя в магазине 'Crazy Fish Store!'"     
    )

    send_showcase_keyboard(moltin_token, update, context)
    
    return MENU


def menu_handler(moltin_token, update: Update, context: CallbackContext):
    chat_id = update.effective_message.chat_id
    query = update.callback_query

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

    context.bot.delete_message(
        chat_id,
        message_id=update.effective_message.message_id
    )
    context.bot.send_photo(chat_id, 
        img_url, 
        reply_markup=reply_markup, 
        caption=text
    )

    return PRODUCT_INFO
    

def product_info_handler(moltin_token, update: Update, context: CallbackContext):
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


def cart_info_handler(moltin_token, update: Update, context: CallbackContext):
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
    query.answer(f"Товар {product_name} удален.")

    send_cart_keyboard(moltin_token, update, context)

    return CART

    
def get_email_handler(update: Update, context: CallbackContext):
    chat_id = update.effective_message.chat_id
    users_message = update.effective_message.text  

    context.bot.send_message(
        chat_id=chat_id,
        text=f"Ты прислал эту почту: {users_message}"     
    )


def quit_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    chat_id = update.callback_query.message.chat_id
    
    text = "Что ж... Твоя жизнь, тебе решать.\nУвидимся!"
    context.bot.send_message(chat_id=chat_id, text=text)

    return ConversationHandler.END


def main():
    load_dotenv()
    
    # persistence = RedisPersistence(
    #     host=os.getenv('REDIS_HOST'),
    #     port=int(os.getenv('REDIS_PORT')),
    #     password=os.getenv('REDIS_PASSWORD')  # опциональный аргумент
    # )
     
    moltin_id = os.getenv("MOLTIN_ID")
    moltin_secret = os.getenv("MOLTIN_SECRET")
    moltin_token = get_moltin_token(moltin_secret, moltin_id)

    tg_token = os.getenv("TG_TOKEN")
    # updater = Updater(token=tg_token, persistence=persistence)
    updater = Updater(token=tg_token)
    dp = updater.dispatcher

    partial_start_handler = partial(start_handler, moltin_token)
    partial_menu_handler = partial(menu_handler,  moltin_token)
    partial_product_info_handler = partial(product_info_handler, moltin_token)
    partial_cart_info_handler= partial(cart_info_handler, moltin_token)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', partial_start_handler)],

        states = {
            MENU: [CallbackQueryHandler(partial_menu_handler)],

            PRODUCT_INFO: [CallbackQueryHandler(partial_product_info_handler)],

            CART: [CallbackQueryHandler(partial_cart_info_handler)],

            WAITING_EMAIL: [MessageHandler(Filters.text, get_email_handler)]
      
        },

        fallbacks=[],

        # name='my_conversation',
        # persistent=True
    )
    
    dp.add_handler(conv_handler)
 
    updater.start_polling()
    
if __name__ == "__main__":
    main()
    