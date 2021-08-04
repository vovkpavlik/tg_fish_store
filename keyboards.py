import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from moltin import get_cart_info, get_cart_items, get_products


def send_showcase_keyboard(redis, update: Update, context: CallbackContext):
    moltin_token = redis.get("moltin_token")

    chat_id = update.effective_message.chat_id

    text = "Сделай свой выбор."    
    keyboard = [
        [InlineKeyboardButton("Перейти в корзину", callback_data="go_to_cart")],
    ]
    
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


def send_cart_keyboard(redis, update: Update, context: CallbackContext):
    moltin_token = redis.get("moltin_token")

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
