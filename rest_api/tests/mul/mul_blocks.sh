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

intkey_service="sawtooth-intkey-tp-python.service"
validator_service="sawtooth-validator.service"

echo "HOST is $HOST"
echo "Target is $TARGET"


block_count=$(sawtooth block list --url http://$HOST:8008 | wc -l)
target_count=$(($block_count+ $BLOCKS))

sudo intkey workload --url http://10.223.155.43:8008 --rate 1 -d 1 &


while true; do 
	block_count=$(sawtooth block list --url http://$HOST:8008 --limit 1)
	echo $block_count
	echo $target_count
	if [ $block_count -gt  $target_count ]; then
		break
	fi
done

pid=ps -ef | grep workload | awk 'NR==2{print $2}'
sudo kill -9 $pid
