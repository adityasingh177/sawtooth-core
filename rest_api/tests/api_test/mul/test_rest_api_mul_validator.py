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
import pytest
import logging
import json
import urllib.request
import urllib.error
import base64
import argparse
import cbor
import subprocess
import shlex
import requests
import time
import paramiko
import sys
import threading
import os


from google.protobuf.json_format import MessageToDict

from base import RestApiBaseTest
from payload import get_signer, create_intkey_transaction , create_batch
from utils import  _get_client_address, _send_cmd, _get_node_list, \
                   _get_node_chain, check_for_consensus, _stop_validator\
            
from workload import Workload
from ssh import SSH



logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )
  
WAIT_TIME = 10
PORT =22
USERNAME = 'test'
PASSWORD = 'aditya9971'
  
BLOCK_TO_CHECK_CONSENSUS = 1

pytestmark = pytest.mark.mul


class TestMultiple(RestApiBaseTest):
    def test_rest_api_mul_val_intk(self):
        """Tests that transactions are submitted and committed for
        each block that are created by submitting intkey and XO batches
        """
        signer = get_signer()
        expected_trxns  = {}
        expected_batches = []
        node_list = [{_get_client_address()}]
            
        LOGGER.info('Starting Test for Intkey payload')
            
        LOGGER.info("Creating intkey batches")
        
        txns = [
            create_intkey_transaction("set", [] , 50 , signer),
            create_intkey_transaction("set", [] , 50 , signer),
       ]
    
        for txn in txns:
            dict = MessageToDict(
                    txn,
                    including_default_value_fields=True,
                    preserving_proto_field_name=True)
                    
            expected_trxns['trxn_id'] = [dict['header_signature']]
            expected_trxns['payload'] = [dict['payload']]
                        
        LOGGER.info("Creating batches for transactions 1trn/batch")
    
        batches = [create_batch([txn], signer) for txn in txns]
         
        node_list = _get_node_list()
            
        chains = _get_node_chain(node_list)
        check_for_consensus(chains , BLOCK_TO_CHECK_CONSENSUS)

    def test_rest_api_mul_val_Node(self):
        """Tests that leaf nodes are brought up/down in a network
           and checks are performed on the respective nodes 
        """
        node_list = ['10.223.155.134' , '10.223.155.25']
        
        threads = []
        
        workload = Workload()
        ssh = SSH()
         
        workload_thread = threading.Thread(target=workload.do_workload())
         
        for node in node_list:
            t= threading.Thread(target=ssh.do_ssh(node, PORT, USERNAME, PASSWORD))
            threads.append(t)    
         
        for t in threads:
            t.start()
            
        workload_thread.start()
        
           
        
        

        
        
        
        
