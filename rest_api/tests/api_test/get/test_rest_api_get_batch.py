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
  
from fixtures import setup_batch , delete_genesis
from utils import get_batches, _get_node_list, _get_node_chain, check_for_consensus

from base import RestApiBaseTest

pytestmark = [pytest.mark.get , pytest.mark.batch]

  
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
  

@pytest.mark.usefixtures('setup_batch')
class TestBatchList(RestApiBaseTest):
    def test_api_get_batch_list(self, setup_batch):
        """Tests the batch list by submitting intkey batches
        """
        signer_key = setup_batch['signer_key']

        try:   
            response = get_batches()
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is unreachable")
            
        print(response)

        self.assert_check_family(response)
        self.assert_check_batch_nonce(response)
           
#     def test_api_get_batch_list_no_batches(self):
#         """Tests that transactions are submitted and committed for
#         each block that are created by submitting intkey batches
#         """    
#         batch=b''
#         try:
#             response = post_batch(batch)
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#             assert data['error']['code'] == 34
#              
#     def test_api_get_batch_list_invalid_batch(self):
#         """Tests that transactions are submitted and committed for
#         each block that are created by submitting intkey batches
#         """    
#         batch= b''
#         try:
#             response = post_batch(batch)
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#             assert data['error']['code'] == 34
#           
#     def test_api_get_batch_list_head(self , setup_batch):   
#         """Tests that GET /batches is reachable with head parameter 
#         """
#         LOGGER.info("Starting test for batch with head parameter")
#         block_list = setup_batch[0]
#         block_ids =  setup_batch[1]
#         batch_ids =  setup_batch[2]
#         expected_head_id = setup_batch[3]
#         self.assert_has_valid_head()
#               
#         try:
#             response = get_batches(head_id=expected_head_id)
#         except  urllib.error.HTTPError as error:
#             LOGGER.info("Rest Api not reachable")
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#               
#         assert response['head'] == expected_head_id , "request is not correct"
#               
#     def test_api_get_batch_list_bad_head(self):   
#         """Tests that GET /batches is unreachable with bad head parameter 
#         """       
#         LOGGER.info("Starting test for batch with bad head parameter")
#         expected_head_id = setup_batch[3]
#         bad_head = 'ff' 
#                    
#         try:
#             batch_list = get_batches(head_id=bad_head)
#         except urllib.error.HTTPError as error:
#             LOGGER.info("Rest Api is not reachable")
#             data = json.loads(error.fp.read().decode('utf-8'))
#             if data:
#                 LOGGER.info(data['error']['title'])
#                 LOGGER.info(data['error']['message'])
#                 assert data['error']['code'] == 60
#                 assert data['error']['title'] == 'Invalid Resource Id'
#             
#     def test_api_get_batch_list_id(self):   
#         """Tests that GET /batches is reachable with id as parameter 
#         """
#         LOGGER.info("Starting test for batch with id parameter")
#                    
#         block_list = setup_batch[0]
#         block_ids =  setup_batch[1]
#         batch_ids =  setup_batch[2]
#         expected_head_id = setup_batch[3]
#         expected_id = batch_ids[0]
#                   
#         try:
#             response = get_batches(id=expected_id)
#         except:
#             LOGGER.info("Rest Api is not reachable")
#                  
#                  
#         assert response['head'] == expected_head_id , "request is not correct"
#         assert response['paging']['start'] == None , "request is not correct"
#         assert response['paging']['limit'] == None , "request is not correct"
#              
#     def test_api_get_batch_list_bad_id(self):   
#         """Tests that GET /batches is unreachable with bad id parameter 
#         """
#         LOGGER.info("Starting test for batch with bad id parameter")
#         block_list = setup_batch[0]
#         block_ids =  setup_batch[1]
#         batch_ids =  setup_batch[2]
#         expected_head_id = setup_batch[3]
#         expected_id = batch_ids[0]
#         bad_id = 'ff' 
#                    
#         try:
#             batch_list = get_batches(head_id=bad_id)
#         except urllib.error.HTTPError as error:
#             LOGGER.info("Rest Api is not reachable")
#             data = json.loads(error.fp.read().decode('utf-8'))
#             if data:
#                 LOGGER.info(data['error']['title'])
#                 LOGGER.info(data['error']['message'])
#                 assert data['error']['code'] == 60
#                 assert data['error']['title'] == 'Invalid Resource Id'
#              
#     def test_api_get_batch_list_head_and_id(self):   
#         """Tests GET /batches is reachable with head and id as parameters 
#         """
#         LOGGER.info("Starting test for batch with head and id parameter")
#         block_list = setup_batch[0]
#         block_ids =  setup_batch[1]
#         batch_ids =  setup_batch[2]
#         expected_head_id = setup_batch[3]
#         expected_id = batch_ids[0]
#                     
#              
#         response = get_batches(head_id=expected_head_id , id=expected_id)
#                    
#         assert response['head'] == expected_head_id , "head is not matching"
#         assert response['paging']['start'] == None ,  "start parameter is not correct"
#         assert response['paging']['limit'] == None ,  "request is not correct"
#         assert bool(response['data']) == True
#              
#             
#     def test_api_get_paginated_batch_list(self):   
#         """Tests GET /batches is reachbale using paging parameters 
#         """
#         LOGGER.info("Starting test for batch with paging parameters")
#                      
#         block_list = setup_batch[0]
#         block_ids =  setup_batch[1]
#         batch_ids =  setup_batch[2]
#         expected_head_id = setup_batch[3]
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
#             assert data['error']['code'] == 54
#              
#     def test_api_get_batch_list_invalid_start(self):   
#         """Tests that GET /batches is unreachable with invalid start parameter 
#         """
#         LOGGER.info("Starting test for batch with invalid start parameter")
#                       
#         block_list = setup_batch[0]
#         block_ids =  setup_batch[1]
#         batch_ids =  setup_batch[2]
#         expected_head_id = setup_batch[3]
#         expected_id = batch_ids[0]
#         start = -1
#                      
#         try:  
#             response = get_batches(start=start)
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#             assert data['error']['code'] == 54
#       
#     def test_api_get_batch_list_invalid_limit(self):   
#         """Tests that GET /batches is unreachable with bad limit parameter 
#         """
#         LOGGER.info("Starting test for batch with bad limit parameter")
#                       
#         block_list = setup_batch[0]
#         block_ids =  setup_batch[1]
#         batch_ids =  setup_batch[2]
#         expected_head_id = setup_batch[3]
#         expected_id = batch_ids[0]
#         limit = 0
#                  
#         try:  
#             response = get_batches(limit=limit)
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#             assert data['error']['code'] == 53
#                  
#     def test_api_get_batch_list_reversed(self):   
#         """Tests that GET /batches is unreachable with bad head parameter 
#         """
#         LOGGER.info("Starting test for batch with bad head parameter")
#                       
#         block_list = setup_batch[0]
#         block_ids =  setup_batch[1]
#         batch_ids =  setup_batch[2]
#         expected_head_id = setup_batch[3]
#         expected_id = batch_ids[0]
#         reverse = True
#                      
#         try:
#             response = get_batches(reverse=reverse)
#         except urllib.error.HTTPError as error:
#             assert response.code == 400
#                     
#         assert response['head'] == expected_head_id , "request is not correct"
#         assert response['paging']['start'] == None ,  "request is not correct"
#         assert response['paging']['limit'] == None ,  "request is not correct"
#         assert bool(response['data']) == True
#          
# class BatchGetTest():
#     def test_api_get_batch_id():
#         """Tests that transactions are submitted and committed for
#         each block that are created by submitting intkey batches
#         """
#         LOGGER.info('Starting test for batch post')
#         LOGGER.info("Creating batches")
#         batches = make_batches('abcd')
#             
#         LOGGER.info("Submitting batches to the handlers")
#             
#         for i, batch in enumerate(batches):
#             response = post_batch(batch)
#             block_list = get_blocks()
#             batch_ids = [block['header']['batch_ids'][0] for block in block_list]
#             for id in batch_ids:
#                 data = get_batch(id)
#             
#             if response['data'][0]['status'] == 'COMMITTED':
#                 LOGGER.info('Batch is committed')           
#                 assert response['data'][0]['id'] in batch_ids, "Block is not created for the given batch"
#            
#         batch_list = get_batches()
#         for batch in batch_list:
#             data = get_batch(batch['header_signature'])
#         assert data , "No batches were submitted"     
