import os
import telebot
import cv2
from telebot import types
import csv

TOKEN = "6356574896:AAEBq_cjz9XNvbC7KahWhzmkLXd2ZBMEd6c"
IMAGES_DIR = 'images'
USERS_CSV_FILE = 'users.csv'

bot = telebot.TeleBot(TOKEN)

welcome = """
    کاربر گرامی لطفا ابتدا در دو پیام جداگانه نام و نام خانوادگی خود را مانند مثال زیر ارسال کنید.
    
    رضا
    رضایی

    📷 کاربر گرامی لطفا تصویر پروفایل خود را برای ربات ارسال کنید.

    ⛔ توجه داشته باشید که این بات به سیستم تشخیص چهره مجهز میباشد و اگر سیع کنید آن را فریب دهید شما را بلاک میکند و گزارش شما را به تلگرام ارسال میکند.
    """
def save_user_info(user_id, first_name, last_name):
    with open(USERS_CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['User ID', 'First Name', 'Last Name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header if the file is empty
        if os.stat(USERS_CSV_FILE).st_size == 0:
            writer.writeheader()

        # Encode Unicode characters before writing
        writer.writerow(user_id)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, welcome)
    bot.send_message(message.chat.id, "ابتدا نام کوچک خود را ارسال کنید.")


@bot.message_handler(func=lambda message: True)
def handle_first_name(message):
    if message.text:
        # Save the first name and prompt for the last name
        bot.send_message(message.chat.id, 'لطفا حال فامیلی خود را ارسال کنید.')
        bot.register_next_step_handler(message, handle_last_name)
    else:
        bot.send_message(message.chat.id, 'مشکلی پیش آمده لطفا دوباره نام خود را ارسال کنید.')

def handle_last_name(message):
    if message.text:
        # Save the last name and prompt for the image
        first_name = message.text
        user_id = message.from_user.id

        bot.send_message(message.chat.id, 'متشکریم, حال تصویر خود را ارسال کنید.')

        # Save user info to CSV
        save_user_info(user_id, first_name, last_name=None)

        # Handle receiving the image
        bot.register_next_step_handler(message, handle_image)
    else:
        bot.send_message(message.chat.id, 'مشکلی پیش آمده لطفا دوباره فامیلی خود را ارسال کنید.')

@bot.message_handler(content_types=['photo'])
def handle_image(message):
    # Get and save image
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)

    file_name = f"{IMAGES_DIR}/{file_id}.png"
    
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Send confirmation message
    bot.send_message(message.chat.id, 'Your image has been successfully received and saved!')

    # Detect faces in the image
    image = cv2.imread(file_name)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    if len(faces) > 0:
        bot.send_message(message.chat.id, f'Number of faces detected: {len(faces)}')
    else:
        bot.send_message(message.chat.id, 'No faces detected in the image.')

    # Removing images after processing
    os.remove(file_name)

@bot.message_handler(func=lambda message: True)
def handle_other(message):
    if message.content_type != message.text != '/start' or message.text != '/users':
        bot.send_message(message.chat.id, 'Send the image only! Supported formats: PNG.')

bot.polling(none_stop=True)
