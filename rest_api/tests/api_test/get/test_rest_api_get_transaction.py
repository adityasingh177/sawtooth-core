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

from utils import get_transactions, get_transaction

from base import RestApiBaseTest

pytestmark = [pytest.mark.get , pytest.mark.transactions]

  
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

INVALID_RESOURCE_ID  = 60
INVALID_PAGING_QUERY = 54
INVALID_COUNT_QUERY  = 53
VALIDATOR_NOT_READY  = 15
  

class TestTransactionList(RestApiBaseTest):
    def test_api_get_transaction_list(self, setup):
        """Tests the transaction list after submitting intkey batches
        """
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_txns = setup['expected_txns']
        expected_length = setup['expected_length']
        payload = setup['payload'][0]
         
        try:   
            response = get_transactions()
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is Unreachable")
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
               
        txns = response['data'][:-1]
        
        self.assert_valid_data_list(response, expected_length)         
        self.assert_check_transaction_seq(txns, expected_txns, 
                                          payload, signer_key)
        self.assert_valid_head(response , expected_head)
        
        
    #     def test_api_get_transaction_list_invalid_batch(self, invalid_batch):
#         """Tests that transactions are submitted and committed for
#         each block that are created by submitting invalid intkey batches
#         """    
#         batch= invalid_batch[0]
#         try:
#             response = post_batch(batch)
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#             assert data['error']['code'] == 34
#            
#     def test_api_get_transaction_list_head(self, setup):   
#         """Tests that GET /transactions is reachable with head parameter 
#         """
#         LOGGER.info("Starting test for transactions with head parameter")
#         expected_head = setup['expected_head']
#                 
#         try:
#             response = get_transactions(head_id=expected_head)
#         except  urllib.error.HTTPError as error:
#             LOGGER.info("Rest Api not reachable")
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#                 
#         assert response['head'] == expected_head , "request is not correct"
#          
#     def test_api_get_transaction_list_bad_head(self, setup):   
#         """Tests that GET /transactions is unreachable with bad head parameter 
#         """       
#         LOGGER.info("Starting test for transactions with bad head parameter")
#         bad_head = 'f' 
#                      
#         try:
#             batch_list = get_transactions(head_id=bad_head)
#         except urllib.error.HTTPError as error:
#             LOGGER.info("Rest Api is not reachable")
#             data = json.loads(error.fp.read().decode('utf-8'))
#             if data:
#                 LOGGER.info(data['error']['title'])
#                 LOGGER.info(data['error']['message'])
#                 assert data['error']['code'] == 60
#                 assert data['error']['title'] == 'Invalid Resource Id'
#               
#     def test_api_get_transaction_list_id(self, setup):   
#         """Tests that GET /transactions is reachable with id as parameter 
#         """
#         LOGGER.info("Starting test for transactions with id parameter")
#                      
#         batch_ids   =  setup['batch_ids']
#         expected_head = setup['expected_head']
#         expected_id = batch_ids[0]
#                     
#         try:
#             response = get_transactions(id=expected_id)
#         except:
#             LOGGER.info("Rest Api is not reachable")
#                    
#                    
#         assert response['head'] == expected_head, "request is not correct"
#         assert response['paging']['start'] == None , "request is not correct"
#         assert response['paging']['limit'] == None , "request is not correct"
#                
#     def test_api_get_transaction_list_bad_id(self, setup):   
#         """Tests that GET /transactions is unreachable with bad id parameter 
#         """
#         LOGGER.info("Starting test for transactions with bad id parameter")
#         bad_id = 'f' 
#                      
#         try:
#             batch_list = get_transactions(head_id=bad_id)
#         except urllib.error.HTTPError as error:
#             LOGGER.info("Rest Api is not reachable")
#             data = json.loads(error.fp.read().decode('utf-8'))
#             if data:
#                 LOGGER.info(data['error']['title'])
#                 LOGGER.info(data['error']['message'])
#                 assert data['error']['code'] == 60
#                 assert data['error']['title'] == 'Invalid Resource Id'
#              
#     def test_api_get_transaction_list_head_and_id(self, setup):   
#         """Tests GET /transactions is reachable with head and id as parameters 
#         """
#         LOGGER.info("Starting test for transactions with head and id parameter")
#         batch_ids =  setup['batch_ids']
#         expected_head = setup['expected_head']
#         expected_id = batch_ids[0]
#                       
#                
#         response = get_transactions(head_id=expected_head , id=expected_id)
#                      
#         assert response['head'] == expected_head , "head is not matching"
#         assert response['paging']['start'] == None ,  "start parameter is not correct"
#         assert response['paging']['limit'] == None ,  "request is not correct"               
#               
#     def test_api_get_paginated_transaction_list(self, setup):   
#         """Tests GET /transactions is reachbale using paging parameters 
#         """
#         LOGGER.info("Starting test for transactions with paging parameters")
#         batch_ids   =  setup['batch_ids']
#         expected_head = setup['expected_head']
#         expected_id = batch_ids[0]
#         start = 1
#         limit = 1
#                   
#         try:
#             response = get_transactions(start=start , limit=limit)
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#             assert data['error']['code'] == 54
#     
#     def test_api_get_transaction_bad_paging(self, setup):   
#         """Tests GET /transactions is reachbale using bad paging parameters 
#         """
#         LOGGER.info("Starting test for transactions with bad paging parameters")
#         batch_ids   =  setup['batch_ids']
#         expected_head = setup['expected_head']
#         expected_id = batch_ids[0]
#         start = -1
#         limit = -1
#                   
#         try:
#             response = get_transactions(start=start , limit=limit)
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#             assert data['error']['code'] == 53
#                
#     def test_api_get_transaction_list_invalid_start(self, setup):   
#         """Tests that GET /transactions is unreachable with invalid start parameter 
#         """
#         LOGGER.info("Starting test for transactions with invalid start parameter")
#         batch_ids   =  setup['batch_ids']
#         expected_head = setup['expected_head']
#         expected_id = batch_ids[0]
#         start = -1
#                        
#         try:  
#             response = get_transactions(start=start)
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#             assert data['error']['code'] == 54
#         
#     def test_api_get_transaction_list_invalid_limit(self, setup):   
#         """Tests that GET /transactions is unreachable with bad limit parameter 
#         """
#         LOGGER.info("Starting test for transactions with bad limit parameter")
#         batch_ids = setup['batch_ids']
#         expected_head = setup['expected_head']
#         expected_id = batch_ids[0]
#         limit = 0
#                    
#         try:  
#             response = get_transactions(limit=limit)
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#             assert data['error']['code'] == 53
#     
#     def test_api_get_transaction_list_count(self, setup):   
#         """Tests that GET /transactions with count parameter 
#         """
#         LOGGER.info("Starting test for transactions with count parameter")
#         batch_ids =  setup['batch_ids']
#         expected_head = setup['expected_head']
#         expected_id = batch_ids[0]
#         count = 1
#                    
#         try:  
#             response = get_transactions(count=count)
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#         
#         assert response['head'] == expected_head , "head is not matching"
#         assert response['paging']['start'] == None ,  "start parameter is not correct"
#         assert response['paging']['limit'] == None ,  "request is not correct"
#   
#     def test_api_get_transaction_list_no_count(self, setup):   
#         """Tests that GET /transactions with no count parameter 
#         """
#         LOGGER.info("Starting test for transactions with no count parameter")
#         batch_ids =  setup['batch_ids']
#         expected_head = setup['expected_head']
#         expected_id = batch_ids[0]
#         count = 0
#                    
#         try:  
#             response = get_transactions(count=count)
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#             assert data['error']['code'] == 53
#                    
#     def test_api_get_transaction_list_reversed(self, setup):   
#         """verifies that GET /transactions with list reversed
#         """
#         LOGGER.info("Starting test for transactions with list reversed")
#         batch_ids = setup['batch_ids']
#         expected_head = setup['expected_head']
#         expected_id = batch_ids[0]
#         reverse = True
#                        
#         try:
#             response = get_transactions(reverse=reverse)
#         except urllib.error.HTTPError as error:
#             assert response.code == 400
#                       
#         assert response['head'] == expected_head , "request is not correct"
#         assert response['paging']['start'] == None ,  "request is not correct"
#         assert response['paging']['limit'] == None ,  "request is not correct"
#         assert bool(response['data']) == True
#  
# #     def test_api_get_transaction_list_bad_protobufs(self):
# #          """Verifies requests for lists of transactions break with bad protobufs.
# #   
# #          Expects to find:
# #              - a status of INTERNAL_ERROR
# #              - that head_id, paging, and transactions are missing
# #          """
# #          response = self.make_bad_request(head_id=B_1)
# #   
# #          self.assertEqual(self.status.INTERNAL_ERROR, response.status)
# #          self.assertFalse(response.head_id)
# #          self.assertFalse(response.paging.SerializeToString())
# #          self.assertFalse(response.batches)
# # 
# #     @pytest.mark.usefixtures('break_genesis')
# #     def test_api_get_transaction_list_no_genesis(self , break_genesis):
# #         """Verifies requests for lists of batches breaks with no genesis.
# #    
# #          Expects to find:
# #              - a status of NOT_READY
# #         """
# #         try:
# #             response = get_transactions()
# #         except urllib.error.HTTPError as error:
# #             data = json.loads(error.fp.read().decode('utf-8'))
# #             LOGGER.info(data['error']['title'])
# #             LOGGER.info(data['error']['message'])
# #             assert data['error']['code'] == 15
# #  
# #     @pytest.mark.usefixtures('setup_settings_tp')
# #     def test_api_get_transaction_list_no_settings_tp(self , setup_settings_tp):
# #         try:
# #             response = get_transactions()
# #         except urllib.error.HTTPError as error:
# #             data = json.loads(error.fp.read().decode('utf-8'))
# #             LOGGER.info(data['error']['title'])
# #             LOGGER.info(data['error']['message'])
# #             assert data['error']['code'] == 15
# 
# class TesttransactionGet():
#     def test_api_get_transaction_id(self, setup):
#         """Tests that GET /transactions/{transaction_id} is reachable 
#         """
#         LOGGER.info("Starting test for transaction/{transaction_id}")
#         expected_head = setup['expected_head']
#         transaction_id = setup['transaction_ids'][0]
#                         
# #         try:
#         response = get_transaction(transaction_id=transaction_id)
#         print(response)
# #         except  urllib.error.HTTPError as error:
# #             LOGGER.info("Rest Api not reachable")
# #             data = json.loads(error.fp.read().decode('utf-8'))
# #             LOGGER.info(data['error']['title'])
# #             LOGGER.info(data['error']['message'])
#                 
#         assert response['head'] == expected_head , "request is not correct"
#    
#          
#     def test_api_get_bad_transaction_bad_id(self, setup):
#         """Tests that GET /transactions/{transaction_id} is not reachable
#            with bad id
#         """
#         LOGGER.info("Starting test for transactions/{transaction_id}")
#         expected_head = setup['expected_head']
#         transaction_id = 'f'
#                 
#         try:
#             response = get_transaction(transaction_id=transaction_id)
#         except  urllib.error.HTTPError as error:
#             LOGGER.info("Rest Api not reachable")
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#                 
#         
#     