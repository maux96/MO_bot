from time import sleep
from types import TracebackType

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext

from handlers import get_handlers
from config import TOKEN


def main():

    app = ApplicationBuilder().token(TOKEN).build()

    handlers = get_handlers()

    print(f"Loaded {len(handlers)} handlers.")

    app.add_handlers(handlers=handlers)
    app.add_error_handler(error_handler)

    app.run_polling()

async def error_handler(obj: object, context: CallbackContext):
    if isinstance(obj, Update):
        await obj.message.reply_text(
            f"error raised, Error:\n{context.error}"
        )


main()
