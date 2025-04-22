import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# New bot token
bot = telebot.TeleBot("7581429150:AAEu8Kmlw6VALm1aROxn6Q4cFCIFryeLMS8")
ADMIN_ID = 6713288104
user_data = {}

# Start command
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("L$D 🃏 (4500 DZD)", callback_data="product_lsd"),
        InlineKeyboardButton("Shrooms 🍄 (4000 DZD)", callback_data="product_shroom")
    )
    bot.send_message(chat_id, "Welcome 🍄 to a world where ego dissolves and soul is fed 💎\n\nChoose your product:", reply_markup=markup)

# Product selection
@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def handle_product(call):
    chat_id = call.message.chat.id
    product = "L$D 🃏" if "lsd" in call.data else "Shrooms 🍄"
    price = 4500 if "lsd" in call.data else 4000
    user_data[chat_id].update({'product': product, 'price': price})
    bot.delete_message(chat_id, call.message.message_id)
    bot.send_message(chat_id, f"How many pieces of {product} do you want? (5+1 free deal applies!)")
    bot.register_next_step_handler_by_chat_id(chat_id, handle_quantity)

# Quantity input
def handle_quantity(message):
    chat_id = message.chat.id
    try:
        quantity = int(message.text)
        bonus = quantity // 5
        total_items = quantity + bonus
        total_price = quantity * user_data[chat_id]['price']
        user_data[chat_id].update({
            'quantity': quantity,
            'bonus': bonus,
            'total_items': total_items,
            'total_price': total_price
        })
        bot.send_message(chat_id, f"You're getting {total_items} for {total_price} DZD 💎\n\nEnter your full name:")
        bot.register_next_step_handler(message, get_name)
    except:
        bot.send_message(chat_id, "Please enter a valid number:")
        bot.register_next_step_handler(message, handle_quantity)

# Info gathering
def get_name(message):
    chat_id = message.chat.id
    user_data[chat_id]['full_name'] = message.text
    bot.send_message(chat_id, "Your wilaya:")
    bot.register_next_step_handler(message, get_wilaya)

def get_wilaya(message):
    chat_id = message.chat.id
    user_data[chat_id]['wilaya'] = message.text
    bot.send_message(chat_id, "Your commune:")
    bot.register_next_step_handler(message, get_commune)

def get_commune(message):
    chat_id = message.chat.id
    user_data[chat_id]['commune'] = message.text
    bot.send_message(chat_id, "Your phone number:")
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    chat_id = message.chat.id
    user_data[chat_id]['phone'] = message.text
    show_summary(chat_id)

# Order summary
def show_summary(chat_id):
    data = user_data[chat_id]
    summary = (
        f"🛍️ Order Summary:\n\n"
        f"Product: {data['product']}\n"
        f"Quantity: {data['quantity']} (+{data['bonus']} free)\n"
        f"Total: {data['total_price']} DZD\n\n"
        f"Name: {data['full_name']}\n"
        f"Wilaya: {data['wilaya']}\n"
        f"Commune: {data['commune']}\n"
        f"Phone: {data['phone']}"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Confirm", callback_data="confirm_order"))
    markup.add(InlineKeyboardButton("🔁 Restart", callback_data="restart_order"))
    bot.send_message(chat_id, summary, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["confirm_order", "restart_order"])
def confirm_or_restart(call):
    chat_id = call.message.chat.id
    bot.delete_message(chat_id, call.message.message_id)
    if call.data == "restart_order":
        bot.send_message(chat_id, "Restarting order...")
        start(call.message)
    else:
        bot.send_message(chat_id, "Please pay via Baridimob (cardless payment).\nSend the withdrawal number and PIN like this:\n\n`12345678 1234`", parse_mode="Markdown")
        bot.register_next_step_handler_by_chat_id(chat_id, handle_payment)

# Payment info
def handle_payment(message):
    chat_id = message.chat.id
    user_data[chat_id]['payment'] = message.text.strip()
    bot.send_message(chat_id, "Thank you soul, we will make sure to kill your ego 🍄")

    data = user_data[chat_id]
    order_details = (
        f"💎 *New Order*\n\n"
        f"Product: {data['product']}\n"
        f"Quantity: {data['quantity']} (+{data['bonus']} free)\n"
        f"Total: {data['total_price']} DZD\n\n"
        f"Name: {data['full_name']}\n"
        f"Wilaya: {data['wilaya']}\n"
        f"Commune: {data['commune']}\n"
        f"Phone: {data['phone']}\n"
        f"Baridimob: `{data['payment']}`\n"
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    bot.send_message(ADMIN_ID, order_details, parse_mode="Markdown")

# Keep bot running
try:
    bot.infinity_polling()
except Exception as e:
    print("Bot crashed:", e)
