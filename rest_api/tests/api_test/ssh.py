# Copyright 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

import paramiko
import logging
import datetime

import os, re, threading
from workload import Workload

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

    
class SSH():
    def do_ssh(self,hostname,port,username,password):
        try:
            sshClient = paramiko.SSHClient()
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.load_system_host_keys()
            sshClient.connect(hostname,port,username,password)
            transport=sshClient.get_transport()
        except paramiko.AuthenticationException:
            LOGGER.info("Failed to connect to {} due to wrong username/password".format(hostname))
            exit(1)
        except:
            LOGGER.info("Failed to connect to {}".format(hostname))
            exit(2)
        
        chan = sshClient.invoke_shell()
        chan = sshClient.get_transport().open_session()
        chan.get_pty()
        workload = Workload()
        workload.do_workload()
        
        endTime = datetime.datetime.now() + datetime.timedelta(seconds=1)
            
        while True:
          if datetime.datetime.now() >= endTime:
            break
          
        chan.exec_command("sudo kill -9  $(ps aux | grep 'intkey' | awk '{print $2}')")
        print(chan.recv(4096))
        chan.send('aditya9971\n')          
        sshClient.close()
    
    def stop_validator(self, node):
        LOGGER.info("stopping validator service for %s",node)
        
    def start_validator(self, node):
        LOGGER.info("starting validator service for %s",node)
    
    def close_session(self):
        LOGGER.info("closing connection")
        