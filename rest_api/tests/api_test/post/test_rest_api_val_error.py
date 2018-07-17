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
import asyncio
import os

from aiohttp import web
from zmq.asyncio import ZMQEventLoop

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_rest_api.messaging import Connection

from sawtooth_rest_api.protobuf.validator_pb2 import Message
from sawtooth_rest_api.protobuf import client_batch_submit_pb2
from sawtooth_rest_api.protobuf import client_batch_pb2
from sawtooth_rest_api.protobuf import client_list_control_pb2

from sawtooth_rest_api.protobuf.batch_pb2 import Batch
from sawtooth_rest_api.protobuf.batch_pb2 import BatchList
from sawtooth_rest_api.protobuf.batch_pb2 import BatchHeader
from sawtooth_rest_api.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_rest_api.protobuf.transaction_pb2 import Transaction

from google.protobuf.message import DecodeError
from google.protobuf.json_format import MessageToDict


CONNECTION_URL = "tcp://127.0.0.1:4004"
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

INTKEY_ADDRESS_PREFIX = hashlib.sha512(
    'intkey'.encode('utf-8')).hexdigest()[0:6]

BLOCK_TO_CHECK_CONSENSUS = 1
WAIT=10

def test_rest_invalid_batch():
    """Tests that transactions are submitted and committed for
    each block that are created by submitting intkey batches
    """    
    signer = get_signer()
    
    txns = [
        create_intkey_transaction("set", 'a', 0, [], signer), 
        create_intkey_transaction("set", 'a', 0, [], signer), 
    ]
        
    batches = [create_batch([txn], signer) for txn in txns]
     
    batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]        
    batches = [create_invalid_batch("bad_batch", "bad_txn")]
    print(batches)
       
    batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]
    print(batch_list)
       
    try:
        for batch in batch_list:
            response = post_batch(batch)
    except urllib.error.HTTPError as error:
        print(error.code)
        data = json.loads(error.fp.read().decode('utf-8'))
        LOGGER.info(data['error']['title'])
        LOGGER.info(data['error']['message'])
        assert data['error']['code'] == 34

def test_rest_validator_503_err_17():
    """Tests for validator error 17 request timed out
    """    
    batches = make_batches('abcd')
    try:
        for batch in batches:
            response = post_batch(batch)
    except urllib.error.HTTPError as error:
           
        data = json.loads(error.fp.read().decode('utf-8'))
        LOGGER.info(data['error']['title'])
        LOGGER.info(data['error']['message'])
        assert data['error']['code'] == 17
    
def test_rest_validator_503_err_18():
    """Tests for validator error 18 validator 
        disconnected before sending a response
    """    
    batches = make_batches('abcd')
    try:
        for batch in batches:
            response = post_batch(batch , stop=1)
    except urllib.error.HTTPError as error:
        data = json.loads(error.fp.read().decode('utf-8'))
        LOGGER.info(data['error']['title'])
        LOGGER.info(data['error']['message'])
        assert data['error']['code'] == 18
        assert error.code == 503
 
def test_rest_api_post_no_genesis():
    """Tests two same intkey transaction in two different batches
    """    
    signer = get_signer()
       
    txns = [
        create_intkey_transaction("set", 'a', 0, [], signer), 
        create_intkey_transaction("set", 'a', 0, [], signer), 
    ]
       
    batches = [create_batch([txn], signer) for txn in txns]
   
    batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]
  
    try:
        for batch in batch_list:
            response = post_batch(batch)
        batches = get_batches()             
    except urllib.error.HTTPError as error:
        data = json.loads(error.fp.read().decode('utf-8'))
        LOGGER.info(data['error']['title'])
        LOGGER.info(data['error']['message'])
        assert error.code == 503
        assert data['error']['code'] == 15
          
    except:
        Logger.info("unable to connect rest api")
 
 
@pytest.mark.asyncio
async def test_rest_validator_invalid_batch(event_loop):
    """Tests for validator error 18 validator 
        disconnected before sending a response
    """    
    loop = ZMQEventLoop()
    asyncio.set_event_loop(loop)
       
    connection = Connection(CONNECTION_URL)
       
    connection.open()
       
    signer = get_signer()
       
    txns = [
        create_intkey_transaction("set", 'a', 0, [], signer)        
    ]
       
    invalid_batches = [
        create_invalid_batch([txn], signer)
        for txn in txns
    ]
           
    invalid_batch_list = BatchList(batches=invalid_batches)
    print(invalid_batch_list)
       
    query = client_batch_submit_pb2.ClientBatchSubmitRequest(
            batches=invalid_batch_list.batches)
               
    payload  = query.SerializeToString()
     
 
    response =  loop.run_until_complete(connection.send(
                message_type=Message.CLIENT_BATCH_SUBMIT_REQUEST,
                message_content=payload,
                timeout=1))
    print(response)
   
    content = client_batch_submit_pb2.ClientBatchSubmitResponse()
    data = content.ParseFromString(response.content)
    data = MessageToDict(
            content,
            including_default_value_fields=True,
            preserving_proto_field_name=True)
    print(data)
   


@pytest.mark.asyncio
async def test_rest_validator_no_genesis(event_loop):
    """Tests for validator error 18 validator 
        disconnected before sending a response
    """    
    loop = ZMQEventLoop()
    asyncio.set_event_loop(loop)
       
    connection = Connection(CONNECTION_URL)
       
    connection.open()
       
    signer = get_signer()
       
    txns = [
        create_intkey_transaction("set", 'a', 0, [], signer)        
    ]
       
    batches = [
        create_batch([txn], signer)
        for txn in txns
    ]
     
    invalid_batches = [
        create_invalid_batch([txn], signer)
        for txn in txns
    ]
       
    batch_list = BatchList(batches=batches)
     
       
    query = client_batch_submit_pb2.ClientBatchSubmitRequest(
            batches=batch_list.batches)
               
    payload  = query.SerializeToString()
       
    response =  loop.run_until_complete(connection.send(
                message_type=Message.CLIENT_BATCH_SUBMIT_REQUEST,
                message_content=payload2,
                timeout=1))
       
    content = client_batch_submit_pb2.ClientBatchSubmitResponse()
    data = content.ParseFromString(response.content)
    data = MessageToDict(
            content,
            including_default_value_fields=True,
            preserving_proto_field_name=True)
    print(data)
       
       
    paging_controls = client_list_control_pb2.ClientPagingControls(
                start=None,
                limit=None)
                     
         
    query2 = client_batch_pb2.ClientBatchListRequest(
                            head_id=None, 
                            batch_ids=None , 
                            sorting=[], 
                            paging= paging_controls)
    payload = query2.SerializeToString()
    response =  loop.run_until_complete(connection.send(
                message_type=Message.CLIENT_BATCH_LIST_REQUEST,
                message_content=payload,
                timeout=1))
    content = client_batch_pb2.ClientBatchListResponse()
    data = content.ParseFromString(response.content)
    data = MessageToDict(
            content,
            including_default_value_fields=True,
            preserving_proto_field_name=True)
    print(data)
         
    data = MessageToDict(
            content,
            including_default_value_fields=True,
            preserving_proto_field_name=True)
   
    connection.close()
