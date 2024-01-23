import requests
import time 

telegram_bot_token = "6527497624:AAFrw5CxRcGtAPUYfr3T1yY7-gY-0iosK7c"
target_group_chat_id = -1002095021922  # Replace with the actual ID of your group chat (prefixed with -100)


# Variable to store the ID of the latest processed message
latest_processed_message_id = 0

def get_updates():
    telegram_api_url = f"https://api.telegram.org/bot{telegram_bot_token}/getUpdates"
    response = requests.get(telegram_api_url)

    if response.status_code == 200:
        updates = response.json().get('result', [])
        return updates
    else:
        print(f"Error: {response.status_code}")
        return None

def delete_message(chat_id, message_id):
    telegram_api_url = f"https://api.telegram.org/bot{telegram_bot_token}/deleteMessage"
    params = {'chat_id': chat_id, 'message_id': message_id}
    response = requests.get(telegram_api_url, params=params)

    if response.status_code == 200:
        print(f"Message deleted successfully in chat ID {chat_id}")
    else:
        print(f"Error deleting message in chat ID {chat_id}: {response.status_code}")

# Continuous polling
while True:
    updates = get_updates()

    if updates:
        for update in updates:
            chat_id = update.get('message', {}).get('chat', {}).get('id')
            message_text = update.get('message', {}).get('text')
            message_id = update.get('message', {}).get('message_id')

            if chat_id == target_group_chat_id and message_id > latest_processed_message_id:
                print(f"Received message '{message_text}' from chat ID {chat_id}")

                # Check if the message contains "سلام" and delete it
                if "سلام" in message_text:
                    delete_message(chat_id, message_id)

                # Update the latest processed message ID
                latest_processed_message_id = message_id

    time.sleep(0.5)  # Wait for 1 second before the next iteration