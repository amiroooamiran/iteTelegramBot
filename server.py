import requests
import csv
import time 

telegram_bot_token = "7154487725:AAFXFPqgA79YqyRCckhKfYeLQ6l3rN0OunI"
target_group_chat_id = -1002093589132  # Replace with the actual ID of your group chat (prefixed with -100)

authentication_link = "https://t.me/itegroup_bot"
latest_processed_message_id = 0
latest_processed_message_ids = {}

# CSV file path containing user IDs
csv_file_path = "users.csv"

# Dictionary to store information about users whose data has been sent to admin
users_data_sent_to_admin = {}

def get_updates(offset=None):
    telegram_api_url = f"https://api.telegram.org/bot{telegram_bot_token}/getUpdates"
    params = {'offset': offset}
    response = requests.get(telegram_api_url, params=params)

    if response.status_code == 200:
        updates = response.json().get('result', [])
        return updates
    else:
        print(f"Error: {response.status_code}")
        return []

def check_user_id_in_csv(user_id):
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if user_id in row:
                return True
    return False

while True:
    updates = get_updates(offset=latest_processed_message_id)

    for update in updates:
        chat_id = update.get('message', {}).get('chat', {}).get('id')
        user_info = update.get('message', {}).get('from', {})
        user_id = user_info.get('username')
        message_text = update.get('message', {}).get('text')
        message_id = update.get('message', {}).get('message_id')

        admin_id = 'YOUR_ADMIN_TELEGRAM_ID'

        if chat_id == target_group_chat_id and message_id > latest_processed_message_ids.get(chat_id, 0):
            print(f"Received message '{message_text}' from chat ID {chat_id}")

            if not (user_id):
                reply_message = f"کاربر گرامی لطفا تصویر پروفایل خود را با یک عکس سلفی از خودتان جایگذین کنید و نام و فامیلی خود را نیز در پرفایل خود بگذارید . \n کاربر گرامی این کار برای امنیت شما کاربران گروه است. \nUser ID: @{user_id}\n{authentication_link}"
                reply_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
                reply_params = {'chat_id': chat_id, 'text': reply_message, 'reply_to_message_id': message_id}
                response = requests.get(reply_url, params=reply_params)
                requests.get(f"https://api.telegram.org/bot{telegram_bot_token}/deleteMessage", params={'chat_id': chat_id, 'message_id': message_id})
                            # Schedule deletion of reply_message after 10 seconds
                if response.status_code == 200:
                    time.sleep(15)
                    delete_params = {'chat_id': chat_id, 'message_id': response.json().get('result', {}).get('message_id')}
                    requests.get(f"https://api.telegram.org/bot{telegram_bot_token}/deleteMessage", params=delete_params)
            else:
                if user_id in users_data_sent_to_admin:
                    print(f"Data for user {user_id} has already been sent to admin.")
                else:
                    if check_user_id_in_csv(user_id):
                        reply_message = f"Your user ID exists in our records. Sending data to admin.\nUser ID: @{user_id}\n{authentication_link}"
                        reply_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
                        reply_params = {'chat_id': chat_id, 'text': reply_message, 'reply_to_message_id': message_id}
                        response = requests.get(reply_url, params=reply_params)
                        requests.get(f"https://api.telegram.org/bot{telegram_bot_token}/deleteMessage", params={'chat_id': chat_id, 'message_id': message_id})

                        if response.status_code == 200:
                            users_data_sent_to_admin[user_id] = True
                    else:
                        reply_message = f"Your user ID does not exist in our records. Please contact admin for assistance.\nUser ID: @{user_id}\n{authentication_link}"
                        reply_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
                        reply_params = {'chat_id': chat_id, 'text': reply_message, 'reply_to_message_id': message_id}
                        response = requests.get(reply_url, params=reply_params)
                        requests.get(f"https://api.telegram.org/bot{telegram_bot_token}/deleteMessage", params={'chat_id': chat_id, 'message_id': message_id})

            latest_processed_message_ids[chat_id] = message_id

    if updates:
        latest_processed_message_id = max(update.get('update_id') for update in updates) + 1

    time.sleep(0.2)
