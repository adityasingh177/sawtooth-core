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

from fixtures import setup_empty_trxs_batch

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

pytestmark = [pytest.mark.post,pytest.mark.last]


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
        

    def test_api_post_empty_trxns_list(self, setup_empty_trxs_batch):
        batch = setup_empty_trxs_batch
        post_batch_list = [BatchList(batches=[batch]).SerializeToString()]
        
        for batch in post_batch_list:
            response = post_batch(batch)

           
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
            except urllib.error.HTTPError as error:
                LOGGER.info("Rest Api is not reachable")
                data = json.loads(error.fp.read().decode('utf-8'))
                LOGGER.info(data['error']['title'])
                LOGGER.info(data['error']['message'])
                assert data['error']['code'] == 30
                assert data['error']['title'] =='Submitted Batches Invalid'
    
    def test_rest_api_post_no_endpoint(self, setup):
        
        signer_trans = get_signer() 
        intkey=create_intkey_transaction("set",[],50,signer_trans)
        translist=[intkey]
        batch= create_batch(translist,signer_trans)
        batch_list=[BatchList(batches=[batch]).SerializeToString()]
        for batc in batch_list:
            try:
                response = post_batch_no_endpoint(batc)
            except urllib.error.HTTPError as e:
                errdata = e.file.read().decode("utf-8")
                errcode = e.code
            assert errcode == 404



class TestPostMulTxns(RestApiBaseTest):
    
    def test_txn_invalid_addr(self, setup_invalid_txns):
        initial_batch_length = setup_invalid_txns['initial_batch_length']
        expected_batch_length = setup_invalid_txns['expected_batch_length']
        initial_trn_length = setup_invalid_txns['initial_trn_length']
        expected_trn_length = setup_invalid_txns['expected_trn_length']
        assert initial_batch_length < expected_batch_length
        assert initial_trn_length < expected_trn_length
        assert setup_invalid_txns['response'] == 'INVALID'
        
    def test_txn_invalid_min(self, setup_invalid_txns_min):
        initial_batch_length = setup_invalid_txns_min['initial_batch_length']
        expected_batch_length = setup_invalid_txns_min['expected_batch_length']
        initial_trn_length = setup_invalid_txns_min['initial_trn_length']
        expected_trn_length = setup_invalid_txns_min['expected_trn_length']
        assert initial_batch_length < expected_batch_length
        assert initial_trn_length < expected_trn_length
        assert setup_invalid_txns_min['response'] == 'INVALID'
        
    def test_txn_invalid_max(self, setup_invalid_txns_max):
        initial_batch_length = setup_invalid_txns_max['initial_batch_length']
        expected_batch_length = setup_invalid_txns_max['expected_batch_length']
        initial_trn_length = setup_invalid_txns_max['initial_trn_length']
        expected_trn_length = setup_invalid_txns_max['expected_trn_length']
        assert initial_batch_length < expected_batch_length
        assert initial_trn_length < expected_trn_length
        assert setup_invalid_txns_max['response'] == 'INVALID'
        
    def test_txn_valid_invalid_txns(self, setup_valinv_txns):
        #data=Txns.setup_batch_valinv_txns()
        initial_batch_length = setup_valinv_txns['initial_batch_length']
        expected_batch_length = setup_valinv_txns['expected_batch_length']
        initial_trn_length = setup_valinv_txns['initial_trn_length']
        expected_trn_length = setup_valinv_txns['expected_trn_length']
        assert initial_batch_length < expected_batch_length
        assert initial_trn_length < expected_trn_length
        assert setup_valinv_txns['response'] == 'INVALID'
        
    def test_txn_invalid_valid_txns(self, setup_invval_txns):     
        initial_batch_length = setup_invval_txns['initial_batch_length']
        expected_batch_length = setup_invval_txns['expected_batch_length']
        initial_trn_length = setup_invval_txns['initial_trn_length']
        expected_trn_length = setup_invval_txns['expected_trn_length']
        assert initial_batch_length < expected_batch_length
        assert initial_trn_length < expected_trn_length
        assert setup_invval_txns['response'] == 'INVALID'
       
    def test_txn_same_txns(self, setup_same_txns):
        initial_batch_length = setup_same_txns['initial_batch_length']
        expected_batch_length = setup_same_txns['expected_batch_length']
        initial_trn_length = setup_same_txns['initial_trn_length']
        expected_trn_length = setup_same_txns['expected_trn_length']
        assert initial_batch_length < expected_batch_length
        assert initial_trn_length < expected_trn_length
        assert setup_same_txns['code'] == 30
    
    def test_api_sent_commit_txns(self, setup_valid_txns):
        expected_transaction=setup_valid_txns['expected_txns']
         
        transaction_id=str(expected_transaction)[2:-2]
        try:   
             response = get_reciepts(transaction_id)
             assert transaction_id == response['data'][0]['id'] 
             assert response['data'][0]['state_changes'][0]['type'] == "SET"    
        except urllib.error.HTTPError as error:
             LOGGER.info("Rest Api is Unreachable")
             response = json.loads(error.fp.read().decode('utf-8'))
             LOGGER.info(response['error']['title'])
             LOGGER.info(response['error']['message'])
             assert response['error']['code'] == RECEIPT_NOT_FOUND
             assert response['error']['title'] == 'Invalid Resource Id'
    
    def test_txn_invalid_family_name(self, setup_invalid_txns_fn):
        initial_batch_length = setup_invalid_txns_fn['initial_batch_length']
        expected_batch_length = setup_invalid_txns_fn['expected_batch_length']
        initial_trn_length = setup_invalid_txns_fn['initial_trn_length']
        expected_trn_length = setup_invalid_txns_fn['expected_trn_length']
        assert initial_batch_length < expected_batch_length
        assert initial_trn_length < expected_trn_length
        assert setup_invalid_txns_fn['code'] == 17
    
    def test_txn_invalid_bad_addr(self, setup_invalid_invaddr):
        initial_batch_length = setup_invalid_invaddr['initial_batch_length']
        expected_batch_length = setup_invalid_invaddr['expected_batch_length']
        initial_trn_length = setup_invalid_invaddr['initial_trn_length']
        expected_trn_length = setup_invalid_invaddr['expected_trn_length']
        assert initial_batch_length < expected_batch_length
        assert initial_trn_length < expected_trn_length
        assert setup_invalid_invaddr['code'] == 17
    

        