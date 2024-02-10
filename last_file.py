import requests
import time 


telegram_bot_token = "6527497624:AAFrw5CxRcGtAPUYfr3T1yY7-gY-0iosK7c"
target_group_chat_id = -1002095021922  
# second_group_chat_id = -1001315042535 orginal-ID
second_group_invite_link = "https://t.me/+LMN6l6dVtx1hM2Vk"

authentication_link = "https://t.me/itegroup_bot"
latest_processed_message_id = 0
latest_processed_message_ids = {}

# Dictionary to store information about users whose data has been sent to admin
users_data_sent_to_admin = {}
users_informed = {}

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

def download_profile_photo(file_id):
    file_info_url = f"https://api.telegram.org/bot{telegram_bot_token}/getFile"
    file_info_params = {'file_id': file_id}
    response = requests.get(file_info_url, params=file_info_params)

    if response.status_code == 200:
        file_path = response.json().get('result', {}).get('file_path')
        if file_path:
            photo_url = f"https://api.telegram.org/file/bot{telegram_bot_token}/{file_path}"
            photo_response = requests.get(photo_url)
            if photo_response.status_code == 200:
                return photo_response.content
            else:
                print("Error downloading profile photo.")
        else:
            print("File path not found in response.")
    else:
        print("Error getting file info.")

def get_user_profile_photos(user_id):
    url = f"https://api.telegram.org/bot{telegram_bot_token}/getUserProfilePhotos"
    payload = {
        "user_id": user_id,
        "offset": 0,
        "limit": 1
    }
    headers = {
        "Accept": "application/json",
        "User-Agent": "Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

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

        admin_id = '358040589'
        # admin_id_second = '5495848617'

        if chat_id == target_group_chat_id and message_id > latest_processed_message_ids.get(chat_id, 0):
            print(f"Received message '{message_text}' from chat ID {chat_id}")

            if not (first_name and last_name and user_id):
                reply_message = f"کاربر گرامی لطفا تصویر پروفایل خود را با یک عکس سلفی از خودتان جایگذین کنید و نام و فامیلی خود را نیز در پرفایل خود بگذارید . \n کاربر گرامی این کار برای امنیت شما کاربران گروه است. \n ⚠️ لطفا از لینک زیر پیام وارد بات شوید و عکس سلفی خود و مشخصات خود را ارسال کنید این کار الزامی است. \nUser ID: @{user_id}\n{authentication_link}"
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
                    user_profile_photos = get_user_profile_photos(user_info.get('id'))
                    if user_profile_photos.get('result', {}).get('photos'):
                        # Download and send profile photo
                        photo_data = download_profile_photo(user_profile_photos['result']['photos'][0][0]['file_id'])
                        if photo_data:
                            send_photo_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendPhoto"
                            files = {'photo': photo_data}
                            send_photo_params = {'chat_id': admin_id, 'caption': f"نام: {first_name}\nنام خانوادگی: {last_name}\nUsername: @{user_id}\nUser ID: {user_info['id']}"}
                            response = requests.post(send_photo_url, files=files, data=send_photo_params)

                            # send_photo_params_second = {'chat_id': admin_id_second, 'caption': f"نام: {first_name}\nUsername: @{user_id}\nUser ID: {user_info['id']}"}
                            # response = requests.post(send_photo_url, files=files, data=send_photo_params_second)

                            if response.status_code != 200:
                                print("Error sending photo.")
                            else:
                                # Store user data to prevent sending it again to admin
                                users_data_sent_to_admin[user_id] = True
                    else:
                        reply_message = f"لطفا عکس پروفایل خود را اصلاح کنید.\nUser ID: @{user_id}\n{authentication_link}"
                        reply_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
                        reply_params = {'chat_id': chat_id, 'text': reply_message, 'reply_to_message_id': message_id}
                        requests.get(reply_url, params=reply_params)
                        requests.get(f"https://api.telegram.org/bot{telegram_bot_token}/deleteMessage", params={'chat_id': chat_id, 'message_id': message_id})

            latest_processed_message_ids[chat_id] = message_id

    if updates:
        latest_processed_message_id = max(update.get('update_id') for update in updates) + 1
    

    time.sleep(0.2)

