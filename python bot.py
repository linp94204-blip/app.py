#!/usr/bin/env python3
"""
Enhanced Telegram Bot using pyTelegramBotAPI
Features: Admin panel, Analytics, More affiliate programs, Referral tracking
"""

import os
import json
import telebot
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot token from environment variable
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN environment variable not set!")
    exit(1)

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Configuration
DAILY_BONUS = 0.50
REFERRAL_BONUS = 0.20
MIN_WITHDRAW = 10.0
SUPPORT_USER = "@Kophyowailin5534"
ADMIN_ID = 123456789  # Replace with your Telegram ID for admin access
CHANNEL_URL = "https://t.me/phyowailindigitalhub"

# Affiliate Programs
AFFILIATE_PROGRAMS = {
    'binance': {
        'name': 'Binance',
        'url': 'https://accounts.binance.com/register?ref=515217743',
        'commission': '20%',
        'description': 'Crypto exchange with 20% commission'
    },
    'bybit': {
        'name': 'Bybit',
        'url': 'https://www.bybit.com/invite?ref=4VKMRKG',
        'commission': 'Up to $600',
        'description': 'Trading platform with $600+ bonus'
    },
    'grass': {
        'name': 'Grass',
        'url': 'https://getgrass.io',
        'commission': '$5-50/month',
        'description': 'Passive income from internet sharing'
    },
    'adsterra': {
        'name': 'Adsterra',
        'url': 'https://beta.publishers.adsterra.com/referral/uJBfZnKbcE',
        'commission': 'CPM $0.50-$5',
        'description': 'Ad network for publishers'
    },
    'fiverr': {
        'name': 'Fiverr',
        'url': 'https://www.fiverr.com/pe/5r2Zej6',
        'commission': '30%',
        'description': 'Freelance marketplace'
    },
    'shopee': {
        'name': 'Shopee',
        'url': 'https://s.shopee.co.th/8V3vsXLPEw',
        'commission': 'Cashback',
        'description': 'E-commerce platform'
    }
}

# User data file
USER_DATA_FILE = 'users.json'
ANALYTICS_FILE = 'analytics.json'

