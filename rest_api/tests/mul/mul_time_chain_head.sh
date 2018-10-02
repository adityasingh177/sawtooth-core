#!/bin/bash 

HOST='192.168.1.21'
TIME=10
USERNAME="ubuntu"
PASSWORD="Bc124816"
PORT="60240"
TARGET='192.168.1.25'
RATE='1'
DISPLAY_FREQUENCY='1'
COUNT=0
EXCLUDE='192.168.1.21,192.168.1.22'

intkey_service="sawtooth-intkey-tp-python.service"
validator_service="sawtooth-validator.service"

echo "HOST is $HOST"


Iparray=$(nmap -sL -n 192.168.1.21-30 --exclude $EXCLUDE | grep 'Nmap scan report for' | cut -f 5 -d ' ')

echo "Target Nodes are $Iparray"

read -a arr <<< $Iparray

echo "Checking Validator connectivity...."

for i in "${arr[@]}"
do
   echo $(sshpass -p $PASSWORD ssh -p $PORT -tt -o StrictHostKeyChecking=no $USERNAME@$i "systemctl is-active sawtooth-validator.service")
done
echo

echo
echo "        NODE | CHAIN_HEAD"

for i in "${arr[@]}"
do
   echo "$i |$(sawtooth block list --url http://$i:8008 --limit 1 | awk 'NR==2{print $2}')"
done
echo

for node in "${arr[@]}"
do
	tput setaf 3
	echo "Target is $node......"
	echo "Stopping Validator service for Target $node......"
	echo "Executing SSH to target $node!!!!!"
	tput sgr0
	echo
	echo "Waiting for Services to Stop!!!!"
	echo
	
	while true ; do
		sshpass -p $PASSWORD ssh -p $PORT -tt -o StrictHostKeyChecking=no $USERNAME@$node "echo $PASSWORD | sudo -S systemctl stop sawtooth-validator.service"
		
		if [ $? -eq 0 ]
		then
		    tput setaf 3 
		    echo -e "[ok]$validator_service has Stopped!!!!!!" 
		    tput sgr0
		    break
		fi
	done
	
	echo
	tput setaf 3
	echo "Starting Workload at $HOST for $TIME seconds...."
	echo "Starting Workload at $RATE trns/sec....."
	tput sgr0
	cmd="timeout $TIME intkey workload --url http://$HOST:8008 --rate $RATE"
	$cmd
	echo
	tput setaf 1
	echo "Workload Stopped after $TIME seconds....."
	tput sgr0
	
	
	tput setaf 3
	echo "Starting Validator Service For Target $node........."
	echo "Executing SSH to target $node!!!!!"
	tput sgr0
	echo
	echo "Waiting for Services to Start!!!!"
	echo
	
	while true ; do
		sshpass -p $PASSWORD ssh -p $PORT -tt -o StrictHostKeyChecking=no $USERNAME@$node "echo $PASSWORD | sudo -S systemctl start sawtooth-validator.service"
		if [ $? -eq 0 ] 
		then
		    tput setaf 1 
		    echo -e "[ok]$validator_service has Started!!!!!!" 
		    tput sgr0
		    break
		fi
	done
	
	SECONDS=0
	echo
	echo "Calculating block list for $node"
	echo "Calculating SYNC TIME for $node"
	
	
	while true ; do
	    tput setaf 1
	    echo "BLOCK LIST"
	    tput sgr0
	    echo "TIME Elapsed : $SECONDS seconds..."
		echo "      NODE       | CHAIN_HEAD "
		
		for i in "${arr[@]}"
		do
		   echo "$i |$(sawtooth block list --url http://$i:8008 --limit 1 | awk 'NR==2{print $2}')"
		done
		echo
	    if [ $(sawtooth block list --url http://$TARGET:8008 --limit 1 | awk 'NR==2{print $2}') == $(sawtooth block list --url http://$HOST:8008 --limit 1 | awk 'NR==2{print $2}') ]; then
	        break
	    fi
	done
	
	tput setaf 2
	echo "SYNC TIME for $node is: $SECONDS seconds"
	echo
	echo
	tput sgr0
	echo "    NODE |  CHAIN_HEAD "

for node in "${arr[@]}"
	do 
	   echo "$node |$(sawtooth block list --url http://$node:8008 --limit 1 | awk 'NR==2{print $2}')"
	done
echo
done
echo 

