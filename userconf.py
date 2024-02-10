from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, ContextTypes

FIRST_NAME, LAST_NAME = range(2)
user_ids = []  # Global list to store user IDs

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keys = [[InlineKeyboardButton('ارسال اطلاعات', callback_data='1')]]
    markup = InlineKeyboardMarkup(keys)

    cap = """
    کاربر گرامی لطفا برای عضویت در گروه و ارسال پیام اطلاعات زیر را برای ما ارسال کنید.

    🧑🏻 نام و نام خانوادگی 
    🤳🏻 یک تصویر سلفی 

    ⚠️ توجه داشته باشید که این کار برای امنیت شما کاربران گروه میباشد.
    """

    await context.bot.send_message(chat_id=update.effective_chat.id, text=cap,
                                   reply_to_message_id=update.effective_message.id,
                                   reply_markup=markup)

    return FIRST_NAME

async def get_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    context.user_data['first_name'] = user_input

    return LAST_NAME  # Transition to the next state

async def get_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    context.user_data['last_name'] = user_input

    # Save user ID to the global list
    user_ids.append(update.effective_user.id)

    # Sending first name, last name, and user ID to the specified user ID
    first_name = context.user_data['first_name']
    last_name = context.user_data['last_name']
    message = f"User ID: {update.effective_user.id}\nFirst Name: {first_name}\nLast Name: {last_name}"
    await context.bot.send_message(chat_id=5645370293, text=message)

    await context.bot.send_message(chat_id=update.effective_chat.id, text="اطلاعات شما با موفقیت برای ادمین ارسال شد.")

    return ConversationHandler.END  # End the conversation

async def callbakc_qury_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    qury = update.callback_query
    call_back_data = qury.data

    cap = """
    کاربر گرامی لطفا ابتدا در دو پیام جداگانه نام و نام خانوادگی خود را مانند مثال زیر ارسال کنید.
    
    رضا
    رضایی

    📷 کاربر گرامی لطفا تصویر پروفایل خود را برای ربات ارسال کنید.

    ⛔ توجه داشته باشید که این بات به سیستم تشخیص چهره مجهز میباشد و اگر سیع کنید آن را فریب دهید شما را بلاک میکند و گزارش شما را به تلگرام ارسال میکند.
    """

    if call_back_data == '1':
        await context.bot.send_message(chat_id=update.effective_chat.id, text=cap,
                                       reply_to_message_id=update.effective_message.id)

async def print_user_ids(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_ids
    if user_ids:
        user_ids_str = '\n'.join(str(uid) for uid in user_ids)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"List of User IDs:\n{user_ids_str}")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="The list of user IDs is empty.")

def main():
    app = Application.builder().token("6527497624:AAFrw5CxRcGtAPUYfr3T1yY7-gY-0iosK7c").build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FIRST_NAME: [MessageHandler(None, get_first_name)],
            LAST_NAME: [MessageHandler(None, get_last_name)],
        },
        fallbacks=[]
    )

    app.add_handlers([
        conversation_handler,
        CallbackQueryHandler(callbakc_qury_handler),
        CommandHandler('print_user_ids', print_user_ids)  # Command handler to print the list of user IDs
    ])

    app.run_polling()

if __name__ == '__main__':
    main()