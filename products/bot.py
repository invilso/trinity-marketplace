#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from django.conf import settings
import sys
from django.dispatch import receiver
from django.db.models.signals import post_save
from asgiref.sync import sync_to_async, async_to_sync

import telegram

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, KeyboardButton
from .models import Product, Server, BotUser
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

SERVER, FILTER = range(2)

# Define the start handler function
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Get user information
    user = update.message.from_user

    # Check if the user is already registered
    bot_user, created = await sync_to_async(BotUser.objects.get_or_create)(telegram_id=user.id)

    # Create a list of servers as InlineKeyboardButtons
    servers = await sync_to_async(Server.objects.all)()
    keyboard = [[KeyboardButton(server.name)] for server in servers]
    reply_markup = ReplyKeyboardMarkup(keyboard)

    # Send the message to the user
    await update.message.reply_text(text="Welcome! Выберите ваш сервер (/cancel потом /start - поменять):", reply_markup=reply_markup)

    # Set the current conversation state to SERVER
    return SERVER

# Define the server handler function
async def server_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Get the selected server
    server_id = update.message.text
    server = await sync_to_async(Server.objects.get)(name=server_id)

    # Get user information
    user = update.message.from_user

    # Check if the user is already registered
    bot_user, created = await sync_to_async(BotUser.objects.get_or_create)(telegram_id=user.id)

    # Save the selected server to the user's profile
    bot_user.server = server
    bot_user.save()

    # Ask the user to enter a filter
    await update.message.reply_text(text='Введите запрос который вам интересен, или введите "skip" чтобы пропустить (/cancel потом /start - поменять):', reply_markup=ReplyKeyboardRemove())

    # Set the current conversation state to FILTER
    return FILTER

async def server_handler_reguser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text='Введите запрос который вам интересен, или введите "skip" чтобы пропустить (/cancel потом /start - поменять):')
    # Set the current conversation state to FILTER
    return FILTER

async def filter_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the filter from the user input
    filter_text = update.message.text

    # Get user information
    user = update.message.from_user

    # Check if the user is already registered
    bot_user, created = await sync_to_async(BotUser.objects.get_or_create)(telegram_id=user.id)

    # Save the filter to the user's profile
    bot_user.name_filter = filter_text
    bot_user.save()
    await update.message.reply_text(text='Ваш фильтр сохранен, приятного использования!')
    # Send the product list to the user
    return None

@receiver(post_save, sender=Product)
def product_created(sender, instance: Product, created, **kwargs):
    if created:
        photo_file = instance.photo.path
        
        message = f"<b>Новый товар добавлен: {instance.name}</b>\n\n{instance.description}\n\n<b>Цена:</b> ${instance.price}\n<b>Продавец:</b> {instance.nickname}\n<b>Создано:</b> {instance.created_at.strftime('%Y-%m-%d %H:%M')} UTC"
        logger.info(22)
        bot = telegram.Bot(token=settings.TELEGRAM_BOT_KEY)
        users = BotUser.objects.all()
        for user in users:
            logger.info(f'|{user.telegram_id}| |{user.server}| |{user.name_filter}|')
            if instance.filter_product(user.server, user.name_filter):
                logger.info(25)
                with open(photo_file, "rb") as f:
                    async_to_sync(bot.send_photo)(chat_id=user.telegram_id, photo=f, caption=message, parse_mode='HTML')

async def cancel_handler(update, context):
    user = update.message.from_user
    my_object = await sync_to_async(BotUser.objects.get)(telegram_id=user.id)
    my_object.delete()
    await update.message.reply_text(text='Бот отменен и вы удалены с базы, пока.')
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token=settings.TELEGRAM_BOT_KEY).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start_handler),
        ],
        states={
            SERVER: [MessageHandler(filters.Regex("^(RPG|RP1|RP2)$"), server_handler)],
            FILTER: [MessageHandler(filters.Regex(r"^(?!/)\w+"), filter_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel_handler)]
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()
