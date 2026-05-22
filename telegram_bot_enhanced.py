import telebot
from telebot import types
import os
import datetime
import json
import threading
from flask import Flask

# --- CONFIGURATION ---
# Bot Token ကို ဒီနေရာမှာ အမှန်ပြန်ထည့်ပေးပါ
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# သင့်ရဲ့ Telegram ID
ADMIN_ID = 7835760300 
# လူတစ်ယောက်ဖိတ်ရင် ရမယ့် Referral Bonus (USDC)
REFERRAL_BONUS = 0.20  

# --- DATABASE ---
USER_DATA_FILE = 'user_data.json'

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

user_data = load_user_data()

def get_user(user_id, first_name, referrer_id=None):
    user_id_str = str(user_id)
    if user_id_str not in user_data:
        user_data[user_id_str] = {
            'first_name': first_name,
            'balance': 0.00,
            'last_bonus_claim': None,
            'referrals': 0
        }
        # Referral bonus ပေးခြင်း
        if referrer_id and str(referrer_id) in user_data and str(referrer_id) != user_id_str:
            user_data[str(referrer_id)]['balance'] += REFERRAL_BONUS
            user_data[str(referrer_id)]['referrals'] += 1
        
        save_user_data(user_data)
    return user_data[user_id_str]

def update_user_balance(user_id, amount):
    user_data[str(user_id)]['balance'] += amount
    save_user_data(user_data)

def update_last_bonus_claim(user_id):
    user_data[str(user_id)]['last_bonus_claim'] = datetime.datetime.now().isoformat()
    save_user_data(user_data)

# --- BOT INITIALIZATION ---
bot = telebot.TeleBot(BOT_TOKEN)

# --- KEYBOARDS ---
def quick_links_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [
        types.InlineKeyboardButton("💰 Binance USDC", url="https://www.binance.com/referral/earn-together/refer2earn-usdc/claim?ref=GRO_28502_AJGKM"),
        types.InlineKeyboardButton("🤝 Bybit Invite", url="https://www.bybit.com/invite?ref=4VKMRKG"),
        types.InlineKeyboardButton("🛍️ Shopee Affiliate", url="https://s.shopee.co.th/8V3vsXLPEw"),
        types.InlineKeyboardButton("📦 AliExpress Deals", url="https://fas.st/z-UHyv"),
        types.InlineKeyboardButton("💼 Fiverr Freelance", url="https://www.fiverr.com/pe/5r2Zej6"),
        types.InlineKeyboardButton("📈 Admitad Affiliate", url="https://www.admitad.com/affiliate-publishers/?ref=ndiypas8sz"),
        types.InlineKeyboardButton("🌐 Blogspot", url="https://phyowailin34.blogspot.com/?m=1"),
        types.InlineKeyboardButton("🌳 Linktree", url="https://linktr.ee/Linp9"),
        # YouTube လင့်ခ်အသစ် နှစ်ခုကို ဤနေရာတွင် ထည့်သွင်းထားပါသည်
        types.InlineKeyboardButton("📺 YouTube Channel 1", url="https://www.youtube.com/@DigitalWealthTips-q8i"),
        types.InlineKeyboardButton("📺 YouTube Channel 2", url="https://youtube.com/@phyowailin-l1z")
    ]
    markup.add(*btns)
    markup.row(types.InlineKeyboardButton("📢Main VIP Channel 🚀", url="https://t.me/kophyowailin553"))
    return markup

def main_menu_markup(user_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('👤 Account', '🔗 All My Channels', '👨‍👩‍👧‍👦 Refer & Earn', '🎁 Daily Bonus', '💳 Withdraw')
    if user_id == ADMIN_ID:
        markup.add('⚙️ Admin: User စစ်ရန်')
    return markup

# --- COMMANDS ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    
    # Referral code ကို စစ်ဆေးခြင်း
    args = message.text.split()
    referrer_id = args[1] if len(args) > 1 else None
    
    get_user(user_id, first_name, referrer_id)

    welcome = (
        f"👋 Welcome, {first_name}!\n\n"
        "Welcome to Digital Wealth Tips! 🎉\n"
        "ကျွန်တော်က Phyo Wai Lin ပါ။ အောက်က ခလုတ်တွေကို နှိပ်ပြီး စတင်နိုင်ပါပြီ။"
    )
    bot.send_message(message.chat.id, welcome, reply_markup=quick_links_markup())
    bot.send_message(message.chat.id, "Please select an option from the main menu:", reply_markup=main_menu_markup(user_id))

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    user_id = message.from_user.id
    user = get_user(user_id, message.from_user.first_name)

    if message.text == '👤 Account':
        msg = f"👤 Name: {user['first_name']}\n💵 Balance: {user['balance']:.2f} USDC\n👥 Referrals: {user.get('referrals', 0)} ယောက်"
        bot.send_message(message.chat.id, msg)
    
    elif message.text == '🔗 All My Channels':
        bot.send_message(message.chat.id, "📌 Official Channel:\nhttps://t.me/kophyowailin553")
    
    elif message.text == '👨‍👩‍👧‍👦 Refer & Earn':
        bot_info = bot.get_me()
        ref_link = f"https://t.me/{bot_info.username}?start={user_id}"
        msg = (
            "👨‍👩‍👧‍👦 **Referral Program**\n\n"
            "သင့်ရဲ့ Referral Link ကိုသုံးပြီး သူငယ်ချင်းတွေကို ဖိတ်ခေါ်ပါ။\n"
            f"လူတစ်ယောက်ဝင်လာတိုင်း {REFERRAL_BONUS} USDC ရရှိပါမည်။\n\n"
            f"🔗 သင့်ရဲ့ Link: `{ref_link}`"
        )
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")

    elif message.text == '🎁 Daily Bonus':
        if user['last_bonus_claim']:
            last_claim_date = datetime.datetime.fromisoformat(user['last_bonus_claim']).date()
            if last_claim_date == datetime.date.today():
                bot.send_message(message.chat.id, "❌ ယနေ့အတွက် Bonus ရယူပြီးပါပြီ။")
                return
        
        bonus_amount = 0.50
        update_user_balance(user_id, bonus_amount)
        update_last_bonus_claim(user_id)
        bot.send_message(message.chat.id, f"✅ Bonus {bonus_amount:.2f} USDC ရရှိပါပြီ။")

    elif message.text == '💳 Withdraw':
        min_withdraw = 10.00
        if user['balance'] >= min_withdraw:
            bot.send_message(message.chat.id, "✅ ငွေထုတ်ယူရန် အဆင်သင့်ဖြစ်ပါပြီ။")
        else:
            bot.send_message(message.chat.id, f"⚠️ အနည်းဆုံး {min_withdraw:.2f} USDC လိုအပ်ပါသည်။ သင့်လက်ကျန်: {user['balance']:.2f} USDC")

    elif message.text == '⚙️ Admin: User စစ်ရန်' and user_id == ADMIN_ID:
        total_users = len(user_data)
        bot.send_message(message.chat.id, f"📊 စုစုပေါင်း User: {total_users} ယောက်")

# --- FLASK SERVER & BOT STARTING ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is running!"

if __name__ == "__main__":
    t = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))))
    t.daemon = True
    t.start()
    print("Bot is starting...")
    bot.infinity_polling()