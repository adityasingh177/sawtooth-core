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
import hashlib

from google.protobuf.json_format import MessageToDict


from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_rest_api.protobuf.batch_pb2 import Batch
from sawtooth_rest_api.protobuf.batch_pb2 import BatchList
from sawtooth_rest_api.protobuf.batch_pb2 import BatchHeader
from sawtooth_rest_api.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_rest_api.protobuf.transaction_pb2 import Transaction

from utils import get_signer, create_intkey_transaction, create_batch , post_batch, \
                  get_state_list , get_blocks , get_transactions , get_batches , get_state, \
                  check_for_consensus, _get_node_list, _get_node_chains
                           

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

BLOCK_TO_CHECK_CONSENSUS = 1

pytestmark = pytest.mark.post


def test_rest_api_post_batch():
    """Tests that transactions are submitted and committed for
    each block that are created by submitting intkey batches
    """
    LOGGER.info('Starting test for batch post')
    
    signer = get_signer()
    expected_trxn_ids  = []
    expected_batch_ids = []
    initial_state_length = len(get_state_list())
    
    LOGGER.info("Creating intkey transactions with set operations")   
    txns = [
        create_intkey_transaction("set", 'a', 0, [], signer), 
        create_intkey_transaction("set", 'b', 0, [], signer),
        create_intkey_transaction("set", 'C', 0, [], signer),
    ]
    
    for txn in txns:
        data = MessageToDict(
                txn,
                including_default_value_fields=True,
                preserving_proto_field_name=True)
        
        trxn_id = data['header_signature']
        expected_trxn_ids.append(trxn_id)
    
    LOGGER.info("Creating batches for transactions 1trn/batch")
    
    batches = [create_batch([txn], signer) for txn in txns]

    for batch in batches:
        data = MessageToDict(
                batch,
                including_default_value_fields=True,
                preserving_proto_field_name=True)
        
        batch_id = data['header_signature']
        expected_batch_ids.append(batch_id)
    
    post_batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]    

    LOGGER.info("Submitting batches to the handlers")
     
    for batch in post_batch_list:
        try:
            response = post_batch(batch)
        except urllib.error.HTTPError as error:
            data = error.fp.read().decode('utf-8')
            LOGGER.info(data)
        
        block_batch_ids = [block['header']['batch_ids'][0] for block in get_blocks()]
        state_addresses = [state['address'] for state in get_state_list()['data']]
        state_head_list = [get_state(address)['head'] for address in state_addresses]
        committed_transaction_list = get_transactions()
        final_state_length= len(get_state_list())
        for trxn in committed_transaction_list:
            print(trxn['header_signature'])
            print(trxn['family_name'])
            print(trxn['family_version'])
            print(trxn['signer_public_key'])
            print(trxn['batcher_public_key'])
            
        if response['data'][0]['status'] == 'COMMITTED':
            LOGGER.info('Batch is committed')   
            
            """check transaction is submitted successfully"""   
             
            
            
            """check block is created for the batch"""
            
            for batch in batch_ids:
                if batch in block_batch_ids:
                    LOGGER.info("Block is created for the respective batch")

            """check state is updated when batch is committed  successfully"""
            
            
            assert initial_state_length ==  initial_state_length + 1      
        elif response['data'][0]['status'] == 'INVALID':
            LOGGER.info('Batch submission failed')
            
            if any(['message' in response['data'][0]['invalid_transactions'][0]]):
                message = response['data'][0]['invalid_transactions'][0]['message']
                LOGGER.info(message)
            
            """check transaction is not submitted successfully"""
            
            
            """check block is not created for the batch"""
            
            for batch in batch_ids:
                if batch in block_batch_ids:
                    LOGGER.info("Block is created for the respective batch")
            
            """check state is not updated when batch submission fails"""
            
            assert initial_state_length == final_state_length, "State should not be updated when batch submission fails"

    
    
    node_list = _get_node_list()
    chains = _get_node_chains(node_list)
    assert check_for_consensus(chains , BLOCK_TO_CHECK_CONSENSUS) == True

    
# def test_rest_post_two_trans_batch():
#     """Tests two same intkey transaction in one batch
#     """    
#     signer = get_signer()
#       
#     txns = [
#         create_intkey_transaction("set", 'a', 0, [], signer), 
#         create_intkey_transaction("set", 'a', 0, [], signer),   
#     ]
#       
#     batches = [create_batch([txn], signer) for txn in txns]
#     print(batches)
#   
#     batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]
#     print(batch_list)
#   
#           
#     for batch in batch_list:
#         post_batch(batch)
#     


# def test_rest_post_two_trans_batch():
#     """Tests two same intkey transaction in two different batches
#     """    
#     signer = get_signer()
#       
#     txns = [
#         create_intkey_transaction("set", 'a', 0, [], signer), 
#         create_intkey_transaction("set", 'a', 0, [], signer),   
#     ]
#       
#     batches = [create_batch([txn], signer) for txn in txns]
#     print(batches)
#   
#     batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]
#     print(batch_list)
#   
#           
#     for batch in batch_list:
#         post_batch(batch)
#     


 



 