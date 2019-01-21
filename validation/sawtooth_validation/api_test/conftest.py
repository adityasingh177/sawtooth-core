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
import sys
import platform
import inspect
import logging
import urllib
import json
import os

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_sdk.protobuf.validator_pb2 import Message
from sawtooth_sdk.protobuf import client_batch_submit_pb2
from sawtooth_sdk.protobuf import client_batch_pb2
from sawtooth_sdk.protobuf import client_list_control_pb2

from sawtooth_sdk.protobuf.batch_pb2 import Batch
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction

from sawtooth_validation.utils import get_batches,  get_transactions, get_state_address, post_batch, get_blocks, \
                  get_state_list , _delete_genesis , _start_validator, \
                  _stop_validator , _create_genesis , _get_client_address, \
                  _stop_settings_tp, _start_settings_tp,state_count,transaction_count,batch_count

from sawtooth_validation.payload import get_signer, create_intkey_transaction , create_batch,\
                    create_invalid_intkey_transaction, create_intkey_same_transaction, random_word_list, IntKeyPayload, \
                    make_intkey_address, Transactions


from google.protobuf.message import DecodeError
from google.protobuf.json_format import MessageToDict
from sawtooth_validation.base import BaseTest

LIMIT = 100 
WAIT = 300
BATCH_SIZE = 1
WORD_COUNT=50
                  
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

class Setup(BaseTest):
    def __init__(self):
        self.data = {}
        self.signer= get_signer()
        self.address = _get_client_address()
        self.url='{}/batches'.format(self.address) 
        
    def _create_transactions(self):
        LOGGER.info("Creating intkey transactions with set operations")
        txns = [create_intkey_transaction("set", [] , WORD_COUNT , self.signer) for i in range(BATCH_SIZE)]
        return txns
        
    
    def _create_batches(self,txns):
        LOGGER.info("Creating batches for transactions 1trn/batch")
        batches = [create_batch([txn], self.signer) for txn in txns]
        return batches
    
    def _create_batch_list(self,batches):
        batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches] 
        return batch_list
    
    
    def _batch_statuses(self,expected_batches):
        LOGGER.info("Batch statuses for the created batches")
        for batch in expected_batches:
            response = get_batch_statuses([batch])
            status = response['data'][0]['status']
            LOGGER.info(status)
            
    
    def _expected_batch_ids(self,batches):
        LOGGER.info("Expected batch ids")
        expected_batches = []
        for batch in batches:
            dict = MessageToDict(
                    batch,
                    including_default_value_fields=True,
                    preserving_proto_field_name=True)
    
            batch_id = dict['header_signature']
            expected_batches.append(batch_id)
        return expected_batches
    
    
    def _expected_txn_ids(self,txns):
        LOGGER.info("Expected transaction ids")
        expected_txns  = {}
        for txn in txns:
            dict = MessageToDict(
                    txn,
                    including_default_value_fields=True,
                    preserving_proto_field_name=True)
            
            if 'trxn_id' not in expected_txns:
                expected_txns['trxn_id'] = []
            if 'payload' not in expected_txns:
                expected_txns['payload'] =[]
                    
            expected_txns['trxn_id'].append(dict['header_signature'])
            expected_txns['payload'].append(dict['payload'])
        return expected_txns
    
    
    def _submit_batches(self,batch_list):
        print("Submitting batches to the route handlers")
        import time
        start_time = time.time()
        for batch in batch_list:
            try:
                response = post_batch(batch)
            except urllib.error.HTTPError as error:
                LOGGER.info("Rest Api is not reachable")
                response = json.loads(error.fp.read().decode('utf-8'))
                LOGGER.info(response['error']['title'])
                LOGGER.info(response['error']['message'])
        print(time.time()-start_time)
        return response
    
    
    def _initial_count(self):
        LOGGER.info("Calculating the initial count of batches,transactions, state before submission of batches")
        data = self.data
        data['state_length'] = state_count()
        data['transaction_length'] = transaction_count()
        data['batch_length'] = batch_count()
        return data
        
    
    def _expected_count(self,txns,batches):
        LOGGER.info("Calculating the expected count of batches, transactions, state")
        data = self.data
        self._initial_count()
        expected_txns=self._expected_txn_ids(txns)
        expected_batches=self._expected_batch_ids(batches)
        length_batches = len(expected_batches)
        length_transactions = len(expected_txns['trxn_id'])
        data['expected_batch_length'] = data['batch_length'] + length_batches
        data['expected_trn_length'] = data['transaction_length'] + length_transactions
        return data
        
    
    def _expected_data(self,txns,batches):
        LOGGER.info("Gathering expected data before submission of batches")
        data = self.data
        self._expected_count(txns,batches)
        expected_txns=self._expected_txn_ids(txns)
        expected_batches=self._expected_batch_ids(batches)
                
        data['expected_txns'] = expected_txns['trxn_id'][::-1]
        data['payload'] = expected_txns['payload'][::-1]
        data['expected_batches'] = expected_batches[::-1]
        data['signer_key'] = self.signer.get_public_key().as_hex()
        return data
    
    def _post_data(self,txns,batches):
        print("Gathering data post submission of batches")
        import time
        start_time = time.time()
        data = self.data
        expected_batches=self._expected_batch_ids(batches)
        batch_list = get_batches()
        data['batch_list'] = batch_list
        data['batch_ids'] = [batch['header_signature'] for batch in batch_list['data']]
        transaction_list = get_transactions()
        data['transaction_list'] = transaction_list
        data['transaction_ids'] = [trans['header_signature'] for trans in transaction_list['data']]
        block_list = get_blocks()
        data['block_list'] = block_list
        block_ids = [block['header_signature'] for block in block_list['data']]
        data['block_ids'] = block_ids[:-1]
        expected_head = block_ids[0]
        data['expected_head'] = expected_head
        state_addresses = [state['address'] for state in get_state_list()['data']]
        data['state_address'] = state_addresses
        state_head_list = [get_state_address(address)['head'] for address in state_addresses]
        data['state_head'] = state_head_list
        data['address'] = self.address
        data['limit'] = LIMIT
        data['start'] = expected_batches[::-1][0]
        return data


