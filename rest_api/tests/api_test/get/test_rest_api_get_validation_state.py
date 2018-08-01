import pytest
import logging
import json
import urllib.request
import urllib.error
  
from utils import get_batches, get_blocks, get_state_list, get_transactions
 
from base import RestApiBaseTest
state_address = 70

class TestStateList(RestApiBaseTest):
    """This class tests the state list with different parameters
    """
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
        try:   
            for _ in get_state_list()['data']:
                expected_head = setup['expected_head'][:6]
                addressList = list(expected_head)
                addressList[2]='?'
                expected_head = ''.join(addressList)
                print("\nVALUE is: ", expected_head)
                res=get_state_list(head_id=expected_head)
        except urllib.error.HTTPError as error:
            LOGGER.info("Not able to access  ")
            data = json.loads(error.fp.read().decode('utf-8'))
            if data:
                LOGGER.info(data['error']['title'])
                LOGGER.info(data['error']['message'])
                assert data['error']['code'] == 60
                assert data['error']['title'] == 'Invalid Resource Id' 
                
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
                
    def test_api_get_state_data_address_wildcard_character(self, setup):
        """Tests the state address with wildcard_character ***STL-1346***
        """   
        try:   
            for _ in get_state_list()['data']:
                namespace = state['address']
                res=get_state_list(address=namespace)
                expected_head = setup['expected_head'][:6]
                addressList = list(expected_head)
                addressList[2]='?'
                expected_head = ''.join(addressList)
                print("\nVALUE is: ", expected_head)
                res=get_state_list(head_id=expected_head)
        except urllib.error.HTTPError as error:
            LOGGER.info("Not able to access  ")
            data = json.loads(error.fp.read().decode('utf-8'))
            if data:
                LOGGER.info(data['error']['title'])
                LOGGER.info(data['error']['message'])
                assert data['error']['code'] == 62
                assert data['error']['title'] == 'Invalid State Address' 
                
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
        assert address == state_address
        
        
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
            
    def test_api_get_batch_key_params(self, setup):
        """Tests/ validate the block key parameters with data, head, link and paging               
        """
        response = get_batches()
        assert 'link' in response
        assert 'data' in response
        assert 'paging' in response
        assert 'head' in response
            
    def test_api_get_block_key_params(self, setup):
        """Tests/ validate the block key parameters with data, head, link and paging               
        """
        response = get_blocks()
        assert 'link' in response
        assert 'data' in response
        assert 'paging' in response
        assert 'head' in response
        
    def test_api_get_state_key_params(self, setup):
        """Tests/ validate the state key parameters with data, head, link and paging               
        """
        response = get_state_list()
        assert 'link' in response
        assert 'data' in response
        assert 'paging' in response
        assert 'head' in response   
        
    def test_api_get_transactions_key_params(self, setup):
        """Tests/ validate the state key parameters with data, head, link and paging               
        """
        response = get_transactions()
        assert 'link' in response
        assert 'data' in response
        assert 'paging' in response
        assert 'head' in response            
