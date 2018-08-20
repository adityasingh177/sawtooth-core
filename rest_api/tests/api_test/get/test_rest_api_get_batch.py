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
from utils import get_batches, get_batch_id, post_batch,\
                  get_batch_statuses, post_batch_statuses,\
                  _create_expected_link, _get_batch_list

from base import RestApiBaseTest

pytestmark = [pytest.mark.get , pytest.mark.batch]

  
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
    def test_api_get_batch_list(self, setup):
        """Tests the batch list by submitting intkey batches
        """
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
        expected_length = setup['expected_batch_length']
        payload = setup['payload']
        start = setup['start']
        limit = setup['limit']
        address = setup['address']        
            
        expected_link = '{}/batches?head={}&start={}&limit={}'.format(address,\
                         expected_head, start, limit)
        
        paging_link = '{}/batches?head={}&start={}'.format(address,\
                         expected_head, start)
                                         
        try:   
            response = get_batches()
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is Unreachable")
              
        batches = _get_batch_list(response) 
         
        self.assert_valid_data(response)
        self.assert_valid_head(response, expected_head) 
        self.assert_valid_data_list(batches, expected_length)
        self.assert_check_batch_seq(batches, expected_batches, 
                                    expected_txns, payload, 
                                    signer_key)
        self.assert_valid_link(response, expected_link)
        self.assert_valid_paging(response, expected_link)
            
    def test_api_get_batch_list_head(self, setup):   
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
                    
        try:
            response = get_batches(head_id=expected_head)
        except  urllib.error.HTTPError as error:
            LOGGER.info("Rest Api not reachable")
                  
        batches = response['data'][:-1]
                    
        self.assert_check_batch_seq(batches, expected_batches, 
                                    expected_txns, payload, 
                                    signer_key)
          
        self.assert_valid_head(response, expected_head)
        self.assert_valid_link(response, expected_link)
        self.assert_valid_paging(response, expected_link)
             
    def test_api_get_batch_list_bad_head(self, setup):   
        """Tests that GET /batches is unreachable with bad head parameter 
        """       
        LOGGER.info("Starting test for batch with bad head parameter")
                          
        try:
            batch_list = get_batches(head_id=BAD_HEAD)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
          
        self.assert_valid_error(data, INVALID_RESOURCE_ID)
  
  
    def test_api_get_batch_list_id(self, setup):   
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
           
        try:
            response = get_batches(id=expected_id)
        except:
            LOGGER.info("Rest Api is not reachable")
                       
                       
        batches = response['data'][:-1]
                    
        self.assert_check_batch_seq(batches, expected_batches, 
                                    expected_txns, payload, 
                                    signer_key)
          
        self.assert_valid_head(response, expected_head)
        self.assert_valid_link(response, expected_link)
 
    def test_api_get_batch_list_bad_id(self, setup):   
        """Tests that GET /batches is unreachable with bad id parameter 
        """
        LOGGER.info("Starting test for batch with bad id parameter")
                         
        try:
            batch_list = get_batches(head_id=BAD_ID)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
          
        self.assert_valid_error(data, INVALID_RESOURCE_ID)
          
    def test_api_get_batch_list_head_and_id(self, setup):   
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
                                  
        try:         
            response = get_batches(head_id=expected_head , id=expected_id)
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api not reachable")
             
                         
        batches = response['data'][:-1]
                                 
        self.assert_check_batch_seq(batches, expected_batches, 
                                    expected_txns, payload, 
                                    signer_key)
          
        self.assert_valid_head(response, expected_head)
        self.assert_valid_link(response, expected_link)
                           
    def test_api_get_paginated_batch_list(self, setup):   
        """Tests GET /batches is reachable using paging parameters 
        """
        LOGGER.info("Starting test for batch with paging parameters")
        batch_ids   =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        start = 1
        limit = 1
                      
        try:
            response = get_batches(start=start , limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
          
        self.assert_valid_error(data, INVALID_PAGING_QUERY)
    
    def test_api_get_batch_list_limit(self, setup):   
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
        limit = 1
        
        expected_link = '{}/batches?head={}&start={}&limit={}'.format(address,\
                         expected_head, start, limit)
                      
        try:
            response = get_batches(limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
        
        batches = response['data'][:-1]
                                 
        self.assert_check_batch_seq(batches, expected_batches, 
                                    expected_txns, payload, 
                                    signer_key)
          
        self.assert_valid_head(response, expected_head)
        self.assert_valid_link(response, expected_link)
        self.assert_valid_paging(response, expected_link)
        
        
    def test_api_get_batch_list_invalid_start(self, setup):   
        """Tests that GET /batches is unreachable with invalid start parameter 
        """
        LOGGER.info("Starting test for batch with invalid start parameter")
        batch_ids   =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        start = -1
                           
        try:  
            response = get_batches(start=start)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
          
        self.assert_valid_error(data, INVALID_PAGING_QUERY)
              
            
    def test_api_get_batch_list_invalid_limit(self, setup):   
        """Tests that GET /batches is unreachable with bad limit parameter 
        """
        LOGGER.info("Starting test for batch with bad limit parameter")
        batch_ids = setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        limit = 0
                       
        try:  
            response = get_batches(limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
          
        self.assert_valid_error(data, INVALID_COUNT_QUERY)
                     
    def test_api_get_batch_list_reversed(self, setup):   
        """verifies that GET /batches is unreachable with bad head parameter 
        """
        LOGGER.info("Starting test for batch with bad head parameter")
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        setup_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
        expected_length = setup['expected_batch_length']
        payload = setup['payload']                       
        start = setup['start']
        limit = setup['limit']
        address = setup['address']
        expected_batches = setup_batches[::-1]
             
        expected_link = '{}/batches?head={}&start={}&limit={}'.format(address,\
                         expected_head, start, limit)
         
        reverse = True
                           
        try:
            response = get_batches(reverse=reverse)
        except urllib.error.HTTPError as error:
            assert response.code == 400
          
        batches = response['data'][:-1]
        
                          
        self.assert_check_batch_seq(batches, expected_batches, 
                                    expected_txns, payload, 
                                    signer_key)
          
        self.assert_valid_head(response, expected_head)
        self.assert_valid_link(response, expected_link)
        self.assert_valid_paging(response)
    
    def test_api_get_batch_key_params(self, setup):
        """Tests/ validate the block key parameters with data, head, link and paging               
        """
        response = get_batches()
        assert 'link' in response
        assert 'data' in response
        assert 'paging' in response
        assert 'head' in response
    
    def test_api_get_batch_param_link_val(self, setup):
        """Tests/ validate the batch parameters with batches, head, start and limit
        """
        try:
            batch_list = get_batches()
            for link in batch_list:
                if(link == 'link'):
                    assert 'head' in batch_list['link']
                    assert 'start' in batch_list['link']  
                    assert 'limit' in batch_list['link'] 
                    assert 'batches' in batch_list['link']  
        except urllib.error.HTTPError as error:
            assert response.code == 400
            LOGGER.info("Link is not proper for batch and parameters are missing")
    
    def test_rest_api_check_batches_count(self, setup):
        """Tests batches count from batch list 
        """
        count =0
        try:
            batch_list = get_batches()
            for batch in enumerate(batch_list['data']):
                count = count+1
        except urllib.error.HTTPError as error:
            LOGGER.info("Batch count not able to collect")
       
class TestBatchGet(RestApiBaseTest):
    def test_api_get_batch_id(self, setup):
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
            response = get_batch_id(expected_batches[0])
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is Unreachable")
                              
        batches = response['data']
        
        self.assert_check_batch_seq(batches, expected_batches, 
                                    expected_txns, payload, 
                                    signer_key)
        self.assert_valid_link(response, expected_link)
                
    def test_api_get_bad_batch_id(self, setup):
        """verifies that GET /batches/{bad_batch_id} 
           is unreachable with bad head parameter 
        """
        try:
            batch_list = get_batches(head_id=BAD_ID)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
          
        self.assert_valid_error(data, INVALID_RESOURCE_ID)
  
class TestBatchStatusesList(RestApiBaseTest):
    """This class tests the batch status list with different parameters
    """
    def test_api_post_batch_status_15ids(self, setup):   
        """verifies that POST /batches_statuses with more than 15 ids
        """
        LOGGER.info("Starting test for batch with bad head parameter")
        data = {}
        batch_ids = setup['batch_ids']
        data['batch_ids'] = batch_ids
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        data_str=json.dumps(data['batch_ids']).encode()
                        
        try:
            response = post_batch_statuses(data_str)
            assert response['data'][0]['status'] == "COMMITTED"
        except urllib.error.HTTPError as error:
            assert response.code == 400
   
    def test_api_post_batch_status_10ids(self, setup):   
        """verifies that POST /batches_status with less than 15 ids
        """
        LOGGER.info("Starting test for batch with bad head parameter")
        data = {}
        values = []
        batch_ids = setup['batch_ids']
        data['batch_ids'] = batch_ids
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        for i in range(10):
            values.append(data['batch_ids'][i])
        data_str=json.dumps(values).encode()
                        
        try:
            response = post_batch_statuses(data_str)
            assert response['data'][0]['status'] == "COMMITTED"
        except urllib.error.HTTPError as error:
            assert response.code == 400
    
    def test_api_get_batch_statuses(self,setup):
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        address = setup['address']
        status = "COMMITTED"

        
        expected_link = '{}/batch_statuses?id={}'.format(address, expected_batches[0])
                                         
        try:   
            response = get_batch_statuses([expected_batches[0]])
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
                                      
        self.assert_status(response,status)
        self.assert_valid_link(response, expected_link)
    
    def test_api_get_batch_statuses_many_ids(self,setup):
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        address = setup['address']
        status = "COMMITTED"
        
        batches = ",".join(expected_batches)

        expected_link = '{}/batch_statuses?id={}'.format(address, batches)
                                         
        try:   
            response = get_batch_statuses(expected_batches)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
                                              
        self.assert_status(response,status)
        self.assert_valid_link(response, expected_link)
    
    def test_api_get_batch_statuses_bad_id(self,setup):
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        address = setup['address']
                                         
        try:   
            response = get_batch_statuses(BAD_ID)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
                                      
        self.assert_valid_error(data, INVALID_RESOURCE_ID)
    
    def test_api_get_batch_statuses_invalid_query(self,setup):
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        address = setup['address']
                                         
        try:   
            response = get_batch_statuses()
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
                                      
        self.assert_valid_error(data, STATUS_ID_QUERY_INVALID)
        
    def test_api_get_batch_statuses_wait(self,setup):
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        address = setup['address']
        status = "COMMITTED"

        expected_link = '{}/batch_statuses?id={}&wait={}'.format(address, expected_batches[0], WAIT)
                                         
        try:   
            response = get_batch_statuses([expected_batches[0]],WAIT)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
                                              
        self.assert_status(response,status)
        self.assert_valid_link(response, expected_link)
    
    
    def test_api_get_batch_statuses_invalid(self, invalid_batch):
        expected_batches = invalid_batch['expected_batches']
        address = invalid_batch['address']
        status = "INVALID"
 
        expected_link = '{}/batch_statuses?id={}'.format(address, expected_batches[0])
                                          
        try:   
            response = get_batch_statuses([expected_batches[0]])
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
                                               
        self.assert_status(response,status)
        self.assert_valid_link(response, expected_link)
        
    
    def test_api_get_batch_statuses_unknown(self, setup):
        address = setup['address']
        expected_batches = setup['expected_batches']
        unknown_batch = expected_batches[0]
        status = "UNKNOWN"

        expected_link = '{}/batch_statuses?id={}'.format(address, unknown_batch)
                                         
        try:   
            response = get_batch_statuses([unknown_batch])
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
                                              
        self.assert_status(response,status)
        self.assert_valid_link(response, expected_link)
    
    def test_api_get_batch_statuses_default_wait(self,setup):
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        address = setup['address']
        status = "COMMITTED"

        expected_link = '{}/batch_statuses?id={}&wait=300'.format(address, expected_batches[0])
                                         
        try:   
            response = get_batch_statuses([expected_batches[0]],300)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
                                              
        self.assert_status(response,status)
        self.assert_valid_link(response, expected_link)