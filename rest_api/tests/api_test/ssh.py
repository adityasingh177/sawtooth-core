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


class SSH():
    def do_ssh(self,hostname,port,username,password):
        try:
            ssh=paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname,port,username,password)
        except paramiko.AuthenticationException:
            print("Failed to connect to {} due to wrong username/password".format(hostname))
            exit(1)
        except:
            print("Failed to connect to {}".format(hostname))
            exit(2)
                
        command = 'ps aux | grep sawtooth'
        stdin,stdout,stderr=ssh.exec_command(command)
        outlines=stdout.readlines()
        resp=''.join(outlines)
        ssh.close()