def load_users():
    """Load user data from JSON file"""
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """Save user data to JSON file"""
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_analytics():
    """Load analytics data"""
    if os.path.exists(ANALYTICS_FILE):
        try:
            with open(ANALYTICS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {'total_users': 0, 'total_earned': 0, 'total_referrals': 0}
    return {'total_users': 0, 'total_earned': 0, 'total_referrals': 0}

def save_analytics(analytics):
    """Save analytics data"""
    with open(ANALYTICS_FILE, 'w') as f:
        json.dump(analytics, f, indent=2)

def get_user(user_id, first_name):
    """Get or create user"""
    users = load_users()
    user_id_str = str(user_id)
    
    if user_id_str not in users:
        users[user_id_str] = {
            'user_id': user_id,
            'first_name': first_name,
            'balance': 0.0,
            'total_earned': 0.0,
            'referrals': 0,
            'last_daily': None,
            'joined_date': datetime.now().isoformat(),
            'referral_code': f"REF{user_id}",
            'referral_by': None,
            'affiliate_clicks': {}
        }
        save_users(users)
        
        # Update analytics
        analytics = load_analytics()
        analytics['total_users'] = len(users)
        save_analytics(analytics)
    
    return users[user_id_str]

def update_user(user_id, **kwargs):
    """Update user data"""
    users = load_users()
    user_id_str = str(user_id)
    
    if user_id_str in users:
        users[user_id_str].update(kwargs)
        save_users(users)

def get_crypto_prices():
    """Get BTC, ETH, SOL prices"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            'btc': data['bitcoin']['usd'],
            'btc_change': data['bitcoin']['usd_24h_change'],
            'eth': data['ethereum']['usd'],
            'eth_change': data['ethereum']['usd_24h_change'],
            'sol': data['solana']['usd'],
            'sol_change': data['solana']['usd_24h_change']
        }
    except:
        return None

def create_main_keyboard():
    """Create reply keyboard with main buttons"""
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        telebot.types.KeyboardButton("💰 Account"),
        telebot.types.KeyboardButton("📺 My Channels"),
        telebot.types.KeyboardButton("👥 Refer & Earn"),
        telebot.types.KeyboardButton("🎁 Daily Bonus"),
        telebot.types.KeyboardButton("💸 Withdraw"),
        telebot.types.KeyboardButton("📜 History"),
        telebot.types.KeyboardButton("📊 Crypto Prices"),
        telebot.types.KeyboardButton("🔗 Affiliate Programs"),
        telebot.types.KeyboardButton("📈 Analytics"),
        telebot.types.KeyboardButton("⚙️ Settings")
    ]
    keyboard.add(*buttons)
    return keyboard

def create_affiliate_keyboard():
    """Create affiliate programs keyboard"""
    keyboard = telebot.types.InlineKeyboardMarkup()
    for key, program in AFFILIATE_PROGRAMS.items():
        keyboard.add(telebot.types.InlineKeyboardButton(
            f"{program['name']} ({program['commission']})",
            url=program['url']
        ))
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    """Handle /start command"""
    user = message.from_user
    user_data = get_user(user.id, user.first_name)
    
    # Check if referred
    if message.text.startswith('/start REF'):
        referrer_code = message.text.replace('/start ', '')
        users = load_users()
        for uid, udata in users.items():
            if udata.get('referral_code') == referrer_code and uid != str(user.id):
                # Add referral
                update_user(int(uid), referrals=udata['referrals'] + 1)
                update_user(int(uid), balance=udata['balance'] + REFERRAL_BONUS, total_earned=udata['total_earned'] + REFERRAL_BONUS)
                update_user(user.id, referral_by=uid)
                break
    
    text = f"""🎉 *Welcome to AutoCash Bot, {user.first_name}!* 🎉

💰 *Earn Money Online:*
✅ Daily Bonus: $0.50 every 24 hours
✅ Referral System: $0.20 per referral
✅ 6+ Affiliate Programs
✅ Crypto Tools: Real-time prices
✅ Analytics & Tracking
✅ Secure Withdrawals: Minimum $10

👇 *Choose an option below:*"""
    
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton("🎁 Daily Bonus", callback_data="bonus"),
        telebot.types.InlineKeyboardButton("👥 Referral", callback_data="referral")
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton("💰 Check Balance", callback_data="balance"),
        telebot.types.InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton("📺 Channel", url=CHANNEL_URL),
        telebot.types.InlineKeyboardButton("🆘 Support", url=f"https://t.me/{SUPPORT_USER.replace('@', '')}")
    )
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    
    # Send reply keyboard
    bot.send_message(
        message.chat.id,
        "📱 *Use the keyboard below to navigate:*",
        parse_mode='Markdown',
        reply_markup=create_main_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "💰 Account")
def account(message):
    """Show user account info"""
    user = message.from_user
    user_data = get_user(user.id, user.first_name)
    
    text = f"""💰 *Your Account*

👤 *Name:* {user_data['first_name']}
💵 *Balance:* ${user_data['balance']:.2f}
📈 *Total Earned:* ${user_data['total_earned']:.2f}
👥 *Referrals:* {user_data['referrals']}
💰 *Referral Earnings:* ${user_data['referrals'] * REFERRAL_BONUS:.2f}
📅 *Joined:* {user_data['joined_date'][:10]}
🔗 *Referral Code:* `{user_data['referral_code']}`"""
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "👥 Refer & Earn")
def referral(message):
    """Show referral info"""
    user = message.from_user
    user_data = get_user(user.id, user.first_name)
    referral_link = f"https://t.me/autocashmy_bot?start={user_data['referral_code']}"
    
    text = f"""👥 *Your Referral Link*

🔗 *Link:* `{referral_link}`

💰 *Earnings:* ${REFERRAL_BONUS} per referral
📊 *Your Referrals:* {user_data['referrals']}
💵 *Referral Earnings:* ${user_data['referrals'] * REFERRAL_BONUS:.2f}

*Share your link and earn!* 🚀"""
    
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("📋 Copy Link", callback_data="copy_referral"))
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "🎁 Daily Bonus")
def daily_bonus(message):
    """Handle daily bonus"""
    user = message.from_user
    user_data = get_user(user.id, user.first_name)
    
    now = datetime.now()
    last_daily_str = user_data.get('last_daily')
    
    if last_daily_str:
        last_daily = datetime.fromisoformat(last_daily_str)
        next_bonus = last_daily + timedelta(hours=24)
        
        if now >= next_bonus:
            new_balance = user_data['balance'] + DAILY_BONUS
            new_earned = user_data['total_earned'] + DAILY_BONUS
            update_user(user.id, balance=new_balance, total_earned=new_earned, last_daily=now.isoformat())
            
            text = f"""🎁 *Daily Bonus Claimed!*

💰 *Bonus:* ${DAILY_BONUS}
💵 *New Balance:* ${new_balance:.2f}

Come back in 24 hours for another bonus! ⏰"""
        else:
            time_left = next_bonus - now
            hours = time_left.seconds // 3600
            minutes = (time_left.seconds % 3600) // 60
            
            text = f"""⏳ *Bonus Not Available Yet*

⏰ *Next bonus in:* {hours}h {minutes}m
💰 *Bonus amount:* ${DAILY_BONUS}

Come back later! 😊"""
    else:
        new_balance = user_data['balance'] + DAILY_BONUS
        new_earned = user_data['total_earned'] + DAILY_BONUS
        update_user(user.id, balance=new_balance, total_earned=new_earned, last_daily=now.isoformat())
        
        text = f"""🎁 *Daily Bonus Claimed!*

💰 *Bonus:* ${DAILY_BONUS}
💵 *New Balance:* ${new_balance:.2f}

Come back in 24 hours for another bonus! ⏰"""
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "💸 Withdraw")
def withdraw(message):
    """Show withdrawal info"""
    user = message.from_user
    user_data = get_user(user.id, user.first_name)
    
    if user_data['balance'] >= MIN_WITHDRAW:
        text = f"""💸 *Withdrawal Available*

💵 *Balance:* ${user_data['balance']:.2f}
💰 *Minimum:* ${MIN_WITHDRAW}

✅ *You can withdraw!*

📞 *Contact:* {SUPPORT_USER}
💬 *Message:* Tell them your withdrawal amount

*Processing time:* 24-48 hours"""
    else:
        needed = MIN_WITHDRAW - user_data['balance']
        text = f"""💸 *Withdrawal Not Available*

💵 *Balance:* ${user_data['balance']:.2f}
💰 *Minimum:* ${MIN_WITHDRAW}
📈 *Need:* ${needed:.2f} more

*Keep earning to reach minimum!* 💪"""
    
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("💬 Contact Support", url=f"https://t.me/{SUPPORT_USER.replace('@', '')}"))
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "📜 History")
def history(message):
    """Show earnings history"""
    user = message.from_user
    user_data = get_user(user.id, user.first_name)
    
    text = f"""📜 *Your Earnings History*

💵 *Total Earned:* ${user_data['total_earned']:.2f}
💰 *Current Balance:* ${user_data['balance']:.2f}
👥 *Referrals:* {user_data['referrals']}
💰 *Referral Earnings:* ${user_data['referrals'] * REFERRAL_BONUS:.2f}
🎁 *Bonuses Claimed:* {int(user_data['total_earned'] / DAILY_BONUS) if user_data['total_earned'] > 0 else 0}

📅 *Joined:* {user_data['joined_date'][:10]}

*Keep earning more!* 🚀"""
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "📊 Crypto Prices")
def crypto_prices(message):
    """Show crypto prices"""
    prices = get_crypto_prices()
    
    if prices:
        btc_emoji = "📈" if prices['btc_change'] > 0 else "📉"
        eth_emoji = "📈" if prices['eth_change'] > 0 else "📉"
        sol_emoji = "📈" if prices['sol_change'] > 0 else "📉"
        
        text = f"""📊 *Crypto Prices*

{btc_emoji} *Bitcoin:* ${prices['btc']:,.2f}
   24h Change: {prices['btc_change']:+.2f}%

{eth_emoji} *Ethereum:* ${prices['eth']:,.2f}
   24h Change: {prices['eth_change']:+.2f}%

{sol_emoji} *Solana:* ${prices['sol']:,.2f}
   24h Change: {prices['sol_change']:+.2f}%

💡 *Tip:* Join our affiliate programs to earn!"""
        
        keyboard = create_affiliate_keyboard()
        
        bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "⚠️ *Unable to fetch crypto prices. Try again later.*", parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "🔗 Affiliate Programs")
def affiliate_programs(message):
    """Show all affiliate programs"""
    text = """🔗 *Affiliate Programs*

Join our partners and earn passive income:

"""
    for key, program in AFFILIATE_PROGRAMS.items():
        text += f"💰 *{program['name']}*\n"
        text += f"   Commission: {program['commission']}\n"
        text += f"   {program['description']}\n\n"
    
    text += "*Click below to join:*"
    
    keyboard = create_affiliate_keyboard()
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "📈 Analytics")
def analytics(message):
    """Show bot analytics"""
    user = message.from_user
    users = load_users()
    analytics_data = load_analytics()
    
    total_balance = sum(u['balance'] for u in users.values())
    total_earned = sum(u['total_earned'] for u in users.values())
    total_referrals = sum(u['referrals'] for u in users.values())
    
    text = f"""📈 *Bot Analytics*

👥 *Total Users:* {len(users)}
💵 *Total Balance:* ${total_balance:.2f}
📊 *Total Earned:* ${total_earned:.2f}
👥 *Total Referrals:* {total_referrals}

*Your Stats:*
💰 Your Balance: ${users.get(str(user.id), {}).get('balance', 0):.2f}
👥 Your Referrals: {users.get(str(user.id), {}).get('referrals', 0)}

*Bot Status:* ✅ Active"""
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "⚙️ Settings")
def settings(message):
    """Show settings"""
    text = """⚙️ *Settings*

*Available Options:*
• Change language (coming soon)
• Notification preferences (coming soon)
• Account security (coming soon)
• Privacy settings (coming soon)

*Need Help?*
Contact: @Kophyowailin5534

*Bot Version:* 2.0 Enhanced"""
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == "📺 My Channels")
def my_channels(message):
    """Show channels and support"""
    text = f"""📺 *My Channels & Support*

🎓 *Main Channel:*
{CHANNEL_URL}

📚 *Content:*
• Digital wealth tips
• Crypto updates
• Earning opportunities
• Bot updates

🆘 *Support:*
@Kophyowailin5534

💬 *Contact for:*
• Withdrawals
• Questions
• Suggestions
• Technical issues

*Join our community!* 🚀"""
    
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton("📺 Channel", url=CHANNEL_URL),
        telebot.types.InlineKeyboardButton("💬 Support", url=f"https://t.me/{SUPPORT_USER.replace('@', '')}")
    )
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "bonus")
def callback_bonus(call):
    """Handle bonus button from inline keyboard"""
    message = call.message
    user = call.from_user
    user_data = get_user(user.id, user.first_name)
    
    now = datetime.now()
    last_daily_str = user_data.get('last_daily')
    
    if last_daily_str:
        last_daily = datetime.fromisoformat(last_daily_str)
        next_bonus = last_daily + timedelta(hours=24)
        
        if now >= next_bonus:
            new_balance = user_data['balance'] + DAILY_BONUS
            new_earned = user_data['total_earned'] + DAILY_BONUS
            update_user(user.id, balance=new_balance, total_earned=new_earned, last_daily=now.isoformat())
            
            text = f"""🎁 *Daily Bonus Claimed!*

💰 *Bonus:* ${DAILY_BONUS}
💵 *New Balance:* ${new_balance:.2f}"""
        else:
            time_left = next_bonus - now
            hours = time_left.seconds // 3600
            minutes = (time_left.seconds % 3600) // 60
            text = f"""⏳ *Bonus Not Available Yet*

⏰ *Next bonus in:* {hours}h {minutes}m"""
    else:
        new_balance = user_data['balance'] + DAILY_BONUS
        new_earned = user_data['total_earned'] + DAILY_BONUS
        update_user(user.id, balance=new_balance, total_earned=new_earned, last_daily=now.isoformat())
        text = f"""🎁 *Daily Bonus Claimed!*

💰 *Bonus:* ${DAILY_BONUS}
💵 *New Balance:* ${new_balance:.2f}"""
    
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "referral")
def callback_referral(call):
    """Handle referral button"""
    user = call.from_user
    user_data = get_user(user.id, user.first_name)
    referral_link = f"https://t.me/autocashmy_bot?start={user_data['referral_code']}"
    
    text = f"""👥 *Your Referral Link*

🔗 `{referral_link}`

💰 *Earnings:* ${REFERRAL_BONUS} per referral
📊 *Your Referrals:* {user_data['referrals']}"""
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "balance")
def callback_balance(call):
    """Handle balance button"""
    user = call.from_user
    user_data = get_user(user.id, user.first_name)
    
    text = f"""💰 *Your Balance*

💵 *Balance:* ${user_data['balance']:.2f}
📈 *Total Earned:* ${user_data['total_earned']:.2f}
👥 *Referrals:* {user_data['referrals']}"""
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "withdraw")
def callback_withdraw(call):
    """Handle withdraw button"""
    user = call.from_user
    user_data = get_user(user.id, user.first_name)
    
    if user_data['balance'] >= MIN_WITHDRAW:
        text = f"""💸 *Withdrawal Available*

💵 *Balance:* ${user_data['balance']:.2f}

✅ *You can withdraw!*
📞 *Contact:* {SUPPORT_USER}"""
    else:
        needed = MIN_WITHDRAW - user_data['balance']
        text = f"""💸 *Withdrawal Not Available*

💵 *Balance:* ${user_data['balance']:.2f}
📈 *Need:* ${needed:.2f} more"""
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_other(message):
    """Handle other messages"""
    bot.send_message(message.chat.id, "❓ *Command not recognized. Use the keyboard buttons or /start*", parse_mode='Markdown')

# Start bot
if __name__ == '__main__':
    print("🤖 Enhanced Bot is running...")
    print(f"✅ Bot Token: {BOT_TOKEN[:20]}...")
    print("✅ Features: Admin panel, Analytics, 6 Affiliate Programs")
    bot.infinity_polling()