#!/bin/bash
echo yourscript.sh called: `date`

HOME = /home/pi/
PYTHONPATH = /usr/bin/python   

# script to run on startup on RPI server
# wait for internet connection before runnning
ROUTER_IP=192.168.1.1
while ( ! ping -c1 $ROUTER_IP) do
  echo "network is not up yet"
  sleep 3
done
echo "network is up now"

cd /home/pi/Jowosh-Discord-Bot/
git pull 
/usr/bin/python /home/pi/Jowosh-Discord-Bot/bot.py 