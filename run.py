
from telegram.ext import MessageHandler, Filters, Updater
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


def optimatHandler(update, context):
    result = p.parseInput(context.message.text)
    updater.bot.sendMessage(config.get(
        'main', 'MY_TELEGRAM_ID'), result['reply'])


optimat = MessageHandler(Filters.text, optimatHandler)
dispatcher.add_handler(optimat)

# this handler is triggered via scheduler every 5min to update the dashboard in the kitchen


def callback_updateDashboard(context: telegram.ext.CallbackContext):
    try:
        p.updateDashboard()
    except Exception:
        logging.exception("Update of the dashboard server failed")


dashboardUpdateJob = scheduler.run_repeating(
    callback_updateDashboard, interval=300, first=1)

# scheduled chats, e.g. send traffic in the morning or the sbahn in the evening after work


def callback_sendTrain(context: telegram.ext.CallbackContext):
    try:
        result = p.parseInput('sbahn')
        updater.bot.sendMessage(config.get(
            'main', 'TELEGRAM_BOT_TOKEN'), result['reply'])
    except Exception:
        logging.exception("Scheduled train info could not be sent")


TrainUpdateJob = scheduler.run_daily(
    callback_sendTrain, datetime.time(hour=17, minute=20, second=0))


# This checks for new messages
updater.start_polling()
