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
#   
import pytest
import logging
import json
import urllib.request
import urllib.error
import aiohttp
  
from sawtooth_validation.utils import get_state_list, get_reciepts, post_receipts
from sawtooth_validation.base import RestApiBaseTest
  
  
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
  
pytestmark = [pytest.mark.get , pytest.mark.receipts, pytest.mark.fifth]

RECEIPT_NOT_FOUND = 80
RECEIPT_WRONG_CONTENT_TYPE = 81
RECEIPT_BODY_INVALID = 82
RECEIPT_Id_QUERYINVALID = 83
INVALID_RESOURCE_ID = 60
TIMEOUT=5
  
  
class TestReceiptsList(RestApiBaseTest):
    """This class tests the receipt list with different parameters
    """
    async def test_api_get_reciept_invalid_id(self,setup):
        """Tests the reciepts after submitting invalid transaction
        """
        address = setup['address']  
        transaction_id="s"
        params={'id':transaction_id}
        
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/receipts'.format(address),params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
        
        self.assert_valid_error(response, INVALID_RESOURCE_ID)
                 
    async def test_api_get_reciepts_multiple_transactions(self, setup):
        """Test the get reciepts for multiple transaction.
        """
        transaction_list=""
        expected_txns = setup['expected_txns']
        address = setup['address']  
        print(expected_txns)
        
        for txn in expected_txns:
            transaction_list=txn+","+transaction_list
         
        trans_list = str(transaction_list)[:-1]
        params={'id':trans_list}
        
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/receipts'.format(address),params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
        
         
        for res,txn in zip(response['data'],reversed(expected_txns)):
           assert str(res['id']) == txn
            
    async def test_api_get_reciepts_single_transactions(self,setup):
        """Tests get reciepts response for single transaction"""
         
        expected_transaction=setup['expected_txns']
        address = setup['address']
        transaction_id=str(expected_transaction)[2:-2]
        params={'id':transaction_id}
        
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/receipts'.format(address),params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
         
    async def test_api_post_reciepts_single_transactions(self,setup):
      """Test post reciepts response for single transaction"""
          
      expected_transaction=setup['expected_txns']
      address = setup['address']
      transaction_json=json.dumps(expected_transaction).encode()      
      headers = {'content-type': 'application/json'}
        
      try:
        async with aiohttp.ClientSession() as session:        
            async with session.post(url='{}/receipts'.format(address),
                                    data=transaction_json,headers=headers) as data:
                response = await data.json()
      except aiohttp.client_exceptions.ClientResponseError as error:
        LOGGER.info(error)
      
            
    async def test_api_post_reciepts_invalid_transactions(self,setup):
      """test reciepts post for invalid transaction"""
          
      expected_transaction="few"
      address = setup['address']
      transaction_json=json.dumps(expected_transaction).encode()
      headers = {'content-type': 'application/json'}
      
      try:
        async with aiohttp.ClientSession() as session:        
            async with session.post(url='{}/receipts'.format(address),
                                    data=transaction_json,headers=headers) as data:
                response = await data.json()
      except aiohttp.client_exceptions.ClientResponseError as error:
        LOGGER.info(error)
          
    async def test_api_post_reciepts_multiple_transactions(self, setup):
       """Test the post reciepts response for multiple transaction.
       """
       address = setup['address']
       expected_txns = setup['expected_txns']
       json_list=json.dumps(expected_txns).encode() 
       headers = {'content-type': 'application/json'}

       try:
        async with aiohttp.ClientSession() as session:        
            async with session.post(url='{}/receipts'.format(address),
                                    data=json_list,headers=headers) as data:
                response = await data.json()
       except aiohttp.client_exceptions.ClientResponseError as error:
        LOGGER.info(error)
           
       for res,txn in zip(response['data'], expected_txns):
           assert str(res['id']) == txn