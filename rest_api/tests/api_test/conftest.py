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

from sawtooth_rest_api.protobuf.validator_pb2 import Message
from sawtooth_rest_api.protobuf import client_batch_submit_pb2
from sawtooth_rest_api.protobuf import client_batch_pb2
from sawtooth_rest_api.protobuf import client_list_control_pb2

from sawtooth_rest_api.protobuf.batch_pb2 import Batch
from sawtooth_rest_api.protobuf.batch_pb2 import BatchList
from sawtooth_rest_api.protobuf.batch_pb2 import BatchHeader
from sawtooth_rest_api.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_rest_api.protobuf.transaction_pb2 import Transaction

from google.protobuf.json_format import MessageToDict

from utils import get_batches,  get_transactions, get_state_address, post_batch, get_blocks,\
                  get_state_list , _delete_genesis , _start_validator, \
                  _stop_validator , _create_genesis , _get_client_address, \
                  _stop_settings_tp, _start_settings_tp, _get_client_address, batch_count, transaction_count,\
                  get_batch_statuses

from payload import get_signer, create_intkey_transaction , create_batch
                  

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


LIMIT = 100
                  
 
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

@pytest.fixture(scope="session", autouse=True)
def setup(request):
    """Setup method for posting batches and returning the 
       response
    """
    data = {}
    signer = get_signer()
    expected_trxns  = {}
    expected_batches = []
    transaction_list = []
    initial_state_length = len(get_state_list())
    initial_batch_length = batch_count()
    initial_transaction_length = transaction_count()
    address = _get_client_address()

    LOGGER.info("Creating intkey transactions with set operations")
    
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

    for batch in batches:
        dict = MessageToDict(
                batch,
                including_default_value_fields=True,
                preserving_proto_field_name=True)

        batch_id = dict['header_signature']
        expected_batches.append(batch_id)
    
    length_batches = len(expected_batches)
    length_transactions = len(expected_trxns)
        
    data['expected_batch_length'] = initial_batch_length + length_batches
    data['expected_trn_length'] = initial_transaction_length + length_transactions
    data['expected_txns'] = expected_trxns['trxn_id'][::-1]
    data['payload'] = expected_trxns['payload'][::-1]
    data['expected_batches'] = expected_batches[::-1]
    data['signer_key'] = signer.get_public_key().as_hex()
    
    post_batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]
    
    LOGGER.info("Submitting batches to the handlers")
    
    for batch in post_batch_list:
        try:
            response = post_batch(batch)
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is not reachable")
            response = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(response['error']['title'])
            LOGGER.info(response['error']['message'])
    
                
    block_list = get_blocks()
    data['block_list'] = block_list
    batch_list = get_batches()
    data['batch_list'] = batch_list
    transaction_list = get_transactions()
    data['transaction_list'] = transaction_list
    transaction_ids = [trans['header_signature'] for trans in transaction_list['data']]
    data['transaction_ids'] = transaction_ids
    block_ids = [block['header_signature'] for block in block_list['data']]
    data['block_ids'] = block_ids[:-1]
    batch_ids = [block['header']['batch_ids'][0] for block in block_list['data']]
    data['batch_ids'] = batch_ids
    expected_head = block_ids[0]
    data['expected_head'] = expected_head
    state_addresses = [state['address'] for state in get_state_list()['data']]
    data['state_address'] = state_addresses
    state_head_list = [get_state_address(address)['head'] for address in state_addresses]
    data['state_head'] = state_head_list
    data['address'] = address
    data['limit'] = LIMIT
    data['start'] = expected_batches[::-1][0]
    data['family_name']=[block['batches'][0]['transactions'][0]['header']['family_name'] for block in block_list['data']]
    return data