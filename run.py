
from telegram.ext import MessageHandler, Filters, Updater

import parser
import time
import datetime
import os
import logging
from configparser import ConfigParser

logging.basicConfig(filename='optimat.log', level=logging.INFO)
config = ConfigParser()
config.read('config.ini')


updater = Updater(token=config.get('main', 'TELEGRAM_BOT_TOKEN'))
dispatcher = updater.dispatcher
p = parser.Parser()


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


logging.info('Listening...')
secondCounter = 295  # when starting, trigger update dashboard after 5sec
logging.info('Optimat started...')

while 1:
    time.sleep(1)
    checkScheduler()  # if there are any scheduled bot messages, trigger them here
    secondCounter += 1
if (secondCounter >= 300):
    try:
        p.updateDashboard()  # this pushed all the data to a dashboard server every 5min
    except Exception:
        logging.info('Could not updated dashboard')
    secondCounter = 0
