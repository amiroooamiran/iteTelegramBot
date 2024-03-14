import os
import telebot
import cv2
from telebot import types
import csv
import time

TOKEN = "6356574896:AAEBq_cjz9XNvbC7KahWhzmkLXd2ZBMEd6c"
IMAGES_DIR = 'images'
USERS_CSV_FILE = 'users.csv'
ADMIN_ID_1 = 5645370293
ADMIN_ID_2 = 5495848617

bot = telebot.TeleBot(TOKEN)

welcome = """
    کاربر گرامی لطفا ابتدا در دو پیام جداگانه نام و نام خانوادگی خود را مانند مثال زیر ارسال کنید.

    رضا
    رضایی

    📷 کاربر گرامی لطفا تصویر پروفایل خود را برای ربات ارسال کنید.

    ⛔ توجه داشته باشید که این بات به سیستم تشخیص چهره مجهز میباشد و اگر سیع کنید آن را فریب دهید شما را بلاک میکند و گزارش شما را به تلگرام ارسال میکند.
"""

print("Bot is running ...")
def save_user_info(user_id, first_name, last_name):
    with open(USERS_CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['User ID', 'First Name', 'Last Name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header if the file is empty
        if os.stat(USERS_CSV_FILE).st_size == 0:
            writer.writeheader()

        # Encode Unicode characters before writing
        writer.writerow({'User ID': user_id, 'First Name': first_name, 'Last Name': last_name if last_name else ''})


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, welcome)
    bot.send_message(message.chat.id, "ابتدا نام کوچک خود را ارسال کنید.")

@bot.message_handler(func=lambda message: True)
def handle_first_name(message):
    if message.text:
        # Save the first name and prompt for the last name
        bot.send_message(message.chat.id, 'حال فامیلی خود را ارسال کنید.')
        bot.register_next_step_handler(message, handle_last_name, message.text)  # Pass the first name to the next step
    else:
        bot.send_message(message.chat.id, 'مشکلی پیش آمده لطفا دوباره نام خود را ارسال کنید.')

def handle_last_name(message, first_name):
    if message.text:
        # Save the last name and prompt for the image
        last_name = message.text
        user_id = message.from_user.id

        image_caption = """
        کاربر گرامی لطفا برای ارسال عکس دوربین جلوی تلفن خود را باز کنید و تصویر خود را ارسال کنید

        ربات مجهز به سیستم تشخیص چهره میباشد و در صورتی که بخواهید آن را دور بزنید شما را بلاک میکند.
        """

        bot.send_message(message.chat.id, image_caption)

        # Save user info to CSV
        save_user_info(user_id, first_name, last_name)

        # Handle receiving the image
        bot.register_next_step_handler(message, handle_image)
    else:
        bot.send_message(message.chat.id, 'مشکلی پیش آمده لطفا دوباره فامیلی خود را ارسال کنید.')

def is_selfie(image):
    # Load Haar Cascade classifier for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # If no faces detected, it's not a selfie
    if len(faces) == 0:
        return False

    # Calculate the distance between the camera and the face
    # Assuming known width of face (in cm) and focal length of the camera
    known_width = 14  # in centimeters (example)
    focal_length = 375.0  # example value
    for (x, y, w, h) in faces:
        per_width = w
        distance = (known_width * focal_length) / per_width

        # Accept as selfie if the distance is less than 18 cm
        if distance < 15:
            return True

    # If none of the detected faces meet the criteria, it's not a selfie
    return False



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

    # Detect faces in the image
    image = cv2.imread(file_name)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 1:
        if is_selfie(image):
            # Get user information from CSV
            user_id = message.from_user.id
            first_name = None
            last_name = None
            with open(USERS_CSV_FILE, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if int(row['User ID']) == user_id:
                        first_name = row['First Name']
                        last_name = row['Last Name']
                        break

            # If user information is found, send it to the admin
            if first_name:
                # Send user information to admin
                admin_message = f"User ID: {user_id}\nFirst Name: {first_name}\nLast Name: {last_name}"
                bot.send_message(ADMIN_ID_1, admin_message)
                bot.send_message(ADMIN_ID_2, admin_message)

                # Send the image to the admins
                bot.send_photo(ADMIN_ID_1, open(file_name, 'rb'))
                bot.send_photo(ADMIN_ID_2, open(file_name, 'rb'))

            # Save user information only if it's a selfie
            save_user_info(user_id, first_name, last_name)

            bot.send_message(message.chat.id, 'اطلاعات شما با موفقیت ثبت شد, حال میتوانید در گروه فعالبت کنید. \n از لینک زیر وارد گروه شوید و پیام بگذارید https://t.me/khodandaaz39')
        else:
            bot.send_message(message.chat.id, 'این تصویر مشخصات یک عکس سلفی را ندارد و بنابراین نام شما ذخیره نشده است.')
    else:
        bot.send_message(message.chat.id, 'چهره ایی در تصویر تشخیص داده نشد شما سیع کردید ربات را گول بزنید تا دقایق دیگر از گروه حدف خواهید شد.')

    # Removing images after processing
    os.remove(file_name)

@bot.message_handler(func=lambda message: True)
def handle_other(message):
    if message.content_type != message.text != '/start' or message.text != '/users':
        bot.send_message(message.chat.id, 'لطفا تصویر خود را ارسال کنید')

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(15)  # Wait 15 seconds before restarting