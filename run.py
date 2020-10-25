
from telegram.ext import MessageHandler, Filters, Updater
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)
import telegram.ext

import parser
import time
import datetime
import os
import logging
from configparser import ConfigParser

logging.basicConfig(filename='optimat.log', level=logging.INFO)
config = ConfigParser()
config.read('config.ini')


# this is the handler to answer incoming chat requests
p = parser.Parser()


updater = Updater(token=config.get(
    'main', 'TELEGRAM_BOT_TOKEN'), use_context=True)
scheduler = updater.job_queue
dispatcher = updater.dispatcher

# this handler reacts on messages sent to the bot


def error_callback(update, context):
    try:
        raise context.error
    except TimedOut:
        logging.exception("timeout error")
    except NetworkError:
        logging.exception("Network error")


def optimatHandler(update, context):
    try:
        result = p.parseInput(update.message.text)
        updater.bot.sendMessage(config.get(
            'main', 'MY_TELEGRAM_ID'), result['reply'])
    except Exception:
        logging.exception("Handlig telegram message failed")


optimat = MessageHandler(Filters.text, optimatHandler)
dispatcher.add_handler(optimat)
dispatcher.add_error_handler(error_callback)

# this handler is triggered via scheduler every 5min to update the dashboard in the kitchen


def callback_updateDashboard(context):
    try:
        p.updateDashboard()
    except Exception:
        logging.exception("Update of the dashboard server failed")


dashboardUpdateJob = scheduler.run_repeating(
    callback_updateDashboard, interval=300, first=1)

# scheduled chats, e.g. send traffic in the morning or the sbahn in the evening after work


def callback_sendTrain(context):
    try:
        result = p.parseInput('sbahn')
        updater.bot.sendMessage(config.get(
            'main', 'MY_TELEGRAM_ID'), result['reply'])
    except Exception:
        logging.exception("Scheduled train info could not be sent")


def callback_sendQuote(context):
    try:
        #result = p.parseInput('Thema test')
        p.saveRandomMotd()
        # updater.bot.sendMessage(config.get(
        #    'main', 'MY_TELEGRAM_ID'), result['reply'])
    except Exception:
        logging.exception("Scheduled quote info could not be sent")


# def callback_sendCorona(context):
#    try:
        #result = p.parseInput('Thema test')
#        p.getCorona()
        # updater.bot.sendMessage(config.get(
        #    'main', 'MY_TELEGRAM_ID'), result['reply'])
#    except Exception:
#        logging.exception("Scheduled corona info could not be sent")


# TrainUpdateJob = scheduler.run_daily(
#    callback_sendTrain, datetime.time(hour=22, minute=27, second=0))
QuoteUpdateJob = scheduler.run_daily(
    callback_sendQuote, datetime.time(hour=20, minute=20, second=0))

# CoronaUpdateJob = scheduler.run_daily(
#    callback_sendCorona, datetime.time(hour=6, minute=20, second=0))


logging.info("Started Optimat at")
logging.info(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"))

# This checks for new messages
try:
    updater.start_polling()
except:
    logging.exception("Telegram polling failed")
