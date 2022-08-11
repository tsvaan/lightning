#!/bin/bash
# This script runs the ld250 data collection programm
cd /home/boltek/boltek
START=`date`
echo "Скрипт запущен " $START > log.txt
echo "Скрипт запущен " $START | mail -s "Письмо от LD-250" user@mail.ru
# xfce4-terminal -e "screen -S ld python LD250.py"
screen -S ld python LD250.py
EN=`date`
echo "Скрипт остановлен" $EN >> log.txt
echo "Скрипт остановлен " $EN | mail -s "Письмо от LD-250" user@mail.ru
