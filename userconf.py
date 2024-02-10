from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext, MessageHandler

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

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

async def callbakc_qury_handler(update:Update, context: ContextTypes.DEFAULT_TYPE):
    qury = update.callback_query
    call_back_data = qury.data

    cap = """
    📷 کاربر گرامی لطفا تصویر پروفایل خود را برای ربات ارسال کنید.

    ⛔ توجه داشته باشید که این بات به سیستم تشخیص چهره مجهز میباشد و اگر سیع کنید آن را فریب دهید شما را بلاک میکند و گزارش شما را به تلگرام ارسال میکند.
    """

    if call_back_data == '1':
            await context.bot.send_message(chat_id=update.effective_chat.id, text=cap,
                                   reply_to_message_id=update.effective_message.id,)
    

def main():
    app = Application.builder().token("6527497624:AAFrw5CxRcGtAPUYfr3T1yY7-gY-0iosK7c").build()


    app.add_handlers([
        CommandHandler('start', start),
        CallbackQueryHandler(callbakc_qury_handler),
    ])

    app.run_polling()

if __name__=='__main__':
    main()