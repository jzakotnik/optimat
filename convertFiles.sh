#!/bin/bash

#depending on the raspberry, change this to the right folder
cd /home/pi/optimat/alarmimages
echo "executing conversion script..."
rm -rf *.mp4
for file in *.avi
do
  extension='.mp4'
  result=$file
  avconv -i $file -c:v libx264 -c:a copy $result$extension >> conversion_results.txt
done
#now execute the python script to send this to my email..
cd /home/pi/optimat
source env_optimat/bin/activate
python3 sendNotificationEmail.py >> conversion_results.txt
cd alarmimages
rm -rf *.mp4 *.avi
cd ..

