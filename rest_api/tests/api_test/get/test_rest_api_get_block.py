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
   
from utils import get_blocks, get_block_id, get_batches, get_transactions
 
from base import RestApiBaseTest
 
 
pytestmark = [pytest.mark.get , pytest.mark.block, pytest.mark.fourth]



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
TIMEOUT=5
 
   
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
   
   
class TestBlockList(RestApiBaseTest):
    """This class tests the blocks list with different parameters
    """
    async def test_api_get_block_list(self, setup):
        """Tests the block list by submitting intkey batches
        """
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
        start = setup['start']
        limit = setup['limit']
        address = setup['address']
        payload = setup['payload']
        
        expected_link = '{}/blocks?head={}&start={}&limit={}'.format(address,\
                         expected_head, start, limit)
        
        paging_link = '{}/blocks?head={}&start={}'.format(address,\
                         expected_head, start)
               
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address), 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
            
        blocks = response['data'][:-1] 
        
        self.assert_check_block_seq(blocks,expected_batches,
                                    expected_txns,payload,signer_key)
        self.assert_valid_head(response, expected_head)
                             
    async def test_api_get_block_list_head(self, setup):   
        """Tests that GET /blocks is reachable with head parameter 
        """
        LOGGER.info("Starting test for blocks with head parameter")
        address = setup['address']
        expected_head = setup['expected_head']
        params={'head': expected_head}
                  
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address), params=params, 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
        
        blocks = response['data'][:-1]                  
        self.assert_valid_head(response, expected_head)
           
    async def test_api_get_block_list_bad_head(self, setup):   
        """Tests that GET /blocks is unreachable with bad head parameter 
        """       
        LOGGER.info("Starting test for blocks with bad head parameter")
        address = setup['address']
        params={'head': BAD_HEAD}
                          
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address), params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
        
        self.assert_valid_error(response, INVALID_RESOURCE_ID)
                
    async def test_api_get_block_list_id(self, setup):   
        """Tests that GET /blocks is reachable with id as parameter 
        """
        LOGGER.info("Starting test for blocks with id parameter")
        address = setup['address']
        signer_key = setup['signer_key']
        block_ids   =  setup['block_ids']
        expected_head = setup['expected_head']
        expected_id = block_ids[0]
        expected_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
        address = setup['address']
        payload = setup['payload']
        
        expected_link = '{}/blocks?head={}&start&limit=0&id={}'.format(address,\
                         expected_head, expected_id)
                      
        params={'id': expected_id}
                    
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address), params=params, 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
        
        blocks = response['data'][:-1] 
                     
        self.assert_check_block_seq(blocks,expected_batches,
                                    expected_txns,payload,signer_key)
        self.assert_valid_head(response, expected_head)
        self.assert_valid_link(response, expected_link)
                 
    async def test_api_get_block_list_bad_id(self, setup):   
        """Tests that GET /blocks is unreachable with bad id parameter 
        """
        LOGGER.info("Starting test for blocks with bad id parameter")
        address = setup['address']
        params={'head': BAD_ID}
                          
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address), params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
          
        self.assert_valid_error(response, INVALID_RESOURCE_ID)
               
             
                
    async def test_api_get_paginated_block_list(self, setup):   
        """Tests GET /blocks is reachable using paging parameters 
        """
        LOGGER.info("Starting test for blocks with paging parameters")
        address = setup['address']
        block_ids   =  setup['block_ids']
        expected_head = setup['expected_head']
        expected_id = block_ids[0]
                    
        params={'limit':1, 'start':1}
                          
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batches'.format(address), params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
          
        self.assert_valid_error(response, INVALID_PAGING_QUERY)
    
    async def test_api_get_block_list_limit(self, setup):   
        """Tests GET /batches is reachable using paging parameters 
        """
        LOGGER.info("Starting test for batch with paging parameters")
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
        start = setup['start']
        limit = setup['limit']
        address = setup['address']
        payload = setup['payload']
        params={'limit':1}
        
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address), params=params, 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
        
        blocks = response['data'][:-1]
        
        self.assert_check_block_seq(blocks,expected_batches,
                                    expected_txns,payload,signer_key)
        self.assert_valid_head(response, expected_head)
                                 
                 
    async def test_api_get_block_list_invalid_start(self, setup):   
        """Tests that GET /blocks is unreachable with invalid start parameter 
        """
        LOGGER.info("Starting test for block with invalid start parameter")
        address = setup['address']
        block_ids   =  setup['block_ids']
        expected_head = setup['expected_head']
        expected_id = block_ids[0]
        params={'start':-1}
                          
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address), params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
          
        self.assert_valid_error(response, INVALID_PAGING_QUERY)
    
          
    async def test_api_get_block_list_invalid_limit(self, setup):   
        """Tests that GET /blocks is unreachable with bad limit parameter 
        """
        LOGGER.info("Starting test for block with bad limit parameter")
        address = setup['address']
        block_ids = setup['block_ids']
        expected_head = setup['expected_head']
        expected_id = block_ids[0]
        params={'limit':0}
                          
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batches'.format(address), params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)

        self.assert_valid_error(response, INVALID_COUNT_QUERY)
    
                     
    async def test_api_get_block_list_reversed(self, setup):   
        """verifies that GET /blocks is unreachable with bad head parameter 
        """
        LOGGER.info("Starting test for blocks with reversed list")
        address = setup['address']
        block_ids = setup['block_ids']
        expected_head = setup['expected_head']
        expected_id = block_ids[0]
                         
        params = 'reverse'
                           
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address), params=params, 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
                        
        assert response['head'] == expected_head , "request is not correct"
        assert response['paging']['start'] == None ,  "request is not correct"
        assert response['paging']['limit'] == None ,  "request is not correct"
        assert bool(response['data']) == True
    
    async def test_api_get_block_link_val(self, setup):
        """Tests/ validate the block parameters with blocks, head, start and limit
        """
        address = setup['address']
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address), 
                                       raise_for_status=True) as data:
                    response = await data.json()

            for link in response:
                if(link == 'link'):
                    assert 'head' in response['link']
                    assert 'start' in response['link']  
                    assert 'limit' in response['link'] 
                    assert 'blocks' in response['link']  
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
            LOGGER.info("Link is not proper for state and parameters are missing")
    
    async def test_api_get_block_key_params(self, setup):
        """Tests/ validate the block key parameters with data, head, link and paging               
        """
        address = setup['address']
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address), 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
        
        assert 'link' in response
        assert 'data' in response
        assert 'paging' in response
        assert 'head' in response
    
    async def test_api_get_each_block_batch_id_length(self, setup):
        """Tests the each batch id length should be 128 hex character long 
        """ 
        address = setup['address']  
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address),
                                       raise_for_status=True) as data:
                    response = await data.json()
                    
            for batch in response['data']:
                expected_head = batch['header']['batch_ids'][0]
                head_len = len(expected_head)
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Batch id length is not 128 hex character long")
        assert head_len == HEAD_LENGTH     
        
    async def test_api_get_first_block_id_length(self, setup):
        """Tests the first block id length should be 128 hex character long 
        """   
        address = setup['address']
        try: 
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address), 
                                       raise_for_status=True) as data:
                    response = await data.json()
                    
            for block_list in get_blocks():
                batch_list = get_batches()
                for block in batch_list:
                    expected_head = batch_list['head']
                    head_len = len(expected_head)
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Block id length is not 128 hex character long")
        assert head_len == HEAD_LENGTH
    
    async def test_rest_api_check_post_max_batches(self, setup):
        """Tests that allow max post batches in block
        Handled max 100 batches post in block and handle for extra batch
        """
        address = setup['address']
        try: 
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address), 
                                       raise_for_status=True) as data:
                    response = await data.json()
                    
            block_list = response['data']
            for batchcount, _ in enumerate(block_list, start=1):
                if batchcount == MAX_BATCH_IN_BLOCK:
                    print("Max 100 Batches are present in Block")
        
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error) 
           
    async def test_rest_api_check_head_signature(self, setup):
        """Tests that head signature of each batch of the block 
        should be not none 
        """
        address = setup['address']
        try: 
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address),
                                       raise_for_status=True) as data:
                    response = await data.json()
                    
            block_list = response['data']
            head_signature = [block['batches'][0]['header_signature'] for block in block_list]
            for i, _ in enumerate(block_list):
                head_sig = json.dumps(head_signature[i]).encode('utf8')
                assert head_signature[i] is not None, "Head signature is available for all batches in block"   
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error) 
    
    async def test_rest_api_check_family_version(self, setup):
        """Test batch transaction family version should be present 
        for each transaction header
        """
        address = setup['address']
        try: 
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address), 
                                       raise_for_status=True) as data:
                    response = await data.json()
                    
            block_list = response['data']
            family_version = [block['batches'][0]['transactions'][0]['header']['family_version'] for block in block_list]
            for i, _ in enumerate(block_list):
                assert family_version[i] is not None, "family version present for all batches in block"
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
        
    async def test_rest_api_check_input_output_content(self,setup):
        """Test batch input and output content should be same for
        each batch and unique from other
        """
        address = setup['address']
        try: 
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address), 
                                       raise_for_status=True) as data:
                    response = await data.json()
            
            block_list = response['data']  
            txn_input = [block['batches'][0]['transactions'][0]['header']['inputs'][0] for block in block_list]
            txn_output = [block['batches'][0]['transactions'][0]['header']['outputs'][0] for block in block_list]
            if(txn_input == txn_output):
                return True
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
            
    async def test_rest_api_check_signer_public_key(self, setup):
        """Tests that signer public key is calculated for a block
        properly
        """
        address = setup['address']
        try: 
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address), 
                                       raise_for_status=True) as data:
                    response = await data.json()
        
            block_list = response['data']   
            signer_public_key = [block['batches'][0]['header']['signer_public_key'] for block in block_list]
            assert signer_public_key is not None, "signer public key is available"
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
    
    async def test_rest_api_check_blocks_count(self, setup):
        """Tests blocks count from block list 
        """
        address = setup['address']
        count =0
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address), 
                                       raise_for_status=True) as data:
                    response = await data.json()
                    
            for block in enumerate(response['data']):
                count = count+1
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("BLock count not able to collect")
    
    async def test_rest_api_blk_content_head_signature(self, setup):
        """Tests that head signature of each batch of the block
        should be not none
        """
        address = setup['address']
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks'.format(address), 
                                       raise_for_status=True) as data:
                    response = await data.json()
                    
            for batch in response['data']:
                batch_list = get_batches()
                for block in batch_list:
                    transaction_list = get_transactions()
                    for trans in transaction_list['data']:
                        head_signature = trans['header_signature']
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Header signature is missing in some of the batches")    
        assert head_signature is not None, "Head signature is available for all batches in block"
        
class TestBlockGet(RestApiBaseTest):
    async def test_api_get_block_id(self, setup):
        """Tests that GET /blocks/{block_id} is reachable 
        """
        LOGGER.info("Starting test for blocks/{block_id}")
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_id  = setup['block_ids'][0]
        expected_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
        payload = setup['payload']
        address = setup['address']
        expected_link = '{}/blocks/{}'.format(address, expected_id)
                         
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks/{}'.format(address,expected_id), 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable") 
        
        blocks = response['data']  
        
        self.assert_check_block_seq(blocks,expected_batches,
                                    expected_txns,payload,signer_key)
          
    async def test_api_get_bad_block_id(self, setup):
        """Tests that GET /blocks/{bad_block_id} is not reachable
           with bad id
        """
        LOGGER.info("Starting test for blocks/{bad_block_id}")
        address = setup['address']
                 
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/blocks/{}'.format(address,BAD_ID)) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
          
        self.assert_valid_error(response, INVALID_RESOURCE_ID)

