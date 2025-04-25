import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import time
import threading
import os

# === CONFIG ===
API_TOKEN = '7581429150:AAEu8Kmlw6VALm1aROxn6Q4cFCIFryeLMS8'
ADMIN_ID = 6713288104
CHANNEL_ID = -1002350700307
PIN_FILE = 'pin_id.txt'

bot = telebot.TeleBot(API_TOKEN)
users = {}
current_pin = None

# === PIN HANDLER ===
def generate_pin():
    return ''.join(random.choices('0123456789', k=6))

def read_last_pin_id():
    if os.path.exists(PIN_FILE):
        with open(PIN_FILE, 'r') as f:
            return int(f.read().strip())
    return None

def write_last_pin_id(pin_id):
    with open(PIN_FILE, 'w') as f:
        f.write(str(pin_id))

def post_new_pin():
    global current_pin
    current_pin = generate_pin()

    # Send new PIN to channel
    msg = bot.send_message(
        CHANNEL_ID,
        f"🔑 <b>New Access Key:</b> <code>{current_pin}</code>",
        parse_mode="HTML"
    )

    # Unpin old PIN
    last_pin_id = read_last_pin_id()
    if last_pin_id:
        try:
            bot.unpin_chat_message(CHANNEL_ID, last_pin_id)
        except Exception as e:
            print(f"[!] Failed to unpin previous message: {e}")

    # Pin new and store its ID
    bot.pin_chat_message(CHANNEL_ID, msg.message_id)
    write_last_pin_id(msg.message_id)

def schedule_pin_refresh():
    def loop():
        while True:
            post_new_pin()
            time.sleep(3 * 24 * 60 * 60)  # Every 3 days
    threading.Thread(target=loop, daemon=True).start()

schedule_pin_refresh()

# === UI ELEMENTS ===
def get_start_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("To the hole", callback_data="start_order"))
    return markup

def get_product_buttons():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🍄 Mushrooms — 4500 DZD", callback_data="product_shrooms"),
        InlineKeyboardButton("🃏 LSD — 4500 DZD", callback_data="product_lsd")
    )
    return markup

def get_confirm_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("To the hole", callback_data="confirm_order"))
    return markup

# === BOT FLOW ===
@bot.message_handler(commands=['start'])
def handle_start(message):
    users[message.chat.id] = {}
    welcome = (
        "✋ <b>Welcome</b>, this is a world where ego is killed and soul is fed.\n"
        "Thank you for trusting your He.art."
    )
    bot.send_message(message.chat.id, welcome, reply_markup=get_start_button(), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "start_order")
def ask_for_pin(call):
    users[call.message.chat.id]['step'] = 'awaiting_pin'
    bot.send_message(
        call.message.chat.id,
        "Please write down the access key or ask @joejowjoe 🔒"
    )

@bot.message_handler(func=lambda m: users.get(m.chat.id, {}).get('step') == 'awaiting_pin')
def check_pin(message):
    if message.text.strip() == current_pin:
        users[message.chat.id]['step'] = 'product'
        bot.send_message(message.chat.id, "Choose your product:", reply_markup=get_product_buttons())
    else:
        bot.send_message(message.chat.id, "❌ Wrong key. Try again or ask @joejowjoe.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def choose_product(call):
    choice = call.data.split("_")[1]
    product_name = "Mushrooms 🍄" if choice == "shrooms" else "LSD 🃏"
    users[call.message.chat.id].update({
        'product': product_name,
        'price': 4500,
        'step': 'quantity'
    })
    bot.send_message(call.message.chat.id, "How many units would you like?")

@bot.message_handler(func=lambda m: users.get(m.chat.id, {}).get('step') == 'quantity')
def get_quantity(message):
    if message.text.isdigit():
        qty = int(message.text)
        total = qty * users[message.chat.id]['price']
        users[message.chat.id].update({'quantity': qty, 'total': total, 'step': 'name'})
        bot.send_message(message.chat.id, f"📪 Full Name:")
    else:
        bot.send_message(message.chat.id, "Please enter a valid number.")

@bot.message_handler(func=lambda m: users.get(m.chat.id, {}).get('step') == 'name')
def get_name(message):
    users[message.chat.id]['name'] = message.text
    users[message.chat.id]['step'] = 'wilaya'
    bot.send_message(message.chat.id, "Wilaya:")

@bot.message_handler(func=lambda m: users.get(m.chat.id, {}).get('step') == 'wilaya')
def get_wilaya(message):
    users[message.chat.id]['wilaya'] = message.text
    users[message.chat.id]['step'] = 'commune'
    bot.send_message(message.chat.id, "Commune:")

@bot.message_handler(func=lambda m: users.get(m.chat.id, {}).get('step') == 'commune')
def get_commune(message):
    users[message.chat.id]['commune'] = message.text
    users[message.chat.id]['step'] = 'phone'
    bot.send_message(message.chat.id, "☎️ Phone Number:")

@bot.message_handler(func=lambda m: users.get(m.chat.id, {}).get('step') == 'phone')
def get_phone(message):
    users[message.chat.id]['phone'] = message.text
    users[message.chat.id]['step'] = 'payment'
    bot.send_message(message.chat.id, "💳 Enter Baridimob Withdrawal Ref + PIN:")

@bot.message_handler(func=lambda m: users.get(m.chat.id, {}).get('step') == 'payment')
def get_payment(message):
    users[message.chat.id]['payment'] = message.text
    users[message.chat.id]['step'] = 'confirm'
    u = users[message.chat.id]
    summary = (
        f"🧾 <b>Order Summary</b>\n"
        f"Product: {u['product']}\n"
        f"Qty: {u['quantity']}\n"
        f"Total: {u['total']} DZD\n\n"
        f"📪 Name: {u['name']}\n"
        f"Wilaya: {u['wilaya']}\n"
        f"Commune: {u['commune']}\n"
        f"☎️ Phone: {u['phone']}\n"
        f"💳 Payment Info: {u['payment']}"
    )
    bot.send_message(message.chat.id, summary, parse_mode="HTML", reply_markup=get_confirm_button())

@bot.callback_query_handler(func=lambda call: call.data == "confirm_order")
def finalize_order(call):
    u = users[call.message.chat.id]
    summary = (
        f"💎 <b>New Order</b>\n"
        f"User ID: {call.message.chat.id}\n"
        f"Product: {u['product']}\n"
        f"Qty: {u['quantity']}\n"
        f"Total: {u['total']} DZD\n\n"
        f"📪 Name: {u['name']}\n"
        f"Wilaya: {u['wilaya']}\n"
        f"Commune: {u['commune']}\n"
        f"☎️ Phone: {u['phone']}\n"
        f"💳 Payment: {u['payment']}"
    )
    bot.send_message(ADMIN_ID, summary, parse_mode="HTML")
    bot.send_message(call.message.chat.id, "Thank you, we will make sure to kill your ego 👽")
    users.pop(call.message.chat.id, None)

# === RUN BOT ===
print("Bot is running...")
bot.infinity_polling()