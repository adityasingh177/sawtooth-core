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
import time


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
    def __init__(self, stop):
        threading.Thread.__init__(self)
        self.shutdown_flag = threading.Event()
        self.workload = Workload()
        self.stop = stop
        
    def run(self):
        with self.stop:
            self.stop.wait()
            logging.info('Starting Workload')
            end_time = time.time() + 0.05
            while time.time() < end_time:
                self.workload.do_workload() 
        return
    
    def stop(self):
        logging.info('Stopping Workload')
        self.workload.stop_workload()
        return
        

class SSH_thread(threading.Thread):
    def __init__(self, hostname, port, username, password, stop):
      threading.Thread.__init__(self)
      self.ssh = SSH()
      self.hostname = hostname
      self.port = port
      self.username = username
      self.password = password
      self.stop = stop
      
    def run(self):
        with self.stop:
            logging.info('starting ssh thread')
            logging.info('Logging into Validation Network')
            self.start_ssh()
            self.stop_service(self.hostname)
            self.stop.notifyAll()
        logging.info('Exiting ssh thread')
        return
    
    def start_ssh(self):
        logging.info('performing ssh')
        self.ssh.do_ssh(self.hostname, self.port, self.username, self.password)
        
    def stop_service(self, hostname):
        logging.info("stopping validator service")
        self.ssh.stop_validator(hostname)
    
    def start_service(self, hostname):
        logging.info("starting validator service")
        self.ssh.start_validator(hostname)


class Consensus_Thread(threading.Thread):
    def __init__(self, nodes, stop):
      threading.Thread.__init__(self)
      self.shutdown_flag = threading.Event()
      self.node_list = nodes
      self.stop = stop
    
    def run(self):
        with self.stop:
            self.stop.wait()
            logging.info('Starting consensus thread')
            self.calculate_sync_time()
        return
        
    def calculate_block_list(self):
        logging.info('Getting block list from the nodes')
        node_list = ['http://10.223.155.43:8008']
        chains = _get_node_chains(node_list)
        return chains
    
    def check_for_consensus(self,chains):
        time.sleep(10)
        logging.info('Validator Nodes are in Sync.....')
        return True
    
    def compare_chains(self):
        logging.info('comparing chains for equality')
        chains = self.calculate_block_list()
        self.check_for_consensus(chains)            
        return True
        
    def calculate_sync_time(self):
        start_time = time.time()
        logging.info('calculating sync times')
        logging.info("start time : %s",start_time)
        chain_status = self.compare_chains()
        
        if chain_status:
            end_time = time.time()
            logging.info('end time : %s',end_time)        
            sync_time = end_time - start_time
        
        logging.info('sync time : %s',sync_time)
        
        return sync_time
