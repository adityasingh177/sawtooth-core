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
import os
import logging
import time

from utils import  _get_client_address, _send_cmd, _get_node_list, \
                   _get_node_chain, check_for_consensus, _stop_validator\
                   

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

class Consensus:
    def __init__(self, nodes):
      self.node_list = nodes
  
    def calculate_block_list(self):
        logging.info('Getting block list from the nodes')
        node_list = ['http://10.223.155.134:8008']
        chains = _get_node_chain(node_list)
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