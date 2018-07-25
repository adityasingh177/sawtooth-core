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
   
from utils import get_blocks
 
from base import RestApiBaseTest
 
 
pytestmark = [pytest.mark.get , pytest.mark.block]


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
 
   
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
   
   
class TestBlockList(RestApiBaseTest):
    """This class tests the batch list with different parameters
    """
    def test_api_get_block_list(self, setup):
        """Tests the batch list by submitting intkey batches
        """
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
              
        try:   
            response = get_blocks()
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is Unreachable")
           
        batches = response['data'][:-1]  
                     
        self.assert_check_block_seq(batches , expected_batches , expected_txns)
        self.assert_valid_head(response , expected_head)
        self.assert_valid_link(response, expected_link)
        self.assert_valid_paging(response)
                            
    def test_api_get_block_list_head(self, setup):   
        """Tests that GET /batches is reachable with head parameter 
        """
        LOGGER.info("Starting test for batch with head parameter")
        expected_head = setup['expected_head']
                 
        try:
            response = get_blocks(head_id=expected_head)
        except  urllib.error.HTTPError as error:
            LOGGER.info("Rest Api not reachable")
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
                 
        assert response['head'] == expected_head , "request is not correct"
          
    def test_api_get_block_list_bad_head(self, setup):   
        """Tests that GET /batches is unreachable with bad head parameter 
        """       
        LOGGER.info("Starting test for batch with bad head parameter")
                      
        try:
            batch_list = get_blocks(head_id=BAD_HEAD)
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is not reachable")
            data = json.loads(error.fp.read().decode('utf-8'))
        
        self.assert_valid_error(data, INVALID_RESOURCE_ID)
               
    def test_api_get_block_list_id(self, setup):   
        """Tests that GET /batches is reachable with id as parameter 
        """
        LOGGER.info("Starting test for batch with id parameter")
                      
        block_ids   =  setup['block_ids']
        expected_head = setup['expected_head']
        expected_id = block_ids[0]
                     
        try:
            response = get_blocks(id=expected_id)
        except:
            LOGGER.info("Rest Api is not reachable")
                    
                    
        assert response['head'] == expected_head, "request is not correct"
        assert response['paging']['start'] == None , "request is not correct"
        assert response['paging']['limit'] == None , "request is not correct"
                
    def test_api_get_block_list_bad_id(self, setup):   
        """Tests that GET /batches is unreachable with bad id parameter 
        """
        LOGGER.info("Starting test for batch with bad id parameter")
        bad_id = 'f' 
                      
        try:
            batch_list = get_blocks(head_id=bad_id)
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is not reachable")
            data = json.loads(error.fp.read().decode('utf-8'))
        
        self.assert_valid_error(data, INVALID_RESOURCE_ID)
              
    def test_api_get_block_list_head_and_id(self, setup):   
        """Tests GET /batches is reachable with head and id as parameters 
        """
        LOGGER.info("Starting test for batch with head and id parameter")
        block_ids =  setup['block_ids']
        expected_head = setup['expected_head']
        expected_id = block_ids[0]
                       
                
        response = get_blocks(head_id=expected_head , id=expected_id)
                      
        assert response['head'] == expected_head , "head is not matching"
        assert response['paging']['start'] == None ,  "start parameter is not correct"
        assert response['paging']['limit'] == None ,  "request is not correct"
        assert bool(response['data']) == True
                
               
    def test_api_get_paginated_block_list(self, setup):   
        """Tests GET /batches is reachbale using paging parameters 
        """
        LOGGER.info("Starting test for batch with paging parameters")
        block_ids   =  setup['block_ids']
        expected_head = setup['expected_head']
        expected_id = block_ids[0]
        start = 1
        limit = 1
                   
        try:
            response = get_blocks(start=start , limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
        
        self.assert_valid_error(data, INVALID_PAGING_QUERY)
                
    def test_api_get_block_list_invalid_start(self, setup):   
        """Tests that GET /batches is unreachable with invalid start parameter 
        """
        LOGGER.info("Starting test for batch with invalid start parameter")
        block_ids   =  setup['block_ids']
        expected_head = setup['expected_head']
        expected_id = block_ids[0]
        start = -1
                        
        try:  
            response = get_blocks(start=start)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
        
        self.assert_valid_error(data, INVALID_PAGING_QUERY)
         
    def test_api_get_block_list_invalid_limit(self, setup):   
        """Tests that GET /batches is unreachable with bad limit parameter 
        """
        LOGGER.info("Starting test for batch with bad limit parameter")
        block_ids = setup['block_ids']
        expected_head = setup['expected_head']
        expected_id = block_ids[0]
        limit = 0
                    
        try:  
            response = get_blocks(limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
        
        self.assert_valid_error(data, INVALID_COUNT_QUERY)
   
                    
    def test_api_get_block_list_reversed(self, setup):   
        """verifies that GET /batches is unreachable with bad head parameter 
        """
        LOGGER.info("Starting test for batch with bad head parameter")
        block_ids = setup['block_ids']
        expected_head = setup['expected_head']
        expected_id = block_ids[0]
        reverse = True
                        
        try:
            response = get_blocks(reverse=reverse)
        except urllib.error.HTTPError as error:
            assert response.code == 400
                       
        assert response['head'] == expected_head , "request is not correct"
        assert response['paging']['start'] == None ,  "request is not correct"
        assert response['paging']['limit'] == None ,  "request is not correct"
        assert bool(response['data']) == True
  
#     def test_api_get_batch_list_bad_protobufs(self):
#          """Verifies requests for lists of batches break with bad protobufs.
#   
#          Expects to find:
#              - a status of INTERNAL_ERROR
#              - that head_id, paging, and batches are missing
#          """
#          response = self.make_bad_request(head_id=B_1)
#   
#          self.assertEqual(self.status.INTERNAL_ERROR, response.status)
#          self.assertFalse(response.head_id)
#          self.assertFalse(response.paging.SerializeToString())
#          self.assertFalse(response.batches)
# 
#     @pytest.mark.usefixtures('break_genesis')
#     def test_api_get_batch_list_no_genesis(self , break_genesis):
#         """Verifies requests for lists of batches breaks with no genesis.
#    
#          Expects to find:
#              - a status of NOT_READY
#         """
#         try:
#             response = get_batches()
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#             assert data['error']['code'] == 15
#  
#     @pytest.mark.usefixtures('setup_settings_tp')
#     def test_api_get_batch_list_no_settings_tp(self , setup_settings_tp):
#         try:
#             response = get_batches()
#         except urllib.error.HTTPError as error:
#             data = json.loads(error.fp.read().decode('utf-8'))
#             LOGGER.info(data['error']['title'])
#             LOGGER.info(data['error']['message'])
#             assert data['error']['code'] == 15
