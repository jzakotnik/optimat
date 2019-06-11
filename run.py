
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


updater = Updater(token=config.get(
    'main', 'TELEGRAM_BOT_TOKEN'), use_context=True)
scheduler = updater.job_queue

dispatcher = updater.dispatcher
p = parser.Parser()


def callback_updateDashboard(context: telegram.ext.CallbackContext):
    p.updateDashboard()
    #print("Scheduler executed")


job = scheduler.run_repeating(
    callback_updateDashboard, interval=300, first=1)


def optimatHandler(update, context):
    result = p.parseInput(context.message.text)
    updater.bot.sendMessage(config.get(
        'main', 'MY_TELEGRAM_ID'), result['reply'])


optimat = MessageHandler(Filters.text, optimatHandler)
dispatcher.add_handler(optimat)

updater.start_polling()


def timeInRange(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


def checkScheduler():
    # TODO this is all too harcoded, refactor
    # TODO This doesn't work with the telegram.ext scheduler, since it blocks
    # send Traffic at 8:00
    if timeInRange(
            datetime.time(7, 59, 55), datetime.time(7, 59, 57),
            datetime.datetime.now().time()):
        result = p.parseInput('verkehr kita')
        updater.bot.sendMessage(config.get(
            'main', 'TELEGRAM_BOT_TOKEN'), result['reply'])

    if timeInRange(
        # TODO fix the hardcoded message for the sbahn notification (is it too late?)
            datetime.time(17, 15, 55), datetime.time(17, 15, 57),
            datetime.datetime.now().time()):
        result = p.parseInput('sbahn')
        updater.bot.sendMessage(config.get(
            'main', 'TELEGRAM_BOT_TOKEN'), result['reply'])
