import json
import urllib
import requests
import logging
import smtplib

import time

from os import listdir
from os.path import isfile, join

import dateutil.parser
import email
import feedparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from lxml import html
import ntpath
import xml.etree.ElementTree as ET
import os
import subprocess
import fritzconnection as fc
import couchdb

#google APIs authentication
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
import datetime

from configparser import ConfigParser



class Parser:
    config = ConfigParser()
    config.read('config.ini')

    def getPhoneList(self):
        FRITZ_IP = self.config.get('main', 'FRITZ_IP')
        FRITZ_USER = self.config.get('main', 'FRITZ_USER')
        FRITZ_PASSWORD = self.config.get('main', 'FRITZ_PASSWORD')
        
        result = "Master, versuche die Anrufe zu ermitteln.."
        telitem = [
            'Kein Call', 'Kein Call', 'Kein Call', 'Kein Call', 'Kein Call'
        ]

        f = fc.FritzConnection(
            address=FRITZ_IP,
            user=FRITZ_USER,
            password=FRITZ_PASSWORD)
        fritz = f.call_action('X_AVM-DE_OnTel', 'GetCallList')
        print ("This is the URL for the callers, including session token for now: " + fritz["NewCallListURL"])
        xmlhandle = urllib.request.urlopen(fritz["NewCallListURL"])
        xmlresult = xmlhandle.read()
        xmlhandle.close()
        root = ET.fromstring(xmlresult)
        result = "Master, hier die verpassten Anrufe (letzte 5):\n"
        thisCall = ""
        maxResults = 4
        countedresults = 0
        for callerID in root.iter('Call'):
            if callerID.find("Type").text == '2':
                callDate = callerID.find("Date").text
                inPhoneBook = callerID.find("Name").text
                callerNumber = callerID.find("Caller").text
                thisCall = callDate + ":\n"
                if callerNumber is not None:
                    thisCall = thisCall + callerNumber
                if inPhoneBook is not None:
                    thisCall = thisCall + " (" + inPhoneBook + ")"
                thisCall = thisCall + "\n"
                telitem[countedresults] = thisCall
                result = result + thisCall
                countedresults = countedresults + 1
                #print countedresults
            if countedresults > maxResults:
                #print "break now"
                break
        return {'reply': result, 'tellist': telitem}

    def getCalendarEvents(self):
        GOOGLECALENDAR_ID = self.config.get('main', 'GOOGLECALENDAR_ID')
        
        result = "Master, hier die folgenden Meetings..\n"
        calitem = [
            'Kein Termin', 'Kein Termin', 'Kein Termin', 'Kein Termin',
            'Kein Termin'
        ]
        try:
            scopes = ['https://www.googleapis.com/auth/calendar']
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                'google-credentials.json', scopes)
            cal = build('calendar', 'v3', credentials=credentials)
            now = datetime.datetime.utcnow().isoformat(
            ) + 'Z'  # 'Z' indicates UTC time
            eventsResult = cal.events().list(
                calendarId=GOOGLECALENDAR_ID,
                timeMin=now,
                maxResults=5,
                singleEvents=True,
                orderBy='startTime').execute()
            calcounter = 0
            for i in eventsResult['items']:
                eventtime = i['start']
                resulttime = ''
                if 'dateTime' in eventtime:
                    resulttime = eventtime['dateTime']
                if 'date' in eventtime:
                    resulttime = eventtime['date']
                parsedTime = dateutil.parser.parse(
                    resulttime)  #reformat the time
                resulttime = parsedTime.strftime('%a, %d-%m, %H:%M')
                result = result + resulttime + '\n' + i['summary'] + '\n'
                calitem[calcounter] = resulttime + ': ' + i['summary']
                calcounter = calcounter + 1
            print ('Got everything together from calendar service, byebye')
            return {'reply': result, 'calendarlist': calitem}
        except:
            return {'reply': 'did not work', 'calendarlist': calitem}

    def getKitaTraffic(self):
        #check google maps for the traffic to kindergarten
        GOOGLE_API_KEY = self.config.get('main', 'GOOGLE_API_KEY')
        GOOGLETRAFFIC_SOURCE = self.config.get('main', 'GOOGLETRAFFIC_SOURCE')
        GOOGLETRAFFIC_DESTINATION = self.config.get('main', 'GOOGLETRAFFIC_DESTINATION')
        data_to = json.load(
            urllib.request.urlopen(
                'https://maps.googleapis.com/maps/api/distancematrix/json?origins='+GOOGLETRAFFIC_SOURCE+'&destinations='+GOOGLETRAFFIC_DESTINATION+'&departure_time=now&mode=driving&language=de-DE&key='
                + GOOGLE_API_KEY))
        data_back = json.load(
            urllib.request.urlopen(
                'https://maps.googleapis.com/maps/api/distancematrix/json?origins='+GOOGLETRAFFIC_DESTINATION+'&destinations='+GOOGLETRAFFIC_SOURCE+'&departure_time=now&mode=driving&language=de-DE&key='
                + GOOGLE_API_KEY))
        resultstring = "Master, hier aktueller Verkehr zur Kita: " + data_to['rows'][0]['elements'][0]['duration_in_traffic']['text'] + ", Rueckweg: " + data_back['rows'][0]['elements'][0]['duration_in_traffic']['text']
        
        return {
            'reply':
            resultstring,
            'toDuration':
            data_to['rows'][0]['elements'][0]['duration_in_traffic']['value']
        }

    def getFuelPrice(self):
        #check fuel price in my neighbourhood
        TANKEN_APIKEY = self.config.get('main', 'TANKEN_APIKEY')
        TANKEN_LOCATION = self.config.get('main', 'TANKEN_LOCATION')
        fuelprice = json.load(
            urllib.request.urlopen(
                'https://creativecommons.tankerkoenig.de/json/prices.php?ids='+TANKEN_LOCATION+'&apikey='
                + TANKEN_APIKEY))
        resultstring = ''
        try:
            resultstring = "Master, hier der Tankpreis E10 bei Aral: " + str(
                fuelprice['prices'][TANKEN_LOCATION]
                ['e10'])
            return {
                'reply':
                str(resultstring),
                'fuelPrice':
                str(fuelprice['prices'][TANKEN_LOCATION]
                    ['e10'])
            }
        except Exception:
            return {'reply': 'Fuel station is closed', 'fuelPrice': 'N/A'}


    def startAlarm(self):
        # this starts motion detection for a connected webcam
        #clean up alarmimages
        subprocess.call('rm -rf /home/pi/optimat/alarmimages/*', shell=True)
        #start daemon
        #maybe this?  on_event_end /home/guillo/bin/motion_encode_and_delete_jpgs gap 10
        subprocess.call('nohup sudo motion -p pid.txt', shell=True)
        self.config.set("main", "ALARM_IS_ON", "1")
        result = "Alarm wurde aktiviert.."
        return {'reply': result}

    def stopAlarm(self):
        pid = '0'
        with open('pid.txt', 'r') as f:
            pid = f.read().replace('\n', '')
        f.close()
        print ('Killing process motion with pid: ' + pid)
        subprocess.call('sudo kill ' + pid, shell=True)
        self.config.set("main", "ALARM_IS_ON", "0")
        result = "Alarm wurde de-aktiviert.."
        return {'reply': result}

    def startEnergy(self):
        #TODO change this to FritzDECT, deleted code for old switches
        result = "Strom ist an.. (Lichter? Buegeleisen? Wasserkocher?)"
        return {'reply': result}

    def stopEnergy(self):
        #TODO change this to FritzDECT, deleted code for old switches
        result = "Strom ist aus.. (Lichter? Buegeleisen? Wasserkocher?)"
        return {'reply': result}

    def sendAlarm(self):
        #TODO delete this?
        resultstring = "Master, das Video wurde per eMail verschickt..."
        
        return {'reply': resultstring}

    def listFilesNAS(self, path):
        #TODO, this does not work yet, because the list call returns different format/values depending on number of files
        #result = 'Your files in ' + path + ' are:\n'
        #filestation = FileStation(config.NAS_IP, config.NAS_USER, config.NAS_PASSWORD)
        #resultdict = filestation.list('/' + path, limit=0)
        ##resultdict = filestation.list('/' + path, limit=0)['files'] #e.g. ourdata
        #print resultdict
        #for key in resultdict:
        #    print key['path']
        #    result = result + key['path'] + '\n'
        return {'reply': 'todo'}

    def downloadFilesNAS(self, myfile, method='download'):
        NAS_IP = self.config.get('main', 'NAS_IP')
        NAS_USER = self.config.get('main', 'NAS_USER')
        NAS_PASSWORD = self.config.get('main', 'NAS_PASSWORD')
        NAS_BASEFOLDER = self.config.get('main', 'NAS_BASEFOLDER')
        authString = json.load(
            urllib.request.urlopen(
                'http://' + NAS_IP +
                ':5000/webapi/auth.cgi?api=SYNO.API.Auth&version=6&method=login&account='
                + NAS_USER + '&passwd=' + NAS_PASSWORD +
                '&session=FileStation&format=sid'))
        sidToken = authString['data']['sid']
        downloadedFile = urllib.urlretrieve(
            'http://' + NAS_IP +
            ':5000/webapi/entry.cgi?api=SYNO.FileStation.Download&version=2&method=download&path='+NAS_BASEFOLDER+
            + myfile + '&mode=download&_sid=' + sidToken,
            'filecache/' + ntpath.basename(myfile))
        #extract file from whole path
        newpath = 'filecache/' + ntpath.basename(myfile)
        return newpath

    def sendFileViaEmail(self, myfile):
        newpath = self.downloadFilesNAS(
            myfile)  #returns the location of the file locally
        mail_user = self.config.get('main', 'MAIL_SENDER')
        mail_pwd = self.config.get('main', 'MAIL_PASSWORD')
        mail_to = self.config.get('main', 'MAIL_RECIPIENT')
        MAIL_SERVER = self.config.get('main', 'MAIL_SERVER')
        msg = MIMEMultipart()

        msg['From'] = mail_user
        msg['To'] = mail_to
        msg['Subject'] = 'Mail from Optimat for you..'

        msg.attach(MIMEText("Hello Master! Hier das File.."))

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(newpath, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="%s"' % os.path.basename(myfile))
        msg.attach(part)

        mailServer = smtplib.SMTP(MAIL_SERVER, 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(mail_user, mail_pwd)
        mailServer.sendmail(mail_user, mail_to, msg.as_string())
        # Should be mailServer.quit(), but that crashes...
        mailServer.close()
        return

    def getSBahnTraffic(self):
        result = "Master, versuche die Verbindungen zu suchen.."
        #result.encode('utf-8')
        #TODO this is harcoded to Frankfurt West
        page = requests.get(
            'http://reiseauskunft.bahn.de/bin/bhftafel.exe/dn?ld=15079&rt=1&input=Frankfurt(Main)West%238002042&boardType=dep&time=actual&productsFilter=00001&REQTrain_name=4&start=yes&'
        )
        tree = html.fromstring(page.content)
        result = "Master, das sind die naechsten Verbindungen der S4 ab Westbahnhof:\n"
        #TODO when this is available as DB OpenData, change to API
        #TODO something is wrong with the encoding here
        for x in range(0, 5):
            traintime = tree.xpath(
                '//*[@id="journeyRow_' + str(x) + '"]/td[1]/text()')
            delay = tree.xpath(
                '//*[@id="journeyRow_' + str(x) + '"]/td[6]//span/text()')
            traintimestring = ''.join(traintime).encode('utf-8')
            delaytimestring = ''.join(delay).encode('utf-8')
            result = result + "Zug um: " + str(traintimestring) + " mit " + str(delaytimestring) + "\n"
        return {'reply': result}

    def getBitcoinBalance(self):
        result = "Master, hier Ihr Kontostand in Bitcoin. Sie sind sehr reich. Nicht.\n"
        result.encode('utf-8')
        BLOCKIO_APIKEY = self.config.get('main', 'BLOCKIO_APIKEY')
        balance = json.load(
            urllib.request.urlopen('https://block.io/api/v2/get_balance/?api_key=' +
                            BLOCKIO_APIKEY))
        result = result + balance['data']['available_balance'] + ', unconfirmed: ' + balance['data']['pending_received_balance']
        return {'reply': result}

    def transferBitcoins(self, request):
        BLOCKIO_APIKEY = self.config.get('main', 'BLOCKIO_APIKEY')
        BLOCKIO_TARGETWALLET = self.config.get('main', 'BLOCKIO_TARGETWALLET')
        BLOCKIO_PIN = self.config.get('main', 'BLOCKIO_PIN')
        
        tokens = request.split(' ')
        amount = str(tokens[1])
        target = BLOCKIO_TARGETWALLET  #hardcoded for now
        transaction_result = json.load(
            urllib.request.urlopen(
                'https://block.io/api/v2/withdraw/?api_key=' +
                BLOCKIO_APIKEY + '&amounts=' + amount +
                '&to_addresses=' + target + '&pin=' + BLOCKIO_PIN))
        result = 'Master, ich habe ' + amount + ' bitcoins an Ihr Konto ueberwiesen'
        return {'reply': result}

    def checkStatus(self, inputstatus):
        # this saves the current wellbeing psycho status.
        # TODO do a proper chatbot here, not if/then
        result = {
            'reply': 'Wie geht es Dir heute?',
            'keyboard': [['Gut', 'Schlecht'], ['Ganz OK', 'Superb']]
        }
        if inputstatus in ['gut', 'schlecht', 'ganz ok', 'superb']:
            result = {
                'reply': 'Warum?',
                'keyboard': [['Arbeit', 'Beziehung'],
                             ['Familie', 'Gesundheit']]
            }
        if inputstatus in ['arbeit']:
            result = {
                'reply': 'Warum?',
                'keyboard': [['Chef', 'Kollegen'], ['Kunde', 'Inhalt']]
            }
        if inputstatus in ['beziehung']:
            result = {
                'reply': 'Warum?',
                'keyboard': [['Erlebnis', 'Event'], ['Streit', 'Partner']]
            }
        if inputstatus in ['familie']:
            result = {
                'reply':
                'Warum?',
                'keyboard': [['Kinder', 'Verwandschaft'],
                             ['Eltern', 'Schwiegereltern']]
            }
        if inputstatus in ['gesundheit']:
            result = {
                'reply': 'Warum?',
                'keyboard': [['Schlapp', 'Fieber'],
                             ['Arztbesuch', 'Uebelkeit']]
            }
        return result

    def saveStatus(self, inputstatus):
        #this saves the current psycho status to a local couchdb
        COUCHDB_SERVER = self.config.get('main', 'COUCHDB_SERVER')
        
        server = couchdb.Server(
            url='http://' + COUCHDB_SERVER + ':5984/')
        db = server['feely']
        db.save({'status': inputstatus, 'timestamp': time.time()})
        return {'reply': 'Danke, viel Erfolg heute noch'}

    def checkWeather(self):
        OPENWEATHER_APIKEY = self.config.get('main', 'OPENWEATHER_APIKEY')
        OPENWEATHER_LOCATIONID = self.config.get('main', 'OPENWEATHER_LOCATIONID')
        temperature = json.load(
            urllib.request.urlopen(
                'http://api.openweathermap.org/data/2.5/weather?id='+OPENWEATHER_LOCATIONID+'&APPID='
                + OPENWEATHER_APIKEY + '&units=metric'))
        t = temperature['main']['temp']
        resultstring = 'Master, Temperatur ist bei ' + str(
            t) + ' Grad Celsius'
        return {'reply': resultstring, 'onlyTemp': str(t)}

    def checkWeatherForecast(self):
        #TODO this doesn't work on the chatbot yet, only dashboard?
        OPENWEATHER_APIKEY = self.config.get('main', 'OPENWEATHER_APIKEY')
        OPENWEATHER_LOCATIONID = self.config.get('main', 'OPENWEATHER_LOCATIONID')
        
        completeforecast = json.load(
            urllib.request.urlopen(
                'http://api.openweathermap.org/data/2.5/forecast?id='+OPENWEATHER_LOCATIONID+'&APPID='
                + OPENWEATHER_APIKEY + '&units=metric'))
        #print 'Forecast: ' + json.dumps(completeforecast)
        forecast = []
        for n in range(0, 7):
            #print 'getting time..' + str(completeforecast['list'][n]['dt'])
            time = datetime.datetime.fromtimestamp(
                completeforecast['list'][n]['dt'])
            temperature = completeforecast['list'][n]['main']['temp']
            #print 'getting icon....' + str(completeforecast['list'][n])
            icon = 'http://openweathermap.org/img/w/' + completeforecast['list'][n]['weather'][0]['icon'] + '.png'
            #print 'Got time ' + str(time) + ' and forecast ' + str(temperature) + ' and icon  ' + str(icon)
            forecast.append((time.strftime('%H:%M'), str(int(temperature)),
                             str(icon)))
        resultstring = 'Master, Temperatur in Koenigstein ist bei Grad Celsius'
        return {'reply': resultstring, 'onlyForecast': forecast}

    def checkNews(self):
        logging.info('Check news started...')

        f = feedparser.parse(
            'http://www.spiegel.de/schlagzeilen/tops/index.rss')
        logging.info('Executed rss feed parse')
        #collect headlines
        newsitem = [
            'No headlines right now..', 'No headlines right now..',
            'No headlines right now..', 'No headlines right now..',
            'No headlines right now..'
        ]
        logging.info('Iterating over news')
        for n in range(0, 5):
            logging.info('This is the news' + f.entries[n]['title'])
            newsitem[n] = f.entries[n]['title']
        resultstring = 'Master, hier sind die aktuellen News von Spiegel Online:\n' + '\n'.join(
            newsitem)
        logging.info(
            'Executed rss feed parse ,this is the result' + resultstring)
        return {'reply': resultstring, 'newslist': newsitem}

    def saveTopic(self, inputmessage):
        try:
            logging.info("Setting a new topic")
        except Exception:
            logging.exception("Save Topic went wrong")

    def updateDashboard(self, displayFuel=False):
        try:
            print ("Update the dashboard..")
            #initial data before the API call
            dashdata = {
                'traffic': '16m',
                'fuel': '1.45',
                'temperature': '18 C',
                'miner': '50 C'
            }
            dashdata['tel'] = [
                'Telefon A', 'Telefon B', 'Telefon C', 'Telefon D', 'Telefon E'
            ]
            dashdata['news'] = ['News1', 'News2', 'News C', 'News D', 'News E']
            dashdata['calendar'] = [
                'Cal 1', 'Cal 2', 'Cal C', 'Cal  D', 'Cal E'
            ]
            dashdata['forecast'] = [('t', '12', 'ico')]
            dashdata['miner'] = '0'
            dashdata['reward'] = '0'
            
            #retrieved real data starts here:
            traffic = self.getKitaTraffic()
            dashdata['traffic'] = str(traffic['toDuration'] / 60) + 'min'

            weather = self.checkWeather()
            dashdata['temperature'] = str(
                int(round(float(weather['onlyTemp'])))) + ' C'

            forecast = self.checkWeatherForecast()
            dashdata['forecast'] = forecast['onlyForecast']

            news = self.checkNews(
            )['newslist']  # news = list of news items from Spiegel online feed
            dashdata['news'] = news

            tel = self.getPhoneList()['tellist']
            dashdata['tel'] = tel

            cal = self.getCalendarEvents()
            dashdata['calendar'] = cal['calendarlist']
            
            fuel = self.getFuelPrice()
            dashdata['fuel'] = str(fuel['fuelPrice']) + 'EUR'

            #TODO this could be routed to any dashboard, not only the local one
            print (requests.post(
                'http://localhost:5000/dashboard', json=dashdata))

            
        except Exception:
            print ('Ohoh, something went wrong when updating the dashboard...')

    def parseInput(self, request):
        #default reply if none of the keywords was used
        result = {'reply': "Master, ich weiss nicht was Du meinst!"}
        logging.info("Got request: " + str(request))
        
        #is it a file to be emailed from my NAS
        if str.lower(request).find("send") >= 0:
            print ("file detected...")
            myfile = request[5:]
            self.sendFileViaEmail(myfile)
            result = "eMail wurde verschickt, viel Spass damit!"

        #is it a directory to be listed?
        if request.find("list") >= 0:
            path = request[5:]
            result = self.listFilesNAS(path)

        #file operations require case sensitivity, therefore insensitivity to the command comes here:
        request = str.lower(request)

        #is it some traffic information?
        if request == ("verkehr kita"):
            result = self.getKitaTraffic()

        #calendar?
        if request == ("kalender"):
            result = self.getCalendarEvents()

        #is it the delay of the SBahn information?
        if request == ("sbahn"):
            result = self.getSBahnTraffic()

        #do we want last callers from fritz box?
        if request == ("telefon"):
            result = self.getPhoneList()

        #Current fuel price
        if request == ("tanken"):
            result = self.getFuelPrice()

        #someone in the house? video alarm
        if request == ("alarm"):
            result = self.sendAlarm()

        #starting webcam
        if request == ("alarm on"):
            result = self.startAlarm()

        #stopping webcam
        if request == ("alarm off"):
            result = self.stopAlarm()

        #starting lights
        if request == ("strom an"):
            result = self.startEnergy()

        #stopping lights
        if request == ("strom aus"):
            result = self.stopEnergy()

        #get bitcon wallet status
        if request == ("konto"):
            result = self.getBitcoinBalance()

        #send bitcon tos
        if 'transfer' in request:
            result = self.transferBitcoins(request)

        #how are you doing
        if request == ("status"):
            result = self.checkStatus('status')
            #how are you doing
        #wetter
        if request == ("wetter"):
            result = self.checkWeather()
        #spiegel online news
        if request == ("news"):
            result = self.checkNews()

        #send a message to the dashboard
        if request.find("thema") >= 0:
            inputmessage = request[6:]
            result = self.saveTopic(inputmessage)

        #save status, TODO make this configurable
        if request in [
                'gut', 'schlecht', 'ganz ok', 'superb', 'arbeit', 'chef',
                'kollegen', 'kunde', 'inhalt', 'beziehung', 'erlebnis',
                'event', 'streit', 'partner', 'familie', 'kinder',
                'verwandschaft', 'eltern', 'schwiegereltern', 'gesundheit',
                'schlapp', 'fieber', 'arztbesuch', 'uebelkeit'
        ]:
            self.saveStatus(request)
            result = self.checkStatus(request)
        return result
