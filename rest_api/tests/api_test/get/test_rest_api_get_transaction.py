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

from fixtures import break_genesis

from utils import get_transactions, get_transaction_id

from base import RestApiBaseTest

pytestmark = [pytest.mark.get , pytest.mark.transactions]

  
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
  

class TestTransactionList(RestApiBaseTest):
    def test_api_get_transaction_list(self, setup):
        """Tests the transaction list after submitting intkey batches
        """
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_txns = setup['expected_txns']
        expected_length = setup['expected_trn_length']
        payload = setup['payload'][0]
        address = setup['address']
        start = expected_txns[::-1][0]
         
        expected_link = '{}/transactions?head={}&start={}&limit={}'.format(address,\
                         expected_head, start, LIMIT)
           
        try:   
            response = get_transactions()
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is Unreachable")
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
                 
        txns = response['data'][:-1]
          
#         self.assert_check_transaction_seq(txns, expected_txns, 
#                                           payload, signer_key)
#         self.assert_valid_head(response , expected_head)
#         self.assert_valid_paging(response)
         
             
    def test_api_get_transaction_list_head(self, setup):   
        """Tests that GET /transactions is reachable with head parameter 
        """
        LOGGER.info("Starting test for transactions with head parameter")
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_txns = setup['expected_txns']
        expected_length = setup['expected_trn_length']
        payload = setup['payload'][0]
        address = setup['address']
        start = expected_txns[::-1][0]
         
        expected_link = '{}/transactions?head={}&start={}&limit={}'.format(address,\
                         expected_head, start, LIMIT)
                          
        try:
            response = get_transactions(head_id=expected_head)
        except  urllib.error.HTTPError as error:
            LOGGER.info("Rest Api not reachable")
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
                              
        txns = response['data'][:-1]
          
        self.assert_check_transaction_seq(txns, expected_txns, 
                                          payload, signer_key)
        self.assert_valid_head(response , expected_head)
           
    def test_api_get_transaction_list_bad_head(self, setup):   
        """Tests that GET /transactions is unreachable with bad head parameter 
        """       
        LOGGER.info("Starting test for transactions with bad head parameter")
                       
        try:
            response = get_transactions(head_id=BAD_HEAD)
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is not reachable")
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
         
        self.assert_valid_error(data, INVALID_RESOURCE_ID)
                
    def test_api_get_transaction_list_id(self, setup):   
        """Tests that GET /transactions is reachable with id as parameter 
        """
        LOGGER.info("Starting test for transactions with id parameter")
                       
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
         
        expected_link = '{}/transactions?head={}&start={}&limit={}&id={}'.format(address,\
                         expected_head, start, LIMIT, expected_id)
                      
        try:
            response = get_transactions(id=expected_id)
        except:
            LOGGER.info("Rest Api is not reachable")
                     
                     
        txns = response['data'][:-1]
          
        self.assert_check_transaction_seq(txns, expected_txns, 
                                          payload, signer_key) 
                 
    def test_api_get_transaction_list_bad_id(self, setup):   
        """Tests that GET /transactions is unreachable with bad id parameter 
        """
        LOGGER.info("Starting test for transactions with bad id parameter")
        bad_id = 'f' 
                       
        try:
            response = get_transactions(head_id=bad_id)
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is not reachable")
            data = json.loads(error.fp.read().decode('utf-8'))
         
        self.assert_valid_error(data, INVALID_RESOURCE_ID)
               
    def test_api_get_transaction_list_head_and_id(self, setup):   
        """Tests GET /transactions is reachable with head and id as parameters 
        """
        LOGGER.info("Starting test for transactions with head and id parameter")
                       
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
                 
        expected_link = '{}/transactions?head={}&start={}&limit={}&id={}'.format(address,\
                         expected_head, start, LIMIT, expected_id)
                                
        try:       
            response = get_transactions(head_id=expected_head , id=expected_id)
        except:
            LOGGER.info("Rest Api not reachable")
                     
                       
        txns = response['data'][:-1]
          
        self.assert_check_transaction_seq(txns, expected_txns, 
                                          payload, signer_key)
        self.assert_valid_head(response , expected_head)
                
    def test_api_get_paginated_transaction_list(self, setup):   
        """Tests GET /transactions is reachbale using paging parameters 
        """
        LOGGER.info("Starting test for transactions with paging parameters")
        batch_ids   =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        start = 1
        limit = 1
                    
        try:
            response = get_transactions(start=start , limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
         
        self.assert_valid_error(data, INVALID_PAGING_QUERY)
      
    def test_api_get_transaction_bad_paging(self, setup):   
        """Tests GET /transactions is reachbale using bad paging parameters 
        """
        LOGGER.info("Starting test for transactions with bad paging parameters")
        batch_ids   =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        start = -1
        limit = -1
                    
        try:
            response = get_transactions(start=start , limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
         
        self.assert_valid_error(data, INVALID_COUNT_QUERY)
                 
    def test_api_get_transaction_list_invalid_start(self, setup):   
        """Tests that GET /transactions is unreachable with invalid start parameter 
        """
        LOGGER.info("Starting test for transactions with invalid start parameter")
        batch_ids   =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        start = -1
                         
        try:  
            response = get_transactions(start=start)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
         
        self.assert_valid_error(data, INVALID_PAGING_QUERY)
          
    def test_api_get_transaction_list_invalid_limit(self, setup):   
        """Tests that GET /transactions is unreachable with bad limit parameter 
        """
        LOGGER.info("Starting test for transactions with bad limit parameter")
        batch_ids = setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        limit = 0
                     
        try:  
            response = get_transactions(limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
         
        self.assert_valid_error(data, INVALID_COUNT_QUERY)
      
                     
    def test_api_get_transaction_list_reversed(self, setup):   
        """verifies that GET /transactions with list reversed
        """
        LOGGER.info("Starting test for transactions with list reversed")
        batch_ids = setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        reverse = True
                         
        try:
            response = get_transactions(reverse=reverse)
        except urllib.error.HTTPError as error:
            assert response.code == 400
                        
        assert response['paging']['start'] == None ,  "request is not correct"
        assert response['paging']['limit'] == None ,  "request is not correct"
        assert bool(response['data']) == True
    
    def test_api_get_transactions_link_val(self, setup):
        """Tests/ validate the transactions parameters with transactions, head, start and limit
        """
        try:
            transactions_list = get_transactions()
            for link in transactions_list:
                if(link == 'link'):
                    assert 'head' in transactions_list['link']
                    assert 'start' in transactions_list['link']  
                    assert 'limit' in transactions_list['link'] 
                    assert 'transactions' in transactions_list['link']  
        except urllib.error.HTTPError as error:
            assert response.code == 400
            LOGGER.info("Link is not proper for transactions and parameters are missing")
    
    def test_api_get_transactions_key_params(self, setup):
        """Tests/ validate the state key parameters with data, head, link and paging               
        """
        response = get_transactions()
        assert 'link' in response
        assert 'data' in response
        assert 'paging' in response
        assert 'head' in response
    
    def test_api_get_transaction_id_length(self, setup):
        """Tests the transaction id length should be 128 hex character long 
        """   
        try:
            transaction_list = get_transactions()
            for trans in transaction_list['data']:
                transaction_ids = trans['header_signature']
                head_len = len(transaction_ids)
        except urllib.error.HTTPError as error:
            LOGGER.info("Transaction id length is not 128 hex character long")
        assert head_len == HEAD_LENGTH
    
    def test_rest_api_check_transactions_count(self, setup):
        """Tests transaction count from transaction list 
        """
        count =0
        try:
            batch_list = get_transactions()
            for batch in enumerate(batch_list['data']):
                count = count+1
        except urllib.error.HTTPError as error:
            LOGGER.info("Transaction count not able to collect")
    
class TesttransactionGet(RestApiBaseTest):
    def test_api_get_transaction_id(self, setup):
        """Tests that GET /transactions/{transaction_id} is reachable 
        """
        LOGGER.info("Starting test for transaction/{transaction_id}")
        expected_head = setup['expected_head']
        expected_id = setup['transaction_ids'][0]
        address = setup['address']
        expected_length = 1
        
        expected_link = '{}/transactions/{}'.format(address,expected_id)
                         
        try:
            response = get_transaction_id(transaction_id=expected_id)
        except  urllib.error.HTTPError as error:
            LOGGER.info("Rest Api not reachable")
            response = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(response['error']['title'])
            LOGGER.info(response['error']['message']) 
        
        self.assert_valid_link(response, expected_link)  
        assert bool(response['data']) == True   
          
    def test_api_get_transaction_bad_id(self, setup):
        """Tests that GET /transactions/{transaction_id} is not reachable
           with bad id
        """
        LOGGER.info("Starting test for transactions/{transaction_id}")
        try:
            response = get_transaction_id(transaction_id=BAD_ID)
        except  urllib.error.HTTPError as error:
            LOGGER.info("Rest Api not reachable")
            response = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(response['error']['title'])
            LOGGER.info(response['error']['message'])
        
        self.assert_valid_error(response, INVALID_RESOURCE_ID)

                 
         
     