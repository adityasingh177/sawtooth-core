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
import subprocess
import paramiko
import re
import fabric


from google.protobuf.json_format import MessageToDict

from base import RestApiBaseTest
from utils import  _get_client_address, _send_cmd, _get_node_list, \
                   _get_node_chain, check_for_consensus, _stop_validator\
                   

from payload import get_signer, create_intkey_transaction, create_batch
            
from workload import Workload
from test_ssh import SSH_CLIENT
from consensus import Consensus


logging.getLogger("paramiko").setLevel(logging.INFO) 
  
WAIT_TIME = 10
PORT = 22
USERNAME = 'test'
PASSWORD = 'aditya9971'
  
BLOCK_TO_CHECK_CONSENSUS = 1

pytestmark = pytest.mark.mul


class TestMultiValidator(RestApiBaseTest):
    def test_rest_api_mul_val_intk(self):
        """Tests that transactions are submitted and committed for
        each block that are created by submitting intkey and XO batches
        """
        signer = get_signer()
        expected_trxns  = {}
        expected_batches = []
        node_list = [{_get_client_address()}]
             
        logging.info('Starting Test for Intkey as payload')
             
        logging.info("Creating intkey batches")
         
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
                         
        logging.info("Creating batches for transactions 1trn/batch")
     
        batches = [create_batch([txn], signer) for txn in txns]
                      
        node_list = _get_node_list()
             
        chains = _get_node_chain(node_list)
        check_for_consensus(chains , BLOCK_TO_CHECK_CONSENSUS)
        
#     def test_rest_api_mul_val_Node(self):
#         """Tests that leaf nodes are brought up/down in a network
#            and checks are performed on the respective nodes 
#         """      
#         logging.info('Starting Test for multiple validators')
#         leaf_nodes = ['10.223.155.134']
#         workload = Workload()
#         ssh_client = paramiko.SSHClient()
#         consensus = Consensus(leaf_nodes)
#         pids = []
#         
#         try:
#             ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#             ssh_client.load_system_host_keys()
#             ssh_client.connect(leaf_nodes[0],PORT,USERNAME,PASSWORD)
#         except paramiko.AuthenticationException:
#             logging.info("Failed to connect to {} due to wrong username/password".format(leaf_nodes[0]))
#             exit(1)
#         except:
#             logging.info("Failed to connect to {}".format(leaf_nodes[0]))
#             exit(2)
#         
#         stdin,stdout,stderr=ssh_client.exec_command("sudo -u sawtooth intkey-tp-python -C tcp://127.0.0.1:4004 -v")
#         outlines=stdout.readlines()
#         resp=''.join(outlines)
#         print(resp)

        