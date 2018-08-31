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
    def start_intkey(self):
        LOGGER.info('Starting Intkey Transaction processor')
        cmd = "sudo -u sawtooth intkey-tp-python -C tcp://127.0.0.1:4004 -v"
        subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        
    def do_workload(self):
        LOGGER.info('Starting Intkey Workload')
        cmd = "intkey workload --url http://10.223.155.43:8008 --rate 1 -d 1"
        subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    
    def stop_workload(self, channel, wait):
        endTime = datetime.datetime.now() + datetime.timedelta(seconds=wait)
            
        while True:
          if datetime.datetime.now() >= endTime:
            break
        
        LOGGER.info('Stopping Intkey Workload')
        channel.exec_command("sudo kill -2  $(ps aux | grep 'intkey' | awk '{print $2}')")
        channel.send('aditya9971\n') 