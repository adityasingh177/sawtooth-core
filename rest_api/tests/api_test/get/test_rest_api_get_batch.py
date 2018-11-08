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
import asyncio

 
from fixtures import break_genesis, invalid_batch

from utils import get_batches, get_batch_id, post_batch,\
                  get_batch_statuses, post_batch_statuses,\
                  _create_expected_link, _get_batch_list

from base import RestApiBaseTest

pytestmark = [pytest.mark.get , pytest.mark.batch, pytest.mark.second]


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
BATCH_NOT_FOUND = 71
STATUS_ID_QUERY_INVALID = 66
STATUS_BODY_INVALID = 43
STATUS_WRONG_CONTENT_TYPE = 46
WAIT = 10

class TestBatchList(RestApiBaseTest):
    """This class tests the batch list with different parameters
    """
    async def test_api_get_batch_list(self, setup):
        """Tests the batch list by submitting intkey batches
        """
        LOGGER.info("Starting tests for batch list")
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
        expected_length = setup['expected_batch_length']
        payload = setup['payload']
        start = setup['start']
        limit = setup['limit']
        address = setup['address'] 
        url='{}/batches'.format(address)            
        expected_link = '{}/batches?head={}&start={}&limit={}'.format(address,\
                         expected_head, start, limit)
        
        paging_link = '{}/batches?head={}&start={}'.format(address,\
                         expected_head, start)
        
                                                 
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url=url) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
            
        batches = _get_batch_list(response) 
          
        self.assert_valid_data(response)
        self.assert_valid_head(response, expected_head) 
        self.assert_valid_data_length(batches, expected_length)
        self.assert_check_batch_seq(batches, expected_batches, 
                                    expected_txns, payload, 
                                    signer_key)
        self.assert_valid_link(response, expected_link)
        self.assert_valid_paging(response, expected_link)
            
    async def test_api_get_batch_list_head(self, setup):   
        """Tests that GET /batches is reachable with head parameter 
        """
        LOGGER.info("Starting test for batch with head parameter")
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
        payload = setup['payload']
        expected_head = setup['expected_head']
        start = setup['start']
        limit = setup['limit']
        address = setup['address']
             
        expected_link = '{}/batches?head={}&start={}&limit={}'.format(address,\
                         expected_head, start, limit)
        
        params={'head': expected_head}
                    
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batches'.format(address), params=params, 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
                  
        batches = response['data'][:-1]
                    
        self.assert_check_batch_seq(batches, expected_batches, 
                                    expected_txns, payload, 
                                    signer_key)
          
        self.assert_valid_head(response, expected_head)
        self.assert_valid_link(response, expected_link)
        self.assert_valid_paging(response, expected_link)
             
    async def test_api_get_batch_list_bad_head(self, setup):   
        """Tests that GET /batches is unreachable with bad head parameter 
        """       
        LOGGER.info("Starting test for batch with bad head parameter")
        params={'head': BAD_HEAD}
        address = setup['address']
                          
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batches'.format(address), params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
        
        self.assert_valid_error(response, INVALID_RESOURCE_ID)

    async def test_api_get_batch_list_id(self, setup):   
        """Tests that GET /batches is reachable with id as parameter 
        """
        LOGGER.info("Starting test for batch with id parameter")
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
        payload = setup['payload']                       
        batch_ids   =  setup['batch_ids']
        start = setup['start']
        limit = setup['limit']
        address = setup['address']
         
        expected_id = batch_ids[0]
        expected_length = len([expected_id])
             
        expected_link = '{}/batches?head={}&start={}&limit={}&id={}'.format(address,\
                         expected_head, start, limit, expected_id)
           
        params={'id': expected_id}
                    
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batches'.format(address), params=params, 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
                       
                       
        batches = response['data'][:-1]
                    
        self.assert_check_batch_seq(batches, expected_batches, 
                                    expected_txns, payload, 
                                    signer_key)
          
        self.assert_valid_head(response, expected_head)
        self.assert_valid_link(response, expected_link)
 
    async def test_api_get_batch_list_bad_id(self, setup):   
        """Tests that GET /batches is unreachable with bad id parameter 
        """
        LOGGER.info("Starting test for batch with bad id parameter")
        address = setup['address']
        params={'head': BAD_ID}
                          
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batches'.format(address), params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
          
        self.assert_valid_error(response, INVALID_RESOURCE_ID)
          
    async def test_api_get_batch_list_head_and_id(self, setup):   
        """Tests GET /batches is reachable with head and id as parameters 
        """
        LOGGER.info("Starting test for batch with head and id parameter")
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
        payload = setup['payload']                       
        batch_ids   =  setup['batch_ids']
        start = setup['start']
        limit = setup['limit']
        address = setup['address']
         
        expected_id = batch_ids[0]
        expected_length = len([expected_id])
             
        expected_link = '{}/batches?head={}&start={}&limit={}&id={}'.format(address,\
                         expected_head, start, limit, expected_id)
                                  
        params={'head':expected_head,'id':expected_id}
                    
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batches'.format(address), params=params, 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
             
                         
        batches = response['data'][:-1]
                                 
        self.assert_check_batch_seq(batches, expected_batches, 
                                    expected_txns, payload, 
                                    signer_key)
          
        self.assert_valid_head(response, expected_head)
        self.assert_valid_link(response, expected_link)
                           
    async def test_api_get_paginated_batch_list(self, setup):   
        """Tests GET /batches is reachable using paging parameters 
        """
        LOGGER.info("Starting test for batch with paging parameters")
        batch_ids   =  setup['batch_ids']
        address = setup['address']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
 
        params={'limit':1, 'start':1}
                          
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batches'.format(address), params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
          
        self.assert_valid_error(response, INVALID_PAGING_QUERY)
    
    async def test_api_get_batch_list_limit(self, setup):   
        """Tests GET /batches is reachable using paging parameters 
        """
        LOGGER.info("Starting test for batch with paging parameters")
        signer_key = setup['signer_key']
        batch_ids   =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
        payload = setup['payload']
        expected_id = batch_ids[0]
        start = setup['start']
        address = setup['address']
        params={'limit':1}
        
        expected_link = '{}/batches?head={}&start={}&limit={}'.format(address,\
                         expected_head, start, 1)
                      
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batches'.format(address), params=params, 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
        
        batches = response['data'][:-1]
                                 
        self.assert_check_batch_seq(batches, expected_batches, 
                                    expected_txns, payload, 
                                    signer_key)
          
        self.assert_valid_head(response, expected_head)
        self.assert_valid_link(response, expected_link)
        self.assert_valid_paging(response, expected_link)
        
        
    async def test_api_get_batch_list_invalid_start(self, setup):   
        """Tests that GET /batches is unreachable with invalid start parameter 
        """
        LOGGER.info("Starting test for batch with invalid start parameter")
        batch_ids   =  setup['batch_ids']
        address = setup['address']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        params={'start':-1}
                          
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batches'.format(address), params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
          
        self.assert_valid_error(response, INVALID_PAGING_QUERY)
              
            
    async def test_api_get_batch_list_invalid_limit(self, setup):   
        """Tests that GET /batches is unreachable with bad limit parameter 
        """
        LOGGER.info("Starting test for batch with bad limit parameter")
        batch_ids = setup['batch_ids']
        address = setup['address']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        params={'limit':0}
                          
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batches'.format(address), params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)

        self.assert_valid_error(response, INVALID_COUNT_QUERY)
                     
    async def test_api_get_batch_list_reversed(self, setup):   
        """verifies that GET /batches is unreachable with bad head parameter 
        """
        LOGGER.info("Starting test for batch list as reversed")
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
        expected_length = setup['expected_batch_length']
        payload = setup['payload']                    
        start = setup['batch_ids'][::-1][0]
        limit = setup['limit']
        address = setup['address']
             
        expected_link = '{}/batches?head={}&start={}&limit={}&reverse'.format(address,\
                         expected_head, start, limit)
         
        params = 'reverse'
                                           
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url='{}/batches'.format(address), params=params, 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
                               
        
        batches = response['data'][::-1][:-1]
        

        self.assert_check_batch_seq(batches, expected_batches, 
                                    expected_txns, payload, 
                                    signer_key)
          
        self.assert_valid_head(response, expected_head)
        self.assert_valid_link(response, expected_link)
        self.assert_valid_paging(response, expected_link)
                  
  
    async def test_api_get_batch_key_params(self, setup):
        """Tests/ validate the block key parameters with data, head, link and paging               
        """
        address = setup['address']
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batches'.format(address), raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
        
        assert 'link' in response
        assert 'data' in response
        assert 'paging' in response
        assert 'head' in response
    
    async def test_api_get_batch_param_link_val(self, setup):
        """Tests/ validate the batch parameters with batches, head, start and limit
        """
        address = setup['address']
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batches'.format(address), raise_for_status=True) as data:
                    response = await data.json()
            
            for link in response:
                if(link == 'link'):
                    assert 'head' in response['link']
                    assert 'start' in response['link']  
                    assert 'limit' in response['link'] 
                    assert 'batches' in response['link']  
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
            LOGGER.info("Link is not proper for batch and parameters are missing")
            self.assert_code(response,400)
            
    
    async def test_rest_api_check_batches_count(self, setup):
        """Tests batches count from batch list 
        """
        address = setup['address']
        expected_count=setup['expected_batch_length']
        count=0
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batches'.format(address), raise_for_status=True) as data:
                    response = await data.json()

            for batch in enumerate(response['data']):
                count = count+1
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
        
        self.assert_count(expected_count,count)
       
