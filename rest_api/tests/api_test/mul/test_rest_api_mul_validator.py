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


from google.protobuf.json_format import MessageToDict

from payload import get_signer, create_intkey_transaction , create_batch
from utils import  _get_client_address, _send_cmd, _get_node_list, \
                   _get_node_chain, check_for_consensus, _stop_validator

from base import RestApiBaseTest

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
  
WAIT_TIME = 10
  
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
        """Tests that node are brought up/down in a network
           and checks are performed on the respective nodes 
        """
        node_list = _get_node_list()
        chains = _get_node_chain(node_list)
        
        nbytes = 4096
        hostname = '10.223.155.130'
        port = 22
        username = '' 
        password = ''
        command = 'ps aux | grep sawtooth'
        
        try:
            ssh=paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname,port,username,password)
        except paramiko.AuthenticationException:
            print("Failed to connect to {} due to wrong username/password").format(hostname)
            exit(1)
        except:
            print("Failed to connect to {}").format(hostname)
            exit(2)
                
        command2 = 'sudo systemctl status sawtooth-rest-api.service'
        stdin,stdout,stderr=ssh.exec_command(command2)
        outlines=stdout.readlines()
        resp=''.join(outlines)
        print(resp)
        
        

        
        
        
        
