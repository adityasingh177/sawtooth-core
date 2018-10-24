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
import aiohttp
import asyncio

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
                  _get_node_list, _get_node_chains, post_batch_no_endpoint,\
                  get_reciepts, _get_client_address, state_count
                  

from payload import get_signer, create_intkey_transaction, create_batch,\
                    create_intkey_same_transaction

from base import RestApiBaseTest

from fixtures import setup_empty_trxs_batch, setup_invalid_txns,setup_invalid_txns_min,\
                     setup_invalid_txns_max, setup_valinv_txns, setup_invval_txns, \
                     setup_same_txns, setup_valid_txns, setup_invalid_txns_fn,\
                     setup_invalid_invaddr
                     

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

BAD_PROTOBUF = b'BAD_PROTOBUF'
EMPTY_BATCH = b''
NO_BATCHES_SUBMITTED = 34
BAD_PROTOBUF_SUBMITTED = 35
WRONG_HEADER_TYPE=42
BATCH_QUEUE_FULL = 31
INVALID_BATCH = 30
WRONG_CONTENT_TYPE = 43
WAIT=300
RECEIPT_NOT_FOUND = 80

BLOCK_TO_CHECK_CONSENSUS = 1

pytestmark = [pytest.mark.post,pytest.mark.last]

async def async_fetch_url(url, session,params=None):
    try:
        async with session.get(url) as response:
            return await response.json()
    except aiohttp.client_exceptions.ClientResponseError as error:
        LOGGER.info(error)

async def async_post_batch(url, session, data, params=None,headers=None):
    if headers:
        headers=headers
    else:
        headers = {'Content-Type': 'application/octet-stream'}
    try:
        async with session.post(url,data=data,headers=headers) as response:
            data = await response.json()
            if 'link' in data:
                link = data['link']
                return await async_fetch_url('{}&wait={}'.format(link, WAIT),session)
            else:
                return data
    except aiohttp.client_exceptions.ClientResponseError as error:
        LOGGER.info(error)
        
        