@pytest.fixture(scope="session")
def setup(request):
    """Setup method for posting batches and returning the 
       response
    """
    LOGGER.info("Starting Setup method for posting batches using intkey as payload")
    data = {}
    ctx = Setup() 
    tasks=[] 
    txns = ctx._create_transactions()
    batches = ctx._create_batches(txns)
    expected_data = ctx._expected_data(txns,batches)
    post_batch_list = ctx._create_batch_list(batches)    
    ctx._submit_batches(post_batch_list)
    data = ctx._post_data(txns,batches)
    data.update(expected_data)
    return data
                  
 
def pytest_addoption(parser):
    """Contains parsers for pytest cli commands
    """
    parser.addoption(
        "--get", action="store_true", default=False, help="run get tests"
    )
     
    parser.addoption(
        "--post", action="store_true", default=False, help="run post tests"
    )
     
    parser.addoption(
        "--sn", action="store_true", default=False, help="run scenario based tests"
    )
    
    parser.addoption("--batch", action="store", metavar="NAME",
        help="only run batch tests."
    )
    
    parser.addoption("--transaction", action="store", metavar="NAME",
        help="only run transaction tests."
    )
    
    parser.addoption("--state", action="store", metavar="NAME",
        help="only run state tests."
    )
    
    parser.addoption("--block", action="store", metavar="NAME",
        help="only run state tests."
    )
     
    parser.addoption("-E", action="store", metavar="NAME",
        help="only run tests matching the environment NAME."
    )
     
    parser.addoption("-N", action="store", metavar="NAME",
        help="only run tests matching the Number."
    )
     
    parser.addoption("-O", action="store", metavar="NAME",
        help="only run tests matching the OS release version."
    )

   
def pytest_collection_modifyitems(config, items):
    """Filters tests based on markers when parameters passed
       through the cli
    """
    try:
        num = int(config.getoption("-N"))
    except:
        num = None
 
    selected_items = []
    deselected_items = []
    if config.getoption("--get"):        
        for item in items:
            for marker in list(item.iter_markers()):
                if marker.name == 'get':
                    selected_items.append(item)
                else:
                    deselected_items.append(item)
 
        items[:] = selected_items[:num]
        return items
    elif config.getoption("--post"):   
        for item in items:
            for marker in item.iter_markers():
                if marker.name == 'post':
                    selected_items.append(item)
                else:
                    deselected_items.append(item)
  
        items[:] = selected_items[:num]
        return items
    elif config.getoption("--sn"):  
        for item in items:
            for marker in item.iter_markers():
                if marker.name == 'scenario':
                    selected_items.append(item)
                else:
                    deselected_items.append(item)
  
        items[:] = selected_items[:num]
        return items
    else:
        selected_items = items[:num]
        items[:] = selected_items
        return items