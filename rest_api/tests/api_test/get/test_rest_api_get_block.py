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
   
from utils import get_blocks, get_block_id, get_batches, get_transactions
 
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
BLOCK_NOT_FOUND = 70
HEAD_LENGTH = 128
MAX_BATCH_IN_BLOCK = 100
FAMILY_NAME = 'xo'
 
   
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
   
   
class TestBlockList(RestApiBaseTest):
    """This class tests the blocks list with different parameters
    """
    def test_api_get_block_list(self, setup):
        """Tests the block list by submitting intkey batches
        """
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
               
        try:   
            response = get_blocks()
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is Unreachable")
            
        blocks = response['data'][:-1]  
                             
    def test_api_get_block_list_head(self, setup):   
        """Tests that GET /blocks is reachable with head parameter 
        """
        LOGGER.info("Starting test for blocks with head parameter")
        expected_head = setup['expected_head']
                  
        try:
            response = get_blocks(head_id=expected_head)
        except  urllib.error.HTTPError as error:
            LOGGER.info("Rest Api not reachable")
            response = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(response['error']['title'])
            LOGGER.info(response['error']['message'])
                  
        assert response['head'] == expected_head , "request is not correct"
           
    def test_api_get_block_list_bad_head(self, setup):   
        """Tests that GET /blocks is unreachable with bad head parameter 
        """       
        LOGGER.info("Starting test for blocks with bad head parameter")
                       
        try:
            batch_list = get_blocks(head_id=BAD_HEAD)
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is not reachable")
            response = json.loads(error.fp.read().decode('utf-8'))
         
        self.assert_valid_error(response, INVALID_RESOURCE_ID)
                
    def test_api_get_block_list_id(self, setup):   
        """Tests that GET /blocks is reachable with id as parameter 
        """
        LOGGER.info("Starting test for blocks with id parameter")
                       
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
        """Tests that GET /blocks is unreachable with bad id parameter 
        """
        LOGGER.info("Starting test for blocks with bad id parameter")
        bad_id = 'f' 
                       
        try:
            batch_list = get_blocks(head_id=bad_id)
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is not reachable")
            response = json.loads(error.fp.read().decode('utf-8'))
         
        self.assert_valid_error(response, INVALID_RESOURCE_ID)
               
    def test_api_get_block_list_head_and_id(self, setup):   
        """Tests GET /blocks is reachable with head and id as parameters 
        """
        LOGGER.info("Starting test for blocks with head and id parameter")
        block_ids =  setup['block_ids']
        expected_head = setup['expected_head']
        expected_id = block_ids[0]
                        
                 
        response = get_blocks(head_id=expected_head , id=expected_id)
                       
        assert response['head'] == expected_head , "head is not matching"
        assert response['paging']['start'] == None ,  "start parameter is not correct"
        assert response['paging']['limit'] == None ,  "request is not correct"
        assert bool(response['data']) == True
                 
                
    def test_api_get_paginated_block_list(self, setup):   
        """Tests GET /blocks is reachable using paging parameters 
        """
        LOGGER.info("Starting test for blocks with paging parameters")
        block_ids   =  setup['block_ids']
        expected_head = setup['expected_head']
        expected_id = block_ids[0]
        start = 1
        limit = 1
                    
        try:
            response = get_blocks(start=start , limit=limit, id=expected_id)
        except urllib.error.HTTPError as error:
            response = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(response['error']['title'])
            LOGGER.info(response['error']['message'])
         
        self.assert_valid_error(response, INVALID_PAGING_QUERY)
    
    def test_api_get_block_list_start_id(self, setup):   
        """Tests GET /blocks is reachable using paging parameters 
        """
        LOGGER.info("Starting test for blocks with paging parameters")
        block_ids   =  setup['block_ids']
        expected_head = setup['expected_head']
        expected_id = block_ids[0]
        start = 1
        limit = 1
                    
        try:
            response = get_blocks(start=start , limit=limit, id=expected_id)
        except urllib.error.HTTPError as error:
            response = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(response['error']['title'])
            LOGGER.info(response['error']['message'])
         
        self.assert_valid_error(response, INVALID_PAGING_QUERY)
                 
    def test_api_get_block_list_invalid_start(self, setup):   
        """Tests that GET /blocks is unreachable with invalid start parameter 
        """
        LOGGER.info("Starting test for batch with invalid start parameter")
        block_ids   =  setup['block_ids']
        expected_head = setup['expected_head']
        expected_id = block_ids[0]
        start = -1
                         
        try:  
            response = get_blocks(start=start)
        except urllib.error.HTTPError as error:
            response = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(response['error']['title'])
            LOGGER.info(response['error']['message'])
         
        self.assert_valid_error(response, INVALID_PAGING_QUERY)
    
    def test_api_get_block_list_limit(self, setup):   
        """Tests that GET /blocks is unreachable with invalid start parameter 
        """
        LOGGER.info("Starting test for batch with invalid start parameter")
        block_ids   =  setup['block_ids']
        expected_head = setup['expected_head']
        expected_id = block_ids[0]
        start = -1
                         
        try:  
            response = get_blocks(start=start)
        except urllib.error.HTTPError as error:
            response = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(response['error']['title'])
            LOGGER.info(response['error']['message'])
         
        self.assert_valid_error(response, INVALID_PAGING_QUERY)
          
    def test_api_get_block_list_invalid_limit(self, setup):   
        """Tests that GET /blocks is unreachable with bad limit parameter 
        """
        LOGGER.info("Starting test for batch with bad limit parameter")
        block_ids = setup['block_ids']
        expected_head = setup['expected_head']
        expected_id = block_ids[0]
        limit = 0
                     
        try:  
            response = get_blocks(limit=limit)
        except urllib.error.HTTPError as error:
            response = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(response['error']['title'])
            LOGGER.info(response['error']['message'])
         
        self.assert_valid_error(response, INVALID_COUNT_QUERY)
    
                     
    def test_api_get_block_list_reversed(self, setup):   
        """verifies that GET /blocks is unreachable with bad head parameter 
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
    
    def test_api_get_block_link_val(self, setup):
        """Tests/ validate the block parameters with blocks, head, start and limit
        """
        try:
            block_list = get_blocks()
            for link in block_list:
                if(link == 'link'):
                    assert 'head' in block_list['link']
                    assert 'start' in block_list['link']  
                    assert 'limit' in block_list['link'] 
                    assert 'blocks' in block_list['link']  
        except urllib.error.HTTPError as error:
            assert response.code == 400
            LOGGER.info("Link is not proper for state and parameters are missing")
    
    def test_api_get_block_key_params(self, setup):
        """Tests/ validate the block key parameters with data, head, link and paging               
        """
        response = get_blocks()
        assert 'link' in response
        assert 'data' in response
        assert 'paging' in response
        assert 'head' in response
    
    def test_api_get_each_batch_id_length(self, setup):
        """Tests the each batch id length should be 128 hex character long 
        """   
        try:
            block_list = get_blocks()
            for batch in block_list['data']:
                expected_head = batch['header']['batch_ids'][0]
                head_len = len(expected_head)
        except urllib.error.HTTPError as error:
            LOGGER.info("Batch id length is not 128 hex character long")
        assert head_len == HEAD_LENGTH     
        
    def test_api_get_first_block_id_length(self, setup):
        """Tests the first block id length should be 128 hex character long 
        """   
        try: 
            for block_list in get_blocks():
                batch_list = get_batches()
                for block in batch_list:
                    expected_head = batch_list['head']
                    head_len = len(expected_head)
        except urllib.error.HTTPError as error:
            LOGGER.info("Block id length is not 128 hex character long")
        assert head_len == HEAD_LENGTH
    
    def test_rest_api_check_post_max_batches(self, setup):
        """Tests that allow max post batches in block
        Handled max 100 batches post in block and handle for extra batch
        """
        block_list = get_blocks()['data']
        for batchcount, _ in enumerate(block_list, start=1):
            if batchcount == MAX_BATCH_IN_BLOCK:
                print("Max 100 Batches are present in Block") 
           
    def test_rest_api_check_head_signature(self, setup):
        """Tests that head signature of each batch of the block 
        should be not none 
        """
        block_list = get_blocks()['data']
        head_signature = [block['batches'][0]['header_signature'] for block in block_list]
        for i, _ in enumerate(block_list):
            head_sig = json.dumps(head_signature[i]).encode('utf8')
            assert head_signature[i] is not None, "Head signature is available for all batches in block"   
    
    def test_rest_api_check_family_version(self, setup):
        """Test batch transaction family version should be present 
        for each transaction header
        """
        block_list = get_blocks()['data']
        family_version = [block['batches'][0]['transactions'][0]['header']['family_version'] for block in block_list]
        for i, _ in enumerate(block_list):
            assert family_version[i] is not None, "family version present for all batches in block"
        
    def test_rest_api_check_input_output_content(self,setup):
        """Test batch input and output content should be same for
        each batch and unique from other
        """
        block_list = get_blocks()['data']  
        txn_input = [block['batches'][0]['transactions'][0]['header']['inputs'][0] for block in block_list]
        txn_output = [block['batches'][0]['transactions'][0]['header']['outputs'][0] for block in block_list]
        if(txn_input == txn_output):
            return True
    def test_rest_api_check_signer_public_key(self, setup):
        """Tests that signer public key is calculated for a block
        properly
        """
        block_list = get_blocks()['data']   
        signer_public_key = [block['batches'][0]['header']['signer_public_key'] for block in block_list]
        assert signer_public_key is not None, "signer public key is available"
    
    def test_rest_api_check_blocks_count(self, setup):
        """Tests blocks count from block list 
        """
        count =0
        try:
            block_list = get_blocks()
            for block in enumerate(block_list['data']):
                count = count+1
        except urllib.error.HTTPError as error:
            LOGGER.info("BLock count not able to collect")
    
    def test_rest_api_blk_content_head_signature(self, setup):
        """Tests that head signature of each batch of the block
        should be not none
        """
        try:
            block_list = get_blocks()
            for batch in block_list['data']:
                batch_list = get_batches()
                for block in batch_list:
                    transaction_list = get_transactions()
                    for trans in transaction_list['data']:
                        head_signature = trans['header_signature']
        except urllib.error.HTTPError as error:
            LOGGER.info("Header signature is missing in some of the batches")    
        assert head_signature is not None, "Head signature is available for all batches in block"
        
class TestBlockGet(RestApiBaseTest):
    def test_api_get_block_id(self, setup):
        """Tests that GET /blocks/{block_id} is reachable 
        """
        LOGGER.info("Starting test for blocks/{block_id}")
        expected_head = setup['expected_head']
        expected_block_id  = setup['block_ids'][0]
                         
        try:
            response = get_block_id(block_id=expected_block_id)
        except  urllib.error.HTTPError as error:
            LOGGER.info("Rest Api not reachable")
            response = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(response['error']['title'])
            LOGGER.info(response['error']['message'])    
          
    def test_api_get_bad_block_id(self, setup):
        """Tests that GET /blocks/{bad_block_id} is not reachable
           with bad id
        """
        LOGGER.info("Starting test for blocks/{bad_block_id}")
                 
        try:
            response = get_block_id(block_id=BAD_ID)
        except  urllib.error.HTTPError as error:
            LOGGER.info("Rest Api not reachable")
            response = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(response['error']['title'])
            LOGGER.info(response['error']['message'])

