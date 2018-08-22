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

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

class Workload():
    def do_workload(self):
        LOGGER.info('Starting Intkey Workload')
#         cmd = "intkey workload --url 10.223.155.43:8008 --rate 1 -d 1"
#         subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    
    def stop_workload(self):
        pass