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
import queue
import threading
import os
import logging


from workload import Workload
from ssh import SSH
from utils import _get_node_chains

logging.basicConfig(level=logging.INFO,
                    format='(%(threadName)-10s) %(message)s',
                    )


def wait_for_event(e):
    """Wait for the event to be set before doing anything"""
    logging.debug('wait_for_event starting')
    event_is_set = e.wait()
    logging.debug('event set: %s', event_is_set)

def wait_for_event_timeout(e, t):
    """Wait t seconds and then timeout"""
    while not e.isSet():
        logging.debug('wait_for_event_timeout starting')
        event_is_set = e.wait(t)
        logging.debug('event set: %s', event_is_set)
        if event_is_set:
            logging.debug('processing event')
        else:
            logging.debug('doing other work')


class Workload_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.shutdown_flag = threading.Event()
        
    def run(self):
        logging.info('Starting Workload')
        workload = Workload()
        while not self.shutdown_flag.is_set():
            workload.do_workload()
        return
    
    def stop(self):
        pass

class SSH_thread(threading.Thread):
    def __init__(self, hostname, port, username, password):
      threading.Thread.__init__(self)
      self.hostname = hostname
      self.port = port
      self.username = username
      self.password = password
      
    def run(self):
        logging.info('starting ssh thread')
        logging.info('Logging into Validation Network')
        self.ssh()
        logging.info('Exiting ssh thread')
        return
    
    def ssh(self):
        logging.info('creating ssh object')
        ssh = SSH()
        logging.info('performing ssh')
        ssh.do_ssh(self.hostname, self.port, self.username, self.password)
        
    def stop_validator(self):
        loggin.info("stopping validator service")
    
    def start_validator(self):
        loggin.info("starting validator service")

class Consensus_Thread(threading.Thread):
    def __init__(self, nodes):
      threading.Thread.__init__(self)
      self.shutdown_flag = threading.Event()
      self.nodes = nodes
    
    def run(self):
        logging.info('starting consensus thread')
        logging.info('calculating block list from the nodes')
        chains = self.calculate_block_list()
        self.compare_chains(chains)
        return
        
    def calculate_block_list(self):
        logging.info('getting block list from the nodes')
        node_list = ['http://10.223.155.43:8008']
        chains = _get_node_chains(node_list)
        return chains
    
    def compare_chains(self, chains):
        logging.info('comparing chains for equality')
        
        
    def calculate_sync_time(self):
        pass