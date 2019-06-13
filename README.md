# Optimat - the actually useful chatbot and kitchen dashboard
A simple Telegran chatbot and dashboard for everyday tasks. It consumes private APIs (e.g. Fritz Box, Synology NAS) as well as public APIs (e.g. google) and Screenscraping (e.g. train delays). It is best run on a raspberry Pi and doesn't need incoming network connections (yeah!).

*This project is totally work in progress - I wanted to know if a chatbot and the related kitchen dashboard make sense and after some years I see that they to. So I'll work here to refactor the platform.*

Currently it does
* Sending files from a local Synology NAS
* Listing files from a local Synology NAS
* Current traffic from home to the Kindergarten
* The next calendar events from the family calendar
* The current delay of the train
* The last missed calls on landline (via Fritz Box)
* The current fuel price around the corner
* Motion detection if a webcam is connected to the raspi (turn on/off)
* Switch power sockets (e.g. for iron or similar)
* Send amount of bitcoins in online wallet and transfer to others
* Tracking "how was your day" - psycho tracker
* Local weather
* Retrieving news from Spiegel Online Feed


![Dashboard example](doc/sample_dashboard.jpg?raw=true "Dashboard example")

# Installation

## Basic install for the Telegram bot
* Start from empty raspberry image Raspbian Stretch 4.14 (April 2019)
* Burn image
* Enable ssh access
* sudo apt-get update
* sudo apt-get dist-upgrade
* sudo apt-get install libffi-dev
* sudo apt-get install build-essential libssl-dev libffi-dev python-dev
* sudo apt-get install libxml2-dev libxslt-dev python-dev
* ssh key gen add to github: ssh-keygen -t rsa -C "yourname@yourdomain.com"
* git clone git@github.com:jzakotnik/optimat.git
* sudo pip3 install virtualenv
* virtualenv env_optimat
* source env_optimat/bin/activate
* Install python and virtualenv
* Install requirements.txt
* Setup config file
* Copy google-credentials.json if you need the calendar function
* python3 run.py
* Go to telegram and send "verkehr kita"

![Telegram chat example](doc/sample_chat.jpg?raw=true "Telegram chat example")

## Install autostart
* copy startOptimat and startDashboard shell scripts