class TestBatchGet(RestApiBaseTest):
    async def test_api_get_batch_id(self, setup):
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
        expected_length = setup['expected_batch_length']
        batch_ids = setup['batch_ids']
        expected_id = batch_ids[0]
        payload = setup['payload']
        address = setup['address']
        
        expected_link = '{}/batches/{}'.format(address, expected_batches[0])
                                                             
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batches/{}'.format(address,expected_id), 
                                       raise_for_status=True) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info("Rest Api is Unreachable")
                                      
        batches = response['data']
        
        self.assert_check_batch_seq(batches, expected_batches, 
                                    expected_txns, payload, 
                                    signer_key)
        self.assert_valid_link(response, expected_link)
                
    async def test_api_get_bad_batch_id(self, setup):
        """verifies that GET /batches/{bad_batch_id} 
           is unreachable with bad head parameter 
        """  
        address = setup['address']                        
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batches/{}'.format(address,BAD_ID)) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
          
        self.assert_valid_error(response, INVALID_RESOURCE_ID)
  
class TestBatchStatusesList(RestApiBaseTest):
    """This class tests the batch status list with different parameters
    """
    async def test_api_post_batch_status_15ids(self, setup):   
        """verifies that POST /batches_statuses with more than 15 ids
        """
        LOGGER.info("Starting test for batch with bad head parameter")
        batch_ids = setup['batch_ids']
        address = setup['address']
        data_str=json.dumps(batch_ids).encode()
        headers = {'content-type': 'application/json'}
        
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.post(url='{}/batch_statuses'.format(address),
                                        data=data_str,headers=headers) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
    
    
    async def test_api_post_batch_status_10ids(self,setup):   
        """verifies that POST /batches_status with less than 15 ids
        """
        LOGGER.info("Starting test for post batch statuses with less than 15 ids")
        batch_ids = setup['batch_ids']
        address = setup['address']
        data_str=json.dumps(batch_ids).encode()
        headers = {'content-type': 'application/json'}
                        
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.post(url='{}/batch_statuses'.format(address),
                                        data=data_str,headers=headers) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
                

    async def test_api_get_batch_statuses(self,setup):
        signer_key = setup['signer_key']
        address = setup['address']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        status = "COMMITTED"
        expected_link = '{}/batch_statuses?id={}'.format(address, expected_batches[0])
        params = {'id': expected_batches[0]}
        
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batch_statuses'.format(address),
                                        params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
                            
        self.assert_status(response,status)
        self.assert_valid_link(response, expected_link)
    
    async def test_api_get_batch_statuses_many_ids(self,setup):
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        address = setup['address']
        status = "COMMITTED"
        batches = ",".join(expected_batches)
        params = {'id': batches}

        expected_link = '{}/batch_statuses?id={}'.format(address, batches)
        
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batch_statuses'.format(address),
                                        params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
                                                                                       
        self.assert_status(response,status)
        self.assert_valid_link(response, expected_link)
    
    async def test_api_get_batch_statuses_bad_id(self,setup):
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        address = setup['address']
        params = {'id': BAD_ID}
                                         
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batch_statuses'.format(address),
                                        params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
                                      
        self.assert_valid_error(response, INVALID_RESOURCE_ID)
    
    async def test_api_get_batch_statuses_invalid_query(self,setup):
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        address = setup['address']
        
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batch_statuses'.format(address)) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
                                                              
        self.assert_valid_error(response, STATUS_ID_QUERY_INVALID)
        
    async def test_api_get_batch_statuses_wait(self,setup):
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        address = setup['address']
        status = "COMMITTED"

        expected_link = '{}/batch_statuses?id={}&wait={}'.format(address, expected_batches[0], WAIT)
        
        params = {'id': expected_batches[0], 'wait':WAIT}
                                         
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batch_statuses'.format(address),
                                        params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
                                         
                                              
        self.assert_status(response,status)
        self.assert_valid_link(response, expected_link)
    
    
    async def test_api_get_batch_statuses_invalid(self, invalid_batch):
        expected_batches = invalid_batch['expected_batches']
        address = invalid_batch['address']
        status = "INVALID"
        expected_link = '{}/batch_statuses?id={}'.format(address, expected_batches[0])
        params = {'id': expected_batches[0]}
        
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batch_statuses'.format(address),
                                        params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
                                                       
        self.assert_status(response,status)
        self.assert_valid_link(response, expected_link)
        
    
    async def test_api_get_batch_statuses_unknown(self, setup):
        address = setup['address']
        expected_batches = setup['expected_batches']
        batch = expected_batches[0]
        unknown_batch = batch[:1] + "b" + batch[1+1:]
        status = "UNKNOWN"
        params = {'id': unknown_batch}

        expected_link = '{}/batch_statuses?id={}'.format(address, unknown_batch)
                                         
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batch_statuses'.format(address),
                                        params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
                                              
        self.assert_status(response,status)
        self.assert_valid_link(response, expected_link)
    
    async def test_api_get_batch_statuses_default_wait(self,setup):
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        address = setup['address']
        status = "COMMITTED"
        expected_link = '{}/batch_statuses?id={}&wait=300'.format(address, expected_batches[0])
        params = {'id': expected_batches[0], 'wait':300}
                                         
        try:
            async with aiohttp.ClientSession() as session:        
                async with session.get(url='{}/batch_statuses'.format(address),
                                        params=params) as data:
                    response = await data.json()
        except aiohttp.client_exceptions.ClientResponseError as error:
            LOGGER.info(error)
                                              
        self.assert_status(response,status)
        self.assert_valid_link(response, expected_link)