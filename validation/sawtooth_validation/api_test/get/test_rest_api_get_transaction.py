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
import aiohttp

from fixtures import break_genesis

from sawtooth_validation.utils import get_transactions, get_transaction_id

from sawtooth_validation.base import RestApiBaseTest

pytestmark = [pytest.mark.get , pytest.mark.transactions, pytest.mark.first]


  
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

START = 1
LIMIT = 1
COUNT = 0
BAD_HEAD = 'f'
BAD_ID = 'f'
INVALID_START = -1
INVALID_LIMIT = 0
INVALID_RESOURCE_ID  = 60
INVALID_PAGING_QUERY = 54
INVALID_COUNT_QUERY  = 53
VALIDATOR_NOT_READY  = 15
TRANSACTION_NOT_FOUND = 72
HEAD_LENGTH = 128
TIMEOUT=5
  

class TestTransactionList(RestApiBaseTest):
    async def test_api_get_transaction_list(self, setup):
        """Tests the transaction list after submitting intkey batches
        """
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_txns = setup['expected_txns']
        expected_length = setup['expected_trn_length']
        payload = setup['payload']
        address = setup['address']
        start = setup['start']
        limit = setup['limit']
        start = expected_txns[0]
         
        expected_link = '{}/transactions?head={}&start={}&limit={}'.format(address,\
                         expected_head, start, limit)
        
        paging_link = '{}/transactions?head={}&start={}'.format(address,\
                         expected_head, start)
           
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/transactions'.format(address), 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
                 
        txns = response['data'][:-1]
          
        self.assert_check_transaction_seq(txns, expected_txns, 
                                          payload, signer_key)
        self.assert_valid_head(response , expected_head)
        self.assert_valid_link(response, expected_link)
        self.assert_valid_paging(response, expected_link)
         
             
    async def test_api_get_transaction_list_head(self, setup):   
        """Tests that GET /transactions is reachable with head parameter 
        """
        LOGGER.info("Starting test for transactions with head parameter")
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_txns = setup['expected_txns']
        expected_length = setup['expected_trn_length']
        payload = setup['payload'][0]
        address = setup['address']
        start = expected_txns[0]
        limit = setup['limit']
         
        expected_link = '{}/transactions?head={}&start={}&limit={}'.format(address,\
                         expected_head, start, limit)
                          
        params={'head': expected_head}
                    
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/transactions'.format(address), params=params, 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
                              
        txns = response['data'][:-1]
          
        self.assert_check_transaction_seq(txns, expected_txns, 
                                          payload, signer_key)
        self.assert_valid_head(response , expected_head)
        self.assert_valid_link(response, expected_link)
        self.assert_valid_paging(response, expected_link)
           
    async def test_api_get_transaction_list_bad_head(self, setup):   
        """Tests that GET /transactions is unreachable with bad head parameter 
        """       
        LOGGER.info("Starting test for transactions with bad head parameter")
        address = setup['address']
        params={'head': BAD_HEAD}
                       
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/transactions'.format(address), params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
         
        self.assert_valid_error(response, INVALID_RESOURCE_ID)
                
    async def test_api_get_transaction_list_id(self, setup):   
        """Tests that GET /transactions is reachable with id as parameter 
        """
        LOGGER.info("Starting test for transactions with id parameter")
                       
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_txns = setup['expected_txns']
        expected_length = setup['expected_trn_length']
        payload = setup['payload'][0]
        address = setup['address']
        start = expected_txns[0]
        transaction_ids   =  setup['transaction_ids']
        expected_id = transaction_ids[0]
        expected_length = len([expected_id])
        limit = setup['limit']
         
        expected_link = '{}/transactions?head={}&start={}&limit={}&id={}'.format(address,\
                         expected_head, start, limit, expected_id)
                      
        params={'id': expected_id}
                    
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/transactions'.format(address), params=params, 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
                     
                     
        txns = response['data'][:-1]
          
        self.assert_check_transaction_seq(txns, expected_txns, 
                                          payload, signer_key) 
                 
    async def test_api_get_transaction_list_bad_id(self, setup):   
        """Tests that GET /transactions is unreachable with bad id parameter 
        """
        LOGGER.info("Starting test for transactions with bad id parameter")
        address = setup['address']
        params={'head': BAD_ID}
                          
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/transactions'.format(address), params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
         
        self.assert_valid_error(response, INVALID_RESOURCE_ID)
               
    async def test_api_get_transaction_list_head_and_id(self, setup):   
        """Tests GET /transactions is reachable with head and id as parameters 
        """
        LOGGER.info("Starting test for transactions with head and id parameter")
                       
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_txns = setup['expected_txns']
        expected_length = setup['expected_trn_length']
        payload = setup['payload'][0]
        address = setup['address']
        start = expected_txns[0]
        transaction_ids   =  setup['transaction_ids']
        expected_id = transaction_ids[0]
        expected_length = len([expected_id])
        limit = setup['limit']
                 
        expected_link = '{}/transactions?head={}&start={}&limit={}&id={}'.format(address,\
                         expected_head, start, limit, expected_id)
                                
        params={'head':expected_head,'id':expected_id}
                    
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/transactions'.format(address), params=params, 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
                     
                       
        txns = response['data'][:-1]
          
        self.assert_check_transaction_seq(txns, expected_txns, 
                                          payload, signer_key)
        self.assert_valid_head(response , expected_head)
                
    async def test_api_get_paginated_transaction_list(self, setup):   
        """Tests GET /transactions is reachable using paging parameters 
        """
        LOGGER.info("Starting test for transactions with paging parameters")
        address = setup['address']
        batch_ids   =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        start = 1
        limit = 1
                    
        params={'limit':1, 'start':1}
                          
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/transactions'.format(address), params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
          
        self.assert_valid_error(response, INVALID_PAGING_QUERY)
    
    async def test_api_get_transaction_list_limit(self, setup):   
        """Tests GET /batches is reachable using paging parameters 
        """
        LOGGER.info("Starting test for batch with paging parameters")
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_txns = setup['expected_txns']
        expected_length = setup['expected_trn_length']
        payload = setup['payload'][0]
        address = setup['address']
        start = expected_txns[0]
        transaction_ids   =  setup['transaction_ids']
        expected_id = transaction_ids[0]
        expected_length = len([expected_id])
        limit = setup['limit']
        
        params={'limit':1}
        
        expected_link = '{}/transactions?head={}&start={}&limit={}'.format(address,\
                         expected_head, start, 1)
                      
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/transactions'.format(address), params=params, 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
        
        
        txns = response['data'][:-1]
                                 
        self.assert_check_transaction_seq(txns, expected_txns, 
                                          payload, signer_key)
          
        self.assert_valid_head(response, expected_head)
        self.assert_valid_link(response, expected_link)
        self.assert_valid_paging(response, expected_link)
      
    async def test_api_get_transaction_bad_paging(self, setup):   
        """Tests GET /transactions is reachbale using bad paging parameters 
        """
        LOGGER.info("Starting test for transactions with bad paging parameters")
        address = setup['address']
        params = {'start':-1 , 'limit':-1}
                    
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/transactions'.format(address), params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
         
        self.assert_valid_error(response, INVALID_COUNT_QUERY)
                 
    async def test_api_get_transaction_list_invalid_start(self, setup):   
        """Tests that GET /transactions is unreachable with invalid start parameter 
        """
        LOGGER.info("Starting test for transactions with invalid start parameter")  
        address = setup['address']                     
        params = {'start':-1 }
                    
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/transactions'.format(address), params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
         
        self.assert_valid_error(response, INVALID_PAGING_QUERY)
          
    async def test_api_get_transaction_list_invalid_limit(self, setup):   
        """Tests that GET /transactions is unreachable with bad limit parameter 
        """
        LOGGER.info("Starting test for transactions with bad limit parameter")
        address = setup['address']                   
        params = {'limit': 0 }
                    
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/transactions'.format(address), params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
         
        self.assert_valid_error(response, INVALID_COUNT_QUERY)
      
                     
    async def test_api_get_transaction_list_reversed(self, setup):   
        """verifies that GET /transactions with list reversed
        """
        LOGGER.info("Starting test for transactions with list reversed")
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_txns = setup['expected_txns']
        expected_length = setup['expected_trn_length']
        payload = setup['payload'][0]
        address = setup['address']
        start = expected_txns[::-1][0]
        transaction_ids   =  setup['transaction_ids']
        expected_id = transaction_ids[0]
        expected_length = len([expected_id])
        limit = setup['limit']
        expected_link = '{}/transactions?head={}&start={}&limit={}'.format(address,\
                         expected_head, start, limit)
         
        params = 'reverse'
                         
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/transactions'.format(address), params=params, 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
                        
        assert response['paging']['start'] == None ,  "request is not correct"
        assert response['paging']['limit'] == None ,  "request is not correct"
        assert bool(response['data']) == True
    
    async def test_api_get_transactions_link_val(self, setup):
        """Tests/ validate the transactions parameters with transactions, head, start and limit
        """
        address = setup['address']
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/transactions'.format(address), raise_for_status=True) as data:
                    response = await data.json()
                    
            for link in response:
                if(link == 'link'):
                    assert 'head' in response['link']
                    assert 'start' in response['link']  
                    assert 'limit' in response['link'] 
                    assert 'transactions' in response['link']  
        except urllib.error.HTTPError as error:
            assert response.code == 400
            LOGGER.info("Link is not proper for transactions and parameters are missing")
    
    async def test_api_get_transactions_key_params(self, setup):
        """Tests/ validate the state key parameters with data, head, link and paging               
        """
        address = setup['address']
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/transactions'.format(address), raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
        
        assert 'link' in response
        assert 'data' in response
        assert 'paging' in response
        assert 'head' in response
    
    async def test_api_get_transaction_id_length(self, setup):
        """Tests the transaction id length should be 128 hex character long 
        """  
        address = setup['address'] 
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/transactions'.format(address), raise_for_status=True) as data:
                    response = await data.json()
            
            for trans in response['data']:
                transaction_ids = trans['header_signature']
                head_len = len(transaction_ids)
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Transaction id length is not 128 hex character long")
        assert head_len == HEAD_LENGTH
    
    async def test_rest_api_check_transactions_count(self, setup):
        """Tests transaction count from transaction list 
        """
        address = setup['address']
        count =0
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/transactions'.format(address), raise_for_status=True) as data:
                    response = await data.json()
                    
            for trans in enumerate(response['data']):
                count = count+1
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Transaction count not able to collect")
    
class TestTransactionGet(RestApiBaseTest):
    async def test_api_get_transaction_id(self, setup):
        """Tests that GET /transactions/{transaction_id} is reachable 
        """
        LOGGER.info("Starting test for transaction/{transaction_id}")
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_txns = setup['expected_txns']
        expected_id = expected_txns[0]
        address = setup['address']
        payload = setup['payload']
        expected_length = 1
        
        expected_link = '{}/transactions/{}'.format(address,expected_id)
                         
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/transactions/{}'.format(address,expected_id), 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
                                      
        txns = response['data']
        
        self.assert_check_transaction_seq(txns, expected_txns, 
                                          payload, signer_key)
        self.assert_valid_link(response, expected_link)   
          
    async def test_api_get_transaction_bad_id(self, setup):
        """Tests that GET /transactions/{transaction_id} is not reachable
           with bad id
        """
        LOGGER.info("Starting test for transactions/{bad_id}")
        address = setup['address']
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/transactions/{}'.format(address,BAD_ID)) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
          
        self.assert_valid_error(response, INVALID_RESOURCE_ID)

