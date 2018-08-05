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

from google.protobuf.json_format import MessageToDict

from payload import get_signer, create_intkey_transaction , create_batch
from utils import  _get_client_address, _send_cmd, _get_node_list, \
                   _get_node_chain, check_for_consensus

from base import RestApiBaseTest

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
WAIT = 300
  
WORKLOAD_TIME = 5
  
BLOCK_TO_CHECK_CONSENSUS = 1
  
INTKEY_PREFIX = '1cf126'
XO_PREFIX = '5b7349'
  
  
pytestmark = pytest.mark.scenario
               
class TestScenario(RestApiBaseTest):  
    def test_rest_api_mul_val_intk_xo(self):
        """Tests that transactions are submitted and committed for
        each block that are created by submitting intkey and XO batches
        """
        signer = get_signer()
        expected_trxns  = {}
        expected_batches = []
        node_list = [{_get_client_address()}]
            
        LOGGER.info('Starting Test for Intkey and Xo as payload')
            
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
            
        LOGGER.info("Creating keys for xo users")
              
        for username in ('aditya', 'singh'):
            _send_cmd('sawtooth keygen {} --force'.format(username))
                  
              
        LOGGER.info("Submitting xo batches to the handlers")
          
                  
        xo_cmds = (
                'xo create game-1 --username aditya',
                'xo take game-1 1 --username singh',
                'xo take game-1 4 --username aditya',
                'xo take game-1 2 --username singh',
            )
              
        for cmd in xo_cmds:
                _send_cmd(
                    '{} --url {} --wait {}'.format(
                        cmd,
                        _get_client_address(),
                        WAIT))
        xo_cli_cmds = (
                'xo list',
                'xo show game-1',
            )
              
        for cmd in xo_cli_cmds:
                _send_cmd(
                    '{} --url {}'.format(
                        cmd,
                        _get_client_address()))
            
        xo_delete_cmds = (
                'xo delete game-1 --username aditya',
            )
        
        for cmd in xo_delete_cmds:
            _send_cmd(
                '{} --url {} --wait {}'.format(
                    cmd,
                    _get_client_address(),
                    WAIT))
         
        node_list = _get_node_list()
            
        chains = _get_node_chain(node_list)
        check_for_consensus(chains , BLOCK_TO_CHECK_CONSENSUS)
