import paramiko
import sys

nbytes = 4096
hostname = '10.223.155.130'
port = 22
username = 'shourya' 
password = 'shourya123'
command = 'ps aux | grep sawtooth'

try:
    ssh=paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname,port,username,password)
except paramiko.AuthenticationException:
    print("Failed to connect to {} due to wrong username/password").format(hostname)
    exit(1)
except:
    print("Failed to connect to {}").format(hostname)
    exit(2)
        
command2 = 'sudo systemctl status sawtooth-rest-api.service'
stdin,stdout,stderr=ssh.exec_command(command)
outlines=stdout.readlines()
resp=''.join(outlines)
print(resp)