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
import hashlib


import asyncio

from aiohttp import web
from zmq.asyncio import ZMQEventLoop

from sawtooth_rest_api.messaging import Connection

from google.protobuf.message import DecodeError
from google.protobuf.json_format import MessageToDict



CONNECTION_URL = "tcp://127.0.0.1:4004"
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

INTKEY_ADDRESS_PREFIX = hashlib.sha512(
    'intkey'.encode('utf-8')).hexdigest()[0:6]

BLOCK_TO_CHECK_CONSENSUS = 1

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
    
    batch_list = BatchList(batches=batches)
    
    query = client_batch_submit_pb2.ClientBatchSubmitRequest(
            batches=batch_list.batches)
            
    payload = query.SerializeToString()
    
    response =  loop.run_until_complete(connection.send(
                message_type=Message.CLIENT_BATCH_SUBMIT_REQUEST,
                message_content=payload,
                timeout=1))
    
    response_proto = client_batch_submit_pb2.ClientBatchSubmitResponse()
    content = response_proto.ParseFromString(response.content)
    
    
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
    print(response)
    content = client_batch_pb2.ClientBatchListResponse()
    data = content.ParseFromString(response.content)
    
    data = MessageToDict(
            content,
            including_default_value_fields=True,
            preserving_proto_field_name=True)
    print(data)

    connection.close()
             

 