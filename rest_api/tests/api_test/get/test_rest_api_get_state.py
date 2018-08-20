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
   
from utils import get_state_list, get_state_address
from fixtures import invalid_batch

  
from base import RestApiBaseTest
   
   
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
   
pytestmark = [pytest.mark.get, pytest.mark.state]

START = 1
LIMIT = 1
COUNT = 0
BAD_HEAD = 'f'
BAD_ID = 'f'
BAD_ADDRESS = 'f'
INVALID_START = -1
INVALID_LIMIT = 0
INVALID_RESOURCE_ID  = 60
INVALID_PAGING_QUERY = 54
INVALID_COUNT_QUERY  = 53
VALIDATOR_NOT_READY  = 15
STATE_ADDRESS_LENGTH = 70
STATE_NOT_FOUND = 75
INVALID_STATE_ADDRESS = 62
HEAD_LENGTH = 128
     
     
class TestStateList(RestApiBaseTest):
    """This class tests the state list with different parameters
    """
    def test_api_get_state_list(self, setup):
        """Tests the state list by submitting intkey batches
        """
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
               
        try:   
            response = get_state_list()
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is Unreachable")
        
        state_list = response['data'][:-1]  
                      
        self.assert_valid_head(response , expected_head)
                              
    def test_api_get_state_list_invalid_batch(self, invalid_batch):
        """Tests that transactions are submitted and committed for
        each block that are created by submitting invalid intkey batches
        """    
        batches = invalid_batch['expected_batches']
        try:
            response = get_state_list()
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
            
    def test_api_get_state_list_head(self, setup):   
        """Tests that GET /state is reachable with head parameter 
        """
        LOGGER.info("Starting test for state with head parameter")
        expected_head = setup['expected_head']
                  
        try:
            response = get_state_list(head_id=expected_head)
        except  urllib.error.HTTPError as error:
            LOGGER.info("Rest Api not reachable")
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
                  
        assert response['head'] == expected_head , "request is not correct"
           
    def test_api_get_state_list_bad_head(self, setup):   
        """Tests that GET /state is unreachable with bad head parameter 
        """       
        LOGGER.info("Starting test for state with bad head parameter")
        bad_head = 'f' 
                       
        try:
            batch_list = get_state_list(head_id=bad_head)
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is not reachable")
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
        
        self.assert_valid_error(data , INVALID_RESOURCE_ID)

      
    def test_api_get_state_list_address(self, setup):   
        """Tests that GET /state is reachable with address parameter 
        """
        LOGGER.info("Starting test for state with address parameter")
        expected_head = setup['expected_head']
        address = setup['state_address'][0]
                  
        try:
            response = get_state_list(address=address)
        except  urllib.error.HTTPError as error:
            LOGGER.info("Rest Api not reachable")
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
                  
        assert response['head'] == expected_head , "request is not correct"
           
    def test_api_get_state_list_bad_address(self, setup):   
        """Tests that GET /state is unreachable with bad address parameter 
        """       
        LOGGER.info("Starting test for state with bad address parameter")
        bad_address = 'f' 
                       
        try:
            batch_list = get_state_list(address=bad_address)
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is not reachable")
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
        
        self.assert_valid_error(data , INVALID_RESOURCE_ID)
                                           
    def test_api_get_paginated_state_list(self, setup):   
        """Tests GET /state is reachbale using paging parameters 
        """
        LOGGER.info("Starting test for state with paging parameters")
        batch_ids   =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        start = 1
        limit = 1
                    
        try:
            response = get_state_list(start=start , limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
        
        self.assert_valid_error(data , INVALID_PAGING_QUERY)
    
    def test_api_get_paginated_state_list_limit(self, setup):   
        """Tests GET /state is reachbale using paging parameters 
        """
        LOGGER.info("Starting test for state with paging parameters")
        batch_ids   =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        limit = 1
                    
        try:
            response = get_state_list(limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
        
    
    def test_api_get_paginated_state_list_start(self, setup):   
        """Tests GET /state is reachbale using paging parameters 
        """
        LOGGER.info("Starting test for state with paging parameters")
        batch_ids   =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        limit = 1
                    
        try:
            response = get_state_list(limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
        
      
    def test_api_get_state_list_bad_paging(self, setup):   
        """Tests GET /state is reachbale using bad paging parameters 
        """
        LOGGER.info("Starting test for state with bad paging parameters")
        batch_ids   =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        start = -1
        limit = -1
                    
        try:
            response = get_state_list(start=start , limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
        
        self.assert_valid_error(data , INVALID_COUNT_QUERY)

                 
    def test_api_get_state_list_invalid_start(self, setup):   
        """Tests that GET /state is unreachable with invalid start parameter 
        """
        LOGGER.info("Starting test for state with invalid start parameter")
        batch_ids   =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        start = -1
                         
        try:  
            response = get_state_list(start=start)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
        
        self.assert_valid_error(data , INVALID_PAGING_QUERY)

          
    def test_api_get_state_list_invalid_limit(self, setup):   
        """Tests that GET /state is unreachable with bad limit parameter 
        """
        LOGGER.info("Starting test for state with bad limit parameter")
        batch_ids = setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        limit = 0
                     
        try:  
            response = get_state_list(limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
        
        self.assert_valid_error(data , INVALID_COUNT_QUERY)
                     
    def test_api_get_state_list_reversed(self, setup):   
        """verifies that GET /state is unreachable with bad head parameter 
        """
        LOGGER.info("Starting test for state with bad head parameter")
        batch_ids = setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        reverse = True
                         
        try:
            response = get_state_list(reverse=reverse)
        except urllib.error.HTTPError as error:
            assert response.code == 400
                        
        assert response['paging']['start'] == None ,  "request is not correct"
        assert response['paging']['limit'] == None ,  "request is not correct"
        assert bool(response['data']) == True
    
    def test_api_get_state_data_address_prefix_namespace(self, setup):
        """Tests the state data address with 6 hex characters long 
        namespace prefix
        """   
        try:   
            for state in get_state_list()['data']:
                #Access each address using namespace prefix
                namespace = state['address'][:6]
                res=get_state_list(address=namespace)
        except urllib.error.HTTPError as error:
            LOGGER.info("Not able to access related state address using namespace prefix")
            
    def test_api_get_state_data_head_wildcard_character(self, setup):
        """Tests the state head with wildcard_character ***STL-1345***
        """   
        pass
#         try:   
#             for _ in get_state_list()['data']:
#                 expected_head = setup['expected_head'][:6]
#                 addressList = list(expected_head)
#                 addressList[2]='?'
#                 expected_head = ''.join(addressList)
#                 print("\nVALUE is: ", expected_head)
#                 res=get_state_list(head_id=expected_head)
#         except urllib.error.HTTPError as error:
#             LOGGER.info("Not able to access  ")
#             data = json.loads(error.fp.read().decode('utf-8'))
#             if data:
#                 LOGGER.info(data['error']['title'])
#                 LOGGER.info(data['error']['message'])
#                 assert data['error']['code'] == 60
#                 assert data['error']['title'] == 'Invalid Resource Id' 

                
    def test_api_get_state_data_head_partial_character(self, setup):
        """Tests the state head with partial head address ***STL-1345***
        """   
        try:   
            for _ in get_state_list()['data']:
                expected_head = setup['expected_head'][:6]
                res=get_state_list(head_id=expected_head)
        except urllib.error.HTTPError as error:
            LOGGER.info("Not able to access ")
            data = json.loads(error.fp.read().decode('utf-8'))
            if data:
                LOGGER.info(data['error']['title'])
                LOGGER.info(data['error']['message'])
                assert data['error']['code'] == 60
                assert data['error']['title'] == 'Invalid Resource Id'    
                
    def test_api_get_state_data_address_partial_character(self, setup):
        """Tests the state address with partial head address ***STL-1346***
        """   
        try:   
            for _ in get_state_list()['data']:
                expected_head = setup['expected_head'][:6]
                res=get_state_list(head_id=expected_head)
        except urllib.error.HTTPError as error:
            LOGGER.info("Not able to access ")
            data = json.loads(error.fp.read().decode('utf-8'))
            if data:
                LOGGER.info(data['error']['title'])
                LOGGER.info(data['error']['message'])
                assert data['error']['code'] == 62
                assert data['error']['title'] == 'Invalid State Address'                            
            
            
    def test_api_get_state_data_address_length(self, setup):
        """Tests the state data address length is 70 hex character long
        with proper prefix namespace
        """   
        try:
            response = get_state_list()   
            for state in get_state_list()['data']:
                #Access each address using of state
                address = len(response['data'][0]['address'])
        except urllib.error.HTTPError as error:
            LOGGER.info("State address is not 70 character long")        
        assert address == STATE_ADDRESS_LENGTH
        
        
    def test_api_get_state_data_address_with_odd_hex_value(self, setup):
        """Tests the state data address fail with odd hex character 
        address 
        """   
        try:
            response = get_state_list()   
            for state in get_state_list()['data']:
                #Access each address using of state
                address = len(response['data'][0]['address'])
                if(address%2 == 0):
                    pass
        except urllib.error.HTTPError as error:
            LOGGER.info("Odd state address is not correct")
            
    def test_api_get_state_data_address_with_reduced_length(self, setup):
        """Tests the state data address with reduced even length hex character long 
        """   
        try:
            response = get_state_list()   
            for state in get_state_list()['data']:
                #Access each address using of state
                address = response['data'][0]['address']
                nhex = address[:-4]
                get_state_list(address = nhex)
        except urllib.error.HTTPError as error:
            LOGGER.info("Reduced length data address failed to processed")        
            
                    
    def test_api_get_state_data_address_64_Hex(self, setup):
        """Tests the state data address with 64 hex give empty data 
        """   
        try:
            response = get_state_list()   
            for state in get_state_list()['data']:
                #Access each address using of state
                address = response['data'][0]['address']
                nhex = address[6:70]
                naddress = get_state_list(address = nhex)
                assert naddress['data'] == []
        except urllib.error.HTTPError as error:
            LOGGER.info("state data address with 64 hex characters not processed ")        
                    
                    
    def test_api_get_state_data_address_alter_bytes(self, setup):
        """Tests the state data address with alter bytes give empty data 
        """   
        try:
            response = get_state_list()   
            for state in get_state_list()['data']:
                #Access each address using of state
                address = response['data'][0]['address']
                nhex = address[6:8]
                naddress = get_state_list(address = nhex)
                addressList = list(naddress)
                addressList[2]='z'
                naddress = ''.join(addressList)
        except urllib.error.HTTPError as error:
            LOGGER.info("state data address with altered bytes not processed ")
            
            
    def test_api_get_state_link_val(self, setup):
        """Tests/ validate the state parameters with state, head, start and limit
        """
        try:
            state_list = get_state_list()
            for link in state_list:
                if(link == 'link'):
                    assert 'head' in state_list['link']
                    assert 'start' in state_list['link']  
                    assert 'limit' in state_list['link'] 
                    assert 'state' in state_list['link']  
        except urllib.error.HTTPError as error:
            assert response.code == 400
            LOGGER.info("Link is not proper for state and parameters are missing")
        
    def test_api_get_state_key_params(self, setup):
        """Tests/ validate the state key parameters with data, head, link and paging               
        """
        response = get_state_list()
        assert 'link' in response
        assert 'data' in response
        assert 'paging' in response
        assert 'head' in response  
    
    def test_api_get_each_state_head_length(self, setup):
        """Tests the each state head length should be 128 hex character long 
        """   
        try:   
            for _ in get_state_list()['data']:
                expected_head = setup['expected_head']
                head_len = len(expected_head)
        except urllib.error.HTTPError as error:
            LOGGER.info("State Head length is not 128 hex character long")
        assert head_len == HEAD_LENGTH 
    
    def test_rest_api_check_state_count(self, setup):
        """Tests state count from state list 
        """
        count = 0
        try:
            state_list = get_state_list()['data']
            for batch in enumerate(state_list):
                count = count+1
        except urllib.error.HTTPError as error:
            LOGGER.info("State count not able to collect") 
        
            
class TestStateGet(RestApiBaseTest):
    def test_api_get_state_address(self, setup):
        """Tests/ validate the state key parameters with data, head, link and paging               
        """
        address = setup['state_address'][0]
        try:
            response = get_state_address(address=address)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
   
    def test_api_get_bad_address(self, setup):
        """Tests /state/{bad_state_address}                
        """
        try:
            response = get_state_address(address=BAD_ADDRESS)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
          
        self.assert_valid_error(data, INVALID_STATE_ADDRESS)
