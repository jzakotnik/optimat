#! /bin/bash
sleep 20
cd /home/pi/optimat
source optimat_pythonenv/bin/activate
cd dashboard
python3 frontend.py
exit 0