class TestPostList(RestApiBaseTest):
    async def test_rest_api_post_batch(self):
        """Tests that transactions are submitted and committed for
        each block that are created by submitting intkey batches
        with set operations
        """
        LOGGER.info('Starting test for batch post')
    
        signer = get_signer()
        expected_trxn_ids  = []
        expected_batch_ids = []
        address = _get_client_address()
        url='{}/batches'.format(address)
        tasks=[]
    
        LOGGER.info("Creating intkey transactions with set operations")
        txns = [
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
    
        try:
            async with aiohttp.ClientSession() as session: 
                for batch in post_batch_list:
                    task = asyncio.ensure_future(async_post_batch(url,session,data=batch))
                    tasks.append(task)
                responses = await asyncio.gather(*tasks)
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
        
        block_batch_ids = [block['header']['batch_ids'][0] for block in get_blocks()['data']]
        state_addresses = [state['address'] for state in get_state_list()['data']]
        state_head_list = [get_state_address(address)['head'] for address in state_addresses]
        committed_transaction_list = get_transactions()['data']
                    
        for response in responses:
            if response['data'][0]['status'] == 'COMMITTED':
                LOGGER.info('Batch is committed')
     
                for batch in expected_batch_ids:
                    if batch in block_batch_ids:
                        LOGGER.info("Block is created for the respective batch")
                     
            elif response['data'][0]['status'] == 'INVALID':
                LOGGER.info('Batch is not committed')
     
                if any(['message' in response['data'][0]['invalid_transactions'][0]]):
                    message = response['data'][0]['invalid_transactions'][0]['message']
                    LOGGER.info(message)
     
                for batch in batch_ids:
                    if batch not in block_batch_ids:
                        LOGGER.info("Block is not created for the respective batch")
                            
        node_list = _get_node_list()
        chains = _get_node_chains(node_list)
        assert check_for_consensus(chains , BLOCK_TO_CHECK_CONSENSUS) == True
        
    async def test_rest_api_no_batches(self):
        LOGGER.info("Starting test for batch with bad protobuf")
        address = _get_client_address()
        url='{}/batches'.format(address)
        tasks=[]
                                  
        try:
            async with aiohttp.ClientSession() as session: 
                task = asyncio.ensure_future(async_post_batch(url,session,data=EMPTY_BATCH))
                tasks.append(task)
                response = await asyncio.gather(*tasks)
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
                           
        self.assert_valid_error(response[0], NO_BATCHES_SUBMITTED)
    
    async def test_rest_api_bad_protobuf(self):
        LOGGER.info("Starting test for batch with bad protobuf")
                         
        address = _get_client_address()
        url='{}/batches'.format(address)
        tasks=[]
                                  
        try:
            async with aiohttp.ClientSession() as session: 
                task = asyncio.ensure_future(async_post_batch(url,session,data=BAD_PROTOBUF))
                tasks.append(task)
                response = await asyncio.gather(*tasks)
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
        
        self.assert_valid_error(response[0], BAD_PROTOBUF_SUBMITTED)
    
    async def test_rest_api_post_wrong_header(self,setup):
        """Tests rest api by posting with wrong header
        """
        LOGGER.info('Starting test for batch post')
    
        signer = get_signer()
        expected_trxn_ids  = []
        expected_batch_ids = []
        address = _get_client_address()
        url='{}/batches'.format(address)
        tasks=[]
        headers = {'Content-Type': 'application/json'}
    
        LOGGER.info("Creating intkey transactions with set operations")
        txns = [
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
        
        try:
            async with aiohttp.ClientSession() as session: 
                for batch in post_batch_list:
                    task = asyncio.ensure_future(async_post_batch(url,session,data=batch,headers=headers))
                    tasks.append(task)
                responses = await asyncio.gather(*tasks)
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
        
        for response in responses:            
            self.assert_valid_error(response, WRONG_HEADER_TYPE)
               
    async def test_rest_api_post_same_txns(self, setup):
        """Tests the rest-api by submitting multiple transactions with same key
        """
        LOGGER.info('Starting test for batch post')
        address = _get_client_address()
        url='{}/batches'.format(address)
        tasks=[]
        signer = get_signer()
        expected_trxn_ids  = []
        expected_batch_ids = []
        initial_state_length = state_count()
    
        LOGGER.info("Creating intkey transactions with set operations")
        txns = [
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
    
        try:
            async with aiohttp.ClientSession() as session: 
                for batch in post_batch_list:
                    task = asyncio.ensure_future(async_post_batch(url,session,data=batch))
                    tasks.append(task)
                responses = await asyncio.gather(*tasks)
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
        
                    
    async def test_rest_api_multiple_txns_batches(self, setup):
        """Tests rest-api state by submitting multiple
            transactions in multiple batches
        """
        LOGGER.info('Starting test for batch post')
    
        signer = get_signer()
        expected_trxn_ids  = []
        expected_batch_ids = []
        address = _get_client_address()
        url='{}/batches'.format(address)
        tasks=[]
    
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
    
        try:
            async with aiohttp.ClientSession() as session: 
                for batch in post_batch_list:
                    task = asyncio.ensure_future(async_post_batch(url,session,data=batch))
                    tasks.append(task)
                responses = await asyncio.gather(*tasks)
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
                
        block_batch_ids = [block['header']['batch_ids'][0] for block in get_blocks()['data']]
        state_addresses = [state['address'] for state in get_state_list()['data']]
        state_head_list = [get_state_address(address)['head'] for address in state_addresses]
        committed_transaction_list = get_transactions()['data']
            
        for response in responses:
            if response['data'][0]['status'] == 'COMMITTED':
                LOGGER.info('Batch is committed')
     
                for batch in expected_batch_ids:
                    if batch in block_batch_ids:
                        LOGGER.info("Block is created for the respective batch")
                     
            elif response['data'][0]['status'] == 'INVALID':
                LOGGER.info('Batch is not committed')
     
                if any(['message' in response['data'][0]['invalid_transactions'][0]]):
                    message = response['data'][0]['invalid_transactions'][0]['message']
                    LOGGER.info(message)
     
                for batch in expected_batch_ids:
                    if batch not in block_batch_ids:
                        LOGGER.info("Block is not created for the respective batch")
                            
        node_list = _get_node_list()
        chains = _get_node_chains(node_list)
        assert check_for_consensus(chains , BLOCK_TO_CHECK_CONSENSUS) == True
        

    async def test_api_post_empty_trxns_list(self, setup_empty_trxs_batch):
        address = _get_client_address()
        url='{}/batches'.format(address)
        tasks=[]
        batch = setup_empty_trxs_batch
        post_batch_list = [BatchList(batches=[batch]).SerializeToString()]
          
        try:
            async with aiohttp.ClientSession() as session: 
                for batch in post_batch_list:
                    task = asyncio.ensure_future(async_post_batch(url,session,data=batch))
                    tasks.append(task)
                response = await asyncio.gather(*tasks)
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")

           
    async def test_api_post_batch_different_signer(self, setup):
        address = _get_client_address()
        url='{}/batches'.format(address)
        tasks=[]
        signer_trans = get_signer() 
        intkey=create_intkey_transaction("set",[],50,signer_trans)
        translist=[intkey]
        signer_batch = get_signer()
        batch= create_batch(translist,signer_batch)
        post_batch_list=[BatchList(batches=[batch]).SerializeToString()]
        
        try:
            async with aiohttp.ClientSession() as session: 
                for batch in post_batch_list:
                    task = asyncio.ensure_future(async_post_batch(url,session,data=batch))
                    tasks.append(task)
                response = await asyncio.gather(*tasks)
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
        
        self.assert_valid_error(response[0], INVALID_BATCH)
    
    async def test_rest_api_post_no_endpoint(self, setup):
        address = _get_client_address()
        url='/'.format(address)
        tasks=[]
        signer_trans = get_signer() 
        intkey=create_intkey_transaction("set",[],50,signer_trans)
        translist=[intkey]
        batch= create_batch(translist,signer_trans)
        post_batch_list=[BatchList(batches=[batch]).SerializeToString()]
        try:
            async with aiohttp.ClientSession() as session: 
                for batch in post_batch_list:
                    task = asyncio.ensure_future(async_post_batch(url,session,data=batch))
                    tasks.append(task)
                response = await asyncio.gather(*tasks)
        except aiohttp.client_exceptions.InvalidURL as error:
            LOGGER.info("Rest Api is Unreachable")
            LOGGER.info("Url is not correct")


class TestPostInvalidTxns(RestApiBaseTest):    
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

    def test_txn_invalid_bad_addr(self, setup_invalid_invaddr):
        initial_batch_length = setup_invalid_invaddr['initial_batch_length']
        expected_batch_length = setup_invalid_invaddr['expected_batch_length']
        initial_trn_length = setup_invalid_invaddr['initial_trn_length']
        expected_trn_length = setup_invalid_invaddr['expected_trn_length']
        assert initial_batch_length < expected_batch_length
        assert initial_trn_length < expected_trn_length
    
    def test_txn_invalid_family_name(self, setup_invalid_txns_fn):
        initial_batch_length = setup_invalid_txns_fn['initial_batch_length']
        expected_batch_length = setup_invalid_txns_fn['expected_batch_length']
        initial_trn_length = setup_invalid_txns_fn['initial_trn_length']
        expected_trn_length = setup_invalid_txns_fn['expected_trn_length']
        assert initial_batch_length < expected_batch_length
        assert initial_trn_length < expected_trn_length
    

        