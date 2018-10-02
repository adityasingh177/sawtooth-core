#!/bin/bash 

HOST='10.223.155.43'
TIME=10
USERNAME="test"
PASSWORD="intel123"
PORT="22"
TARGET='10.223.155.69'
BLOCKS=10
RATE='1'
DISPLAY_FREQUENCY='1'
COUNT=0
EXCLUDE='192.168.1.22'

while true; do 
	block_count=$(sawtooth block list --url http://$HOST:8008 | wc -l)
	if [ $block_count -eq  $(($block_count+$BLOCKS)) ]; then 
	   pid=ps -ef | grep workload | awk 'NR==2{print $2}'
	   sudo kill -9 $pid
	fi
done