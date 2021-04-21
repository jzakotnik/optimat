#! /bin/bash
sleep 20
cd /home/pi/optimat
source env_optimat2/bin/activate
cd dashboard
python3 frontend.py
exit 0

