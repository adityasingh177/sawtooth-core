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
# ------------------------------------------------------------------------
import paramiko
import logging


logging.getLogger("paramiko").setLevel(logging.DEBUG)

class SSH_CLIENT:   
    def __init__(self):
        self.sshClient = paramiko.SSHClient()
         
    def do_ssh(self,hostname,port,username,password):        
        try:
            self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.sshClient.load_system_host_keys()
            self.sshClient.connect(hostname,port,username,password)
        except paramiko.AuthenticationException:
            logging.info("Failed to connect to {} due to wrong username/password".format(hostname))
            exit(1)
        except:
            logging.info("Failed to connect to {}".format(hostname))
            exit(2)

        return True
        
    def get_channel(self):
        channel = self.sshClient.invoke_shell()
        channel = self.sshClient.get_transport().open_session()
        channel.get_pty()
        return channel
        
    def stop_validator(self, node):
        logging.info("stopping validator service for %s",node)
        
    def start_validator(self, node):
        logging.info("starting validator service for %s",node)
    
    def close_session(self,node):
        logging.info("closing connection for %s",node)
        self.sshClient.close()