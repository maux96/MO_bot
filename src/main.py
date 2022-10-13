from typing import Tuple, List, Dict, TypedDict

from os import environ
from time import sleep

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, ContextTypes

from handlers import get_handlers
from config import TOKEN


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    handlers = get_handlers()

    print(f"Loaded {len(handlers)} handlers.")
    app.add_handlers(handlers=handlers)

    app.add_error_handler(error_handler)

    app.run_polling()

async def error_handler(object: object, context: CallbackContext):
    if isinstance(object, Update):
        await object.message.reply_text(
            f"error raised, Error:\n{context.error}"
        )


while True:
    try:
        main()
    except Exception as e:
        print("No controlled Exception:\n",e)
        sleep(5)
