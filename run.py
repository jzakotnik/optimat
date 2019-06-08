import telepot
import parser
import time
import datetime
import optimatconfig as config
import os
import logging

p = parser.Parser()
bot = telepot.Bot(config.TELEGRAM_BOT_TOKEN)
logging.basicConfig(filename='optimat.log', level=logging.DEBUG)


def timeInRange(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


def handle(msg):
    inputmessage = msg['text'].encode('ascii')
    result = p.parseInput(inputmessage)
    if 'keyboard' in result.keys():  # custom reply keyboard specified, this is for the psycho tracker
        show_keyboard = {'keyboard': result['keyboard']}
        bot.sendMessage(
            config.MY_TELEGRAM_ID, result['reply'],
            reply_markup=show_keyboard)  # send whatever
    else:
        bot.sendMessage(config.MY_TELEGRAM_ID,
                        result['reply'])  # send whatever


def checkScheduler():
    # TODO this is all too harcoded, refactor
    # send Traffic at 8:00
    if timeInRange(
            datetime.time(7, 59, 55), datetime.time(7, 59, 57),
            datetime.datetime.now().time()):
        result = p.parseInput('verkehr kita')
        print(bot.sendMessage(config.MY_TELEGRAM_ID,
                              result['reply']))  # send verkehr

    if timeInRange(
        # TODO fix the hardcoded message for the sbahn notification (is it too late?)
            datetime.time(17, 15, 55), datetime.time(17, 15, 57),
            datetime.datetime.now().time()):
        result = p.parseInput('sbahn')
        print(bot.sendMessage(config.MY_TELEGRAM_ID,
                              result['reply']))  # send sbahn


print(bot.getMe())
bot.notifyOnMessage(handle)
logging.info('Listening...')
secondCounter = 295  # when starting, trigger update dashboard after 5sec
logging.info('Optimat started...')

while 1:
    time.sleep(1)
    checkScheduler()  # if there are any scheduled bot messages, trigger them here
    secondCounter += 1
    if (secondCounter >= 300):
        p.updateDashboard()  # this pushed all the data to a dashboard server every 5min
        secondCounter = 0
