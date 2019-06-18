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

This works via two components, one server that polls Telegram, parses the commands and emits the respective replies. Moreover there is another webserver (dashboard), which the first server updates every 5 minutes with all the data via POST. A browser (e.g. a Chrome in the kitchen raspberry) can access this dashboard webserver.

![Dashboard example](doc/sample_dashboard.jpg?raw=true "Dashboard example")

# Installation

## Basic install for the Telegram bot
This installation guide describes how to install the software from scratch. Follow these steps:
* Start from empty raspberry image Raspbian Stretch 4.14 (April 2019), burn the image to a SD card with the respective tool
* Enable ssh access which is disabled by default on the raspberry
* Update the operating system via `sudo apt-get update` and `sudo apt-get dist-upgrade` 
* Install a number of libraries which are needed for the telegram bot: `sudo apt-get install build-essential libssl-dev libffi-dev python-dev libxml2-dev libxslt-dev python-dev` 
* Create an ssh key and add it to github, so you can pull the code: `ssh-keygen -t rsa -C "yourname@yourdomain.com"` then copy the RSA key on the home .ssh folder to github
* Clone the respository: `git clone git@github.com:jzakotnik/optimat.git`
* To manage the python libraries, install virtualenv with `sudo pip3 install virtualenv`
* In the optimat folder (created by git cline), create a new python environment with `virtualenv env_optimat`
* Activate the new environment with `source env_optimat/bin/activate`
* Install all depending libraries with `pip3 install -r requirements.txt`
* Setup config file by using the sample `config.ini.sample` and copying it `cp config.ini.sample config.ini`
* Copy `google-credentials.json` if you need the calendar function
* Try running the bot using `python3 run.py`
* Go to telegram and send "verkehr kita", it should return the respective time

![Telegram chat example](doc/sample_chat.jpg?raw=true "Telegram chat example")

## Install autostart
* copy startOptimat and startDashboard shell scripts

## Enable camera
* Enable camera module
* sudo apt-get install motion -y
* Copy motion.conf to /etc/motion/motion.conf

