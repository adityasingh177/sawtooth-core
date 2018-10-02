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

import subprocess
import logging
import datetime

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

class Workload:
    def start_intkey(self,channel):
        LOGGER.info('Starting Intkey Transaction processor')
        cmd = "sudo -u sawtooth intkey-tp-python -C tcp://127.0.0.1:4004 -v"
        channel.exec_command(cmd)
        channel.send('aditya9971\n')
        
    def do_workload(self, channel):
        LOGGER.info('Starting Intkey Workload')
    
    def stop_workload(self, ssh_client):
        LOGGER.info('Stopping Intkey Workload')
        cmd = "ps aux | grep 'intkey' | awk '{print $2}'"
        stdin,stdout,stderr = ssh_client.exec_command(cmd)
        output = stdout.readlines()
        pids = [i.strip('\n') for i in output]
        print(pids[0])