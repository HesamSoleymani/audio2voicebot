import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv
import os
import subprocess
import shlex
import random

load_dotenv()
TOKEN = os.getenv("TOKEN")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text("سلام " + user.first_name)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)


async def audio_to_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    document = update.message.document
    if document.mime_type.startswith("audio/"):
        await update.message.reply_text("در حال تبدیل فایل صوتی به پیام صوتی...")
        file = await document.get_file()
        random_id = str(random.randint(0, 1000))
        file_name = random_id + "_" + document.file_name
        file_path = await file.download_to_drive(custom_path=file_name)
        subprocess.run(
            shlex.split(
                "ffmpeg -i '"
                + file_name
                + "' -c:a libopus -b:a 20k -t 20 "
                + random_id
                + ".opus"
            )
        )
        await update.message.reply_voice(voice=open(random_id + ".opus", "rb"))
        os.remove(file_path)
        os.remove(random_id + ".opus")
        return
    update.message.reply_text("لطفا یک فایل صوتی ارسال کنید.")


def main() -> None:
    application = (
        Application.builder()
        .token(TOKEN)
        .base_url("https://tapi.bale.ai/bot")
        .base_file_url("https://tapi.bale.ai/file/bot")
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(MessageHandler(filters.ATTACHMENT, audio_to_voice))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
