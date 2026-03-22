import telebot
from telebot import types
import os

# --- TOKEN SETTING ---
# နည်းလမ်း (၁) - Token ကို ဒီနေရာမှာ တိုက်ရိုက်ထည့်ပါ (အသေချာဆုံးနည်းလမ်း)
TOKEN = "၇၄၈၃၉၂၀:ABC-DEF..." # သင့် Bot Token ကို ဒီမျက်တောင်ဖွင့်ပိတ်ထဲမှာ ထည့်ပါ

bot = telebot.TeleBot(TOKEN)

# --- KEYBOARDS ---
def quick_links_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    # သင်ပေးထားတဲ့ Link များ
    btns = [
        types.InlineKeyboardButton("💰 Binance USDC", url="https://www.binance.com/referral/earn-together/refer2earn-usdc/claim?hl=en&ref=GRO_28502_AJGKM"),
        types.InlineKeyboardButton("🤝 Bybit Invite", url="https://www.bybit.com/invite?ref=4VKMRKG"),
        types.InlineKeyboardButton("🛍️ Shopee Deals", url="https://s.shopee.co.th/8V3vsXLPEw"),
        types.InlineKeyboardButton("💼 Fiverr Freelance", url="https://www.fiverr.com/pe/5r2Zej6"),
        types.InlineKeyboardButton("🌐 My Blogspot", url="https://phyowailin34.blogspot.com/?m=1"),
        types.InlineKeyboardButton("🔥 New User Deals", url="https://s.shopee.co.th/6fcQyMRcjz"),
        types.InlineKeyboardButton("🌳 Linktree Links", url="https://linktr.ee/Linp9"),
        types.InlineKeyboardButton("📱 Play Store App", url="https://play.google.com/store/apps/details?id=in.co.websites.websitesapp")
    ]
    markup.add(*btns)
    markup.row(types.InlineKeyboardButton("📢 Official Channel", url="https://t.me/phyowaichannel"))
    return markup

def main_menu_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('👤 Account', '🔗 All My Channels', '🎁 Daily Bonus', '💳 Withdraw')
    return markup

# --- COMMANDS ---
@bot.message_handler(commands=['start'])
def start(message):
    welcome = (
        f"👋 Welcome, {message.from_user.first_name}!\n\n"
        "Welcome to Digital Wealth Tips! 🎉\n"
        "ကျွန်တော်က Phyo Wai Lin ပါ။ အောက်က ခလုတ်တွေကို နှိပ်ပြီး စတင်နိုင်ပါပြီ။"
    )
    # Welcome Message ပို့မယ်
    bot.send_message(message.chat.id, welcome, reply_markup=quick_links_markup())
    # အောက်က Menu ခလုတ်တွေ ပေါ်အောင် ထပ်ပို့မယ်
    bot.send_message(message.chat.id, "📎 Quick links-", reply_markup=main_menu_markup())

@bot.message_handler(func=lambda message: True)
def handle_msg(message):
    if message.text == '👤 Account':
        bot.send_message(message.chat.id, f"👤 Name: {message.from_user.first_name}\n💵 Balance: 0.00 USDC")
    elif message.text == '🔗 All My Channels':
        bot.send_message(message.chat.id, "📌 My Channels:\n@phyowaichannel\n@mycrypto_phyo\n@money12345ok")
    elif message.text == '🎁 Daily Bonus':
        bot.send_message(message.chat.id, "✅ ယနေ့အတွက် Bonus ရရှိပြီးပါပြီ။")
    elif message.text == '💳 Withdraw':
        bot.send_message(message.chat.id, "⚠️ ငွေထုတ်ယူရန် အနည်းဆုံး 10 USDC လိုအပ်ပါသည်။")

# --- BOT STARTING ---
if __name__ == "__main__":
    print("Bot is starting...")
    bot.infinity_polling()
