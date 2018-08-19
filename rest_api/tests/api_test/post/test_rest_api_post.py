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

from utils import post_batch, get_state_list , get_blocks , get_transactions, \
                  get_batches , get_state_address, check_for_consensus,\
                  _get_node_list, _get_node_chains
                  

from payload import get_signer, create_intkey_transaction, create_batch,\
                    create_intkey_same_transaction

from base import RestApiBaseTest

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

BAD_PROTOBUF = b'BAD_PROTOBUF'
EMPTY_BATCH = b''
NO_BATCHES_SUBMITTED = 34
BAD_PROTOBUF_SUBMITTED = 35
BATCH_QUEUE_FULL = 31
INVALID_BATCH = 30
WRONG_CONTENT_TYPE = 43

BLOCK_TO_CHECK_CONSENSUS = 1

pytestmark = pytest.mark.post


class TestPost(RestApiBaseTest):
    def test_rest_api_post_batch(self):
        """Tests that transactions are submitted and committed for
        each block that are created by submitting intkey batches
        with set operations
        """
        LOGGER.info('Starting test for batch post')
    
        signer = get_signer()
        expected_trxn_ids  = []
        expected_batch_ids = []
        initial_state_length = len(get_state_list()['data'])
    
        LOGGER.info("Creating intkey transactions with set operations")
        txns = [
            create_intkey_transaction("set", [] , 50 , signer),
            create_intkey_transaction("set", [] , 50 , signer),
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
    
            block_batch_ids = [block['header']['batch_ids'][0] for block in get_blocks()['data']]
            state_addresses = [state['address'] for state in get_state_list()['data']]
            state_head_list = [get_state_address(address)['head'] for address in state_addresses]
            committed_transaction_list = get_transactions()['data']
                
            if response['data'][0]['status'] == 'COMMITTED':
                LOGGER.info('Batch is committed')
    
                for batch in expected_batch_ids:
                    if batch in block_batch_ids:
                        LOGGER.info("Block is created for the respective batch")
    
            elif response['data'][0]['status'] == 'INVALID':
                LOGGER.info('Batch submission failed')
    
                if any(['message' in response['data'][0]['invalid_transactions'][0]]):
                    message = response['data'][0]['invalid_transactions'][0]['message']
                    LOGGER.info(message)
    
                for batch in batch_ids:
                    if batch in block_batch_ids:
                        LOGGER.info("Block is created for the respective batch")
        
        final_state_length = len(get_state_list()['data'])
        node_list = _get_node_list()
        chains = _get_node_chains(node_list)
        assert final_state_length ==  initial_state_length + len(expected_batch_ids)
        assert check_for_consensus(chains , BLOCK_TO_CHECK_CONSENSUS) == True
        
    def test_rest_api_no_batches(self):
        LOGGER.info("Starting test for batch with bad protobuf")
                         
        try:
            response = post_batch(batch=EMPTY_BATCH)
        except urllib.error.HTTPError as error:
            response = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(response['error']['title'])
            LOGGER.info(response['error']['message'])
                  
        self.assert_valid_error(response, NO_BATCHES_SUBMITTED)
    
    def test_rest_api_bad_protobuf(self):
        LOGGER.info("Starting test for batch with bad protobuf")
                         
        try:
            response = post_batch(batch=BAD_PROTOBUF)
        except urllib.error.HTTPError as error:
            response = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(response['error']['title'])
            LOGGER.info(response['error']['message'])
                          
        self.assert_valid_error(response, BAD_PROTOBUF_SUBMITTED)
    
    def test_rest_api_post_wrong_header(self,setup):
        """Tests rest api by posting with wrong header
        """
        LOGGER.info('Starting test for batch post')
    
        signer = get_signer()
        expected_trxn_ids  = []
        expected_batch_ids = []
        initial_state_length = len(get_state_list())
    
        LOGGER.info("Creating intkey transactions with set operations")
        txns = [
            create_intkey_transaction("set", [] , 50 , signer),
            create_intkey_transaction("set", [] , 50 , signer),
            create_intkey_transaction("set", [] , 50 , signer),
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
                response = post_batch(batch,headers="True")
            except urllib.error.HTTPError as e:
                errdata = e.file.read().decode("utf-8")
                error = json.loads(errdata)
                LOGGER.info(error['error']['message'])
                assert (json.loads(errdata)['error']['code']) == 42
                assert e.code == 400

    def test_rest_api_post_same_txns(self, setup):
        """Tests the rest-api by submitting multiple transactions with same key
        """
        LOGGER.info('Starting test for batch post')
    
        signer = get_signer()
        expected_trxn_ids  = []
        expected_batch_ids = []
        initial_state_length = len(get_state_list())
    
        LOGGER.info("Creating intkey transactions with set operations")
        txns = [
            create_intkey_same_transaction("set", [] , 50 , signer),
            create_intkey_same_transaction("set", [] , 50 , signer),
            create_intkey_same_transaction("set", [] , 50 , signer),
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
                response = post_batch(batch,headers="None")
                assert response['data'][0]['status'] == "INVALID"
            except urllib.error.HTTPError as e:
                errdata = e.file.read().decode("utf-8")
                error = json.loads(errdata)
                LOGGER.info(error['error']['message'])
                assert (json.loads(errdata)['error']['code']) == 42
                assert e.code == 400
                    
    def test_rest_api_multiple_txns_batches(self, setup):
        """Tests rest-api state by submitting multiple
            transactions in multiple batches
        """
        LOGGER.info('Starting test for batch post')
    
        signer = get_signer()
        expected_trxn_ids  = []
        expected_batch_ids = []
        initial_state_length = len(get_state_list())
    
        LOGGER.info("Creating intkey transactions with set operations")
        txns = [
            create_intkey_transaction("set", [] , 50 , signer),
            create_intkey_transaction("set", [] , 50 , signer),
            create_intkey_transaction("set", [] , 50 , signer),
        ]
    
        for txn in txns:
            data = MessageToDict(
                    txn,
                    including_default_value_fields=True,
                    preserving_proto_field_name=True)
    
            trxn_id = data['header_signature']
            expected_trxn_ids.append(trxn_id)
    
        LOGGER.info("Creating batches for transactions 1trn/batch")
    
        batches = [create_batch([txns], signer)]
    
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
                response = post_batch(batch,headers="None")
                response = get_state_list()
            except urllib.error.HTTPError as e:
                errdata = e.file.read().decode("utf-8")
                error = json.loads(errdata)
                LOGGER.info(error['error']['message'])
                assert (json.loads(errdata)['error']['code']) == 17
                assert e.code == 400
        final_state_length = len(get_state_list())
        assert initial_state_length == final_state_length
        
    def test_api_post_batch_different_signer(self, setup):
        signer_trans = get_signer() 
        intkey=create_intkey_transaction("set",[],50,signer_trans)
        translist=[intkey]
        signer_batch = get_signer()
        batch= create_batch(translist,signer_batch)
        batch_list=[BatchList(batches=[batch]).SerializeToString()]
        for batc in batch_list:
            try:
                response = post_batch(batc)
                print(response)
            except urllib.error.HTTPError as error:
                LOGGER.info("Rest Api is not reachable")
                data = json.loads(error.fp.read().decode('utf-8'))
                LOGGER.info(data['error']['title'])
                LOGGER.info(data['error']['message'])
                assert data['error']['code'] == 30
                assert data['error']['title'] =='Submitted Batches Invalid' 
                    
    def test_api_post_batch_different_signer(self, setup):
        signer_trans = get_signer() 
        intkey=create_intkey_transaction("set",[],50,signer_trans)
        translist=[intkey]
        signer_batch = get_signer()
        batch= create_batch(translist,signer_batch)
        batch_list=[BatchList(batches=[batch]).SerializeToString()]
        for batc in batch_list:
            try:
                response = post_batch(batc)
                print(response)
            except urllib.error.HTTPError as error:
                LOGGER.info("Rest Api is not reachable")
                data = json.loads(error.fp.read().decode('utf-8'))
                LOGGER.info(data['error']['title'])
                LOGGER.info(data['error']['message'])
                assert data['error']['code'] == 30
                assert data['error']['title'] =='Submitted Batches Invalid'
    

        