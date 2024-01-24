import requests
import time 

telegram_bot_token = "6527497624:AAFrw5CxRcGtAPUYfr3T1yY7-gY-0iosK7c"
target_group_chat_id = -1002095021922  # Replace with the actual ID of your group chat (prefixed with -100)


authentication_link = "https://t.me/itegroup_bot"
Bot_link = "https://t.me/itegroup_bot"
latest_processed_message_id = 0
latest_processed_message_ids = {}  # Dictionary to keep track of latest processed message for each chat_id

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

while True:
    updates = get_updates(offset=latest_processed_message_id)

    for update in updates:
        chat_id = update.get('message', {}).get('chat', {}).get('id')
        user_info = update.get('message', {}).get('from', {})
        user_id = user_info.get('username')
        first_name = user_info.get('first_name')
        last_name = user_info.get('last_name')
        message_text = update.get('message', {}).get('text')
        message_id = update.get('message', {}).get('message_id')

        if chat_id == target_group_chat_id and message_id > latest_processed_message_ids.get(chat_id, 0):
            print(f"Received message '{message_text}' from chat ID {chat_id}")

            # Check if the user has both first_name and last_name
            if not (first_name and last_name):
                # Reply to the message with user ID
                reply_message = f"لطفا ابتدا نام و نام خانوادگی خود را در پروفایل تلگرام اصلاح کنید\nUser ID: @{user_id}\n{authentication_link}"
                reply_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
                reply_params = {'chat_id': chat_id, 'text': reply_message, 'reply_to_message_id': message_id}
                requests.get(reply_url, params=reply_params)

                # Delete the original message
                requests.get(f"https://api.telegram.org/bot{telegram_bot_token}/deleteMessage", params={'chat_id': chat_id, 'message_id': message_id})

            # Update the latest processed message ID for the specific chat_id
            latest_processed_message_ids[chat_id] = message_id

    # Update the latest processed message ID for the entire loop
    if updates:
        latest_processed_message_id = max(update.get('update_id') for update in updates) + 1

    time.sleep(0.2)  # Adjust the sleep interval as needed