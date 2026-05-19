import telebot
from telebot import types
import json
import os
from datetime import datetime

# BOT TOKEN - 2 မျိုးထဲက 1 မျိုးရွေး

# နည်းလမ်း 1: Render Environment Variable သုံးမယ်ဆို ဒါကိုသုံး
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# နည်းလမ်း 2: တိုက်ရိုက်ထည့်မယ်ဆို ဒါကိုသုံး, အပေါ်ကဟာကိုဖျက်
# BOT_TOKEN = "8374928743:AAHdjhfkjashdfkjasdhfkjasdhfk"  # ← မင်းရဲ့ Token အစစ်ထည့်

bot = telebot.TeleBot(BOT_TOKEN)


# Channel Links
CHANNEL_URL = "https://t.me/phyowailindigitalhub"
SUPPORT_USERNAME = "@Kophyowailin5534"

# Database File
DB_FILE = "users.json"

# Load Database
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save Database
def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

users = load_db()

# Quick Links Keyboard
def quick_links_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("💰 Daily Bonus", callback_data="daily")
    btn2 = types.InlineKeyboardButton("👥 Referral", callback_data="referral")
    btn3 = types.InlineKeyboardButton("📈 Check Balance", callback_data="balance")
    btn4 = types.InlineKeyboardButton("💵 Withdraw", callback_data="withdraw")
    btn5 = types.InlineKeyboardButton("📢 Channel", url=CHANNEL_URL)
    btn6 = types.InlineKeyboardButton("💬 Support", url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup

# /start Command
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    username = message.from_user.first_name
    
    if user_id not in users:
        users[user_id] = {
            "username": message.from_user.username,
            "first_name": username,
            "balance": 0.00,
            "referrals": 0,
            "total_earned": 0.00,
            "last_daily": "",
            "join_date": datetime.now().strftime("%Y-%m-%d")
        }
        save_db(users)
    
    user_data = users[user_id]
    balance = user_data["balance"]
    referrals = user_data["referrals"]
    total_earned = user_data["total_earned"]
    
    welcome_caption = f"""
👋 Welcome, {username}!

🎉 **Auto Cash Bot** မှ ကြိုဆိုပါတယ်
ကျွန်တော်က Phyo Wai Lin ပါ။

📊 **Your Stats:**
💰 Balance: ${balance:.2f}
👥 Referrals: {referrals}
💵 Total Earned: ${total_earned:.2f}

⚡ **နေ့တိုင်း $0.50 အခမဲ့**
👥 **Refer 1 ယောက် = $0.20**
📈 **Grass Airdrop Passive Income**
💵 **Min Withdraw $10**

👉 /daily နှိပ်ပြီးစတင်ငွေရှာပါ

📢 Channel: {CHANNEL_URL}
💬 Support: {SUPPORT_USERNAME}
"""

    try:
        bot.send_video(
            chat_id=message.chat.id,
            video=WELCOME_VIDEO,
            caption=welcome_caption,
            reply_markup=quick_links_markup(),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Video Error: {e}")
        bot.send_message(
            message.chat.id, 
            welcome_caption, 
            reply_markup=quick_links_markup(),
            parse_mode="Markdown"
        )

# /daily Command
@bot.message_handler(commands=['daily'])
def daily_bonus(message):
    user_id = str(message.from_user.id)
    today = datetime.now().strftime("%Y-%m-%d")
    
    if user_id not in users:
        bot.reply_to(message, "❌ /start နှိပ်ပြီး အရင်စတင်ပါ")
        return
    
    if users[user_id]["last_daily"] == today:
        bot.reply_to(message, "⏰ ဒီနေ့အတွက် Bonus ယူပြီးပါပြီ။ မနက်ဖြန်မှ ပြန်လာပါ!")
        return
    
    users[user_id]["balance"] += 0.50
    users[user_id]["total_earned"] += 0.50
    users[user_id]["last_daily"] = today
    save_db(users)
    
    bot.reply_to(message, f"✅ Daily Bonus $0.50 ရပါပြီ!\n💰 လက်ကျန်ငွေ: ${users[user_id]['balance']:.2f}")

# Callback Handler
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = str(call.from_user.id)
    
    if call.data == "daily":
        daily_bonus(call.message)
    elif call.data == "balance":
        if user_id in users:
            bal = users[user_id]["balance"]
            bot.answer_callback_query(call.id, f"💰 Balance: ${bal:.2f}")
        else:
            bot.answer_callback_query(call.id, "❌ /start နှိပ်ပါ")
    elif call.data == "referral":
        ref_link = f"https://t.me/autocashmy_bot?start={user_id}"
        bot.send_message(call.message.chat.id, f"👥 **မင်းရဲ့ Referral Link:**\n`{ref_link}`\n\n1 ယောက်ခေါ်ရင် $0.20 ရမယ်", parse_mode="Markdown")
    elif call.data == "withdraw":
        bot.send_message(call.message.chat.id, f"💵 **Withdraw**\n\nMin: $10\nလက်ရှိလက်ကျန်: ${users[user_id]['balance']:.2f}\n\nWithdraw လုပ်ရန် {SUPPORT_USERNAME} ကို ဆက်သွယ်ပါ")

print("Bot is running...")
bot.infinity_polling()