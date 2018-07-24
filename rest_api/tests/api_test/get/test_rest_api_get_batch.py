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

 
from fixtures import break_genesis, invalid_batch
from utils import get_batches, post_batch

from base import RestApiBaseTest


pytestmark = [pytest.mark.get , pytest.mark.batch]

  
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

INVALID_RESOURCE_ID  = 60
INVALID_PAGING_QUERY = 54
INVALID_COUNT_QUERY  = 53
VALIDATOR_NOT_READY  = 15
  
class TestBatchList(RestApiBaseTest):
    """This class tests the batch list with different parameters
    """
    def test_api_get_batch_list(self, setup):
        """Tests the batch list by submitting intkey batches
        """
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
        expected_length = setup['expected_length']
        payload = setup['payload']
                                 
        try:   
            response = get_batches()
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is Unreachable")
              
        batches = response['data'][:-1]  
        
        self.assert_valid_data_list(response, expected_length)               
        self.assert_check_batch_seq(batches, expected_batches, 
                                    expected_txns, payload, 
                                    signer_key)
        
        self.assert_valid_head(response, expected_head)
            
#     def test_api_get_batch_list_head(self, setup):   
#         """Tests that GET /batches is reachable with head parameter 
#         """
#         LOGGER.info("Starting test for batch with head parameter")
#         signer_key = setup['signer_key']
#         expected_head = setup['expected_head']
#         expected_batches = setup['expected_batches']
#         expected_txns = setup['expected_txns']
#         expected_length = setup['expected_length']
#         payload = setup['payload']
#         expected_head = setup['expected_head']
#                   
#         try:
#             response = get_batches(head_id=expected_head)
#         except  urllib.error.HTTPError as error:
#             LOGGER.info("Rest Api not reachable")
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#                 
#         batches = response['data'][:-1]
#                   
#         self.assert_valid_data_list(response, expected_length)                 
#         self.assert_check_batch_seq(batches, expected_batches, 
#                                     expected_txns, payload, 
#                                     signer_key)
#         
#         self.assert_valid_head(response, expected_head)
#            
#     def test_api_get_batch_list_bad_head(self, setup):   
#         """Tests that GET /batches is unreachable with bad head parameter 
#         """       
#         LOGGER.info("Starting test for batch with bad head parameter")
#         bad_head = 'f' 
#                         
#         try:
#             batch_list = get_batches(head_id=bad_head)
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#         
#         self.assert_valid_error(data, INVALID_RESOURCE_ID)
# 
# 
#     def test_api_get_batch_list_id(self, setup):   
#         """Tests that GET /batches is reachable with id as parameter 
#         """
#         LOGGER.info("Starting test for batch with id parameter")
#         signer_key = setup['signer_key']
#         expected_head = setup['expected_head']
#         expected_batches = setup['expected_batches']
#         expected_txns = setup['expected_txns']
#         expected_length = setup['expected_length']
#         payload = setup['payload']                       
#         batch_ids   =  setup['batch_ids']
#         expected_id = batch_ids[0]
#                       
#         try:
#             response = get_batches(id=expected_id)
#         except:
#             LOGGER.info("Rest Api is not reachable")
#                      
#                      
#         batches = response['data'][:-1]
#                   
#         self.assert_valid_data_list(response, expected_length)                 
#         self.assert_check_batch_seq(batches, expected_batches, 
#                                     expected_txns, payload, 
#                                     signer_key)
#         
#         self.assert_valid_head(response, expected_head)
#                  
#     def test_api_get_batch_list_bad_id(self, setup):   
#         """Tests that GET /batches is unreachable with bad id parameter 
#         """
#         LOGGER.info("Starting test for batch with bad id parameter")
#         bad_id = 'f' 
#                        
#         try:
#             batch_list = get_batches(head_id=bad_id)
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#         
#         self.assert_valid_error(data, INVALID_RESOURCE_ID)
#         
#     def test_api_get_batch_list_head_and_id(self, setup):   
#         """Tests GET /batches is reachable with head and id as parameters 
#         """
#         LOGGER.info("Starting test for batch with head and id parameter")
#         signer_key = setup['signer_key']
#         expected_head = setup['expected_head']
#         expected_batches = setup['expected_batches']
#         expected_txns = setup['expected_txns']
#         expected_length = setup['expected_length']
#         payload = setup['payload']                       
#         batch_ids   =  setup['batch_ids']
#         expected_id = batch_ids[0]
#                         
#                  
#         response = get_batches(head_id=expected_head , id=expected_id)
#                        
#         self.assert_valid_data_list(response, expected_length)                 
#         self.assert_check_batch_seq(batches, expected_batches, 
#                                     expected_txns, payload, 
#                                     signer_key)
#         
#         self.assert_valid_head(response, expected_head)
#                  
#                 
#     def test_api_get_paginated_batch_list(self, setup):   
#         """Tests GET /batches is reachable using paging parameters 
#         """
#         LOGGER.info("Starting test for batch with paging parameters")
#         batch_ids   =  setup['batch_ids']
#         expected_head = setup['expected_head']
#         expected_id = batch_ids[0]
#         start = 1
#         limit = 1
#                     
#         try:
#             response = get_batches(start=start , limit=limit)
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#         
#         self.assert_valid_error(data, INVALID_PAGING_QUERY)
#               
#     def test_api_get_batch_list_invalid_start(self, setup):   
#         """Tests that GET /batches is unreachable with invalid start parameter 
#         """
#         LOGGER.info("Starting test for batch with invalid start parameter")
#         batch_ids   =  setup['batch_ids']
#         expected_head = setup['expected_head']
#         expected_id = batch_ids[0]
#         start = -1
#                          
#         try:  
#             response = get_batches(start=start)
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#         
#         self.assert_valid_error(data, INVALID_PAGING_QUERY)
#             
#           
#     def test_api_get_batch_list_invalid_limit(self, setup):   
#         """Tests that GET /batches is unreachable with bad limit parameter 
#         """
#         LOGGER.info("Starting test for batch with bad limit parameter")
#         batch_ids = setup['batch_ids']
#         expected_head = setup['expected_head']
#         expected_id = batch_ids[0]
#         limit = 0
#                      
#         try:  
#             response = get_batches(limit=limit)
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#         
#         self.assert_valid_error(data, INVALID_PAGING_QUERY)
#     
#     def test_api_get_batch_list_no_count(self, setup):   
#         """Tests that GET /batches is unreachable with bad limit parameter 
#         """
#         LOGGER.info("Starting test for batch with bad limit parameter")
#         batch_ids =  setup['batch_ids']
#         expected_head = setup['expected_head']
#         expected_id = batch_ids[0]
#         limit = 0
#                      
#         try:  
#             response = get_batches(limit=limit)
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#         
#         self.assert_valid_error(data, INVALID_PAGING_QUERY)
#                    
#     def test_api_get_batch_list_reversed(self, setup):   
#         """verifies that GET /batches is unreachable with bad head parameter 
#         """
#         LOGGER.info("Starting test for batch with bad head parameter")
#         signer_key = setup['signer_key']
#         expected_head = setup['expected_head']
#         expected_batches = setup['expected_batches']
#         expected_txns = setup['expected_txns']
#         expected_length = setup['expected_length']
#         payload = setup['payload']                       
#         batch_ids   =  setup['batch_ids']
#         expected_id = batch_ids[0]
#         reverse = True
#                          
#         try:
#             response = get_batches(reverse=reverse)
#         except urllib.error.HTTPError as error:
#             assert response.code == 400
#         
#         batches = response['data'][:-1]
#                         
#         self.assert_valid_data_list(response, expected_length)                 
#         self.assert_check_batch_seq(batches, expected_batches, 
#                                     expected_txns, payload, 
#                                     signer_key)
#         
#         self.assert_valid_head(response, expected_head)
#       
# class TestBatchGet():
#     def test_api_get_batch_id(self):
#         pass
#    
#          
#     def test_api_get_bad_batch_id(self):
#         pass    
# 
# 
# class TestBatchStatusGet():
#     def test_api_get_batch_id(self):
#         pass
#    
#          
#     def test_api_get_bad_batch_id(self):
#         pass 
#     
