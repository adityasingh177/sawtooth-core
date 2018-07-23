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
from base64 import b64decode

CONSENSUS_ALGO = b'devmode'
FAMILY_NAME = 'intkey'
FAMILY_VERSION = '1.0'
DEFAULT_LIMIT = 100
TRACE = False
NONCE = ''


class RestApiBaseTest(object):
    """Base class for Rest Api tests that simplifies making assertions
       for the test cases
    """ 
    
    def assert_check_nonce(self, response):
        """Asserts response has nonce parameter
        """
        assert 'nonce' in response['header']
        assert response['header'] == NONCE
    
    def assert_check_family(self, response):
        """Asserts family name and versions in response
        """
        assert 'family_name' in response['header']
        assert 'family_version' in response['header']
        assert response['header']['family_name'] == FAMILY_NAME
        assert response['header']['family_version'] == FAMILY_VERSION
    
    def assert_check_dependency(self, response):
        """Asserts transaction dependencies in response
        """ 
        assert 'dependencies' in response['header']
    
    def assert_check_content(self, response):
        """Asserts response has inputs and outputs parameter
        """
        assert 'inputs' in response['header']
        assert 'outputs' in response['header']
    
    def assert_check_payload_algo(self, response):
        """Asserts payload has been created with 
           proper algorithm
        """
        assert 'payload_sha512' in response['header']
        
    def assert_check_payload(self, txn, payload):
        """Asserts payload is constructed properly
        """
        assert 'payload' in txn
        assert payload == txn['payload']
        self.assert_check_payload_algo(txn)
    
    def assert_batcher_public_key(self, public_key, response):
        """Asserts batcher public key in response
        """
        assert 'signer_public_key' in response['header']
        assert public_key == response['header']['signer_public_key']
    
    def assert_signer_public_key(self, public_key, response):
        """Asserts that signer public key is proper
        """
        assert 'signer_public_key' in response['header']
        assert public_key == batch['header']['signer_public_key']
    
    def assert_check_batch_trace(self, trace):
        """Asserts whether the response has trace parameter
        """
        assert 'trace' in response['header']
        assert bool(trace)
        assert response['header']['trace'] == TRACE
    
    def assert_check_consensus(self, response):
        """Asserts response has consensus as parameter
        """
        assert 'consensus' in response
        assert response['consensus'] == CONSENSUS_ALGO
    
    def assert_state_root_hash(self, response):
        """Asserts the response has state root hash
        """
        assert 'state_root_hash' in response
    
    def assert_previous_block_id(self, response):
        """Asserts that response has previous block id
        """
        assert 'previous_block_id' in response
    
    def assert_block_num(self, response):
        """Asserts that response has proper block number
        """
        assert 'block_num' in response
    
    def assert_items(self, items, cls):
        """Asserts that all items in a collection are instances of a class
        """
        for item in items:
            assert isinstance(item, cls)
     
    def assert_valid_head(self, response, expected):
        """Asserts a response has a head string with an 
           expected value
        """
        assert 'head' in response
        head = response['head']
        assert isinstance(head, str)
        assert head == expected
    
    def assert_valid_link(self, response, expected):
        """Asserts a response has a link url string with an 
           expected ending
        """
        assert link in response['link']
        self.assert_valid_url(link, expected)
            
    def assert_valid_paging(self, js_response, pb_paging,
                                    next_link=None, previous_link=None):
        """Asserts a response has a paging dict with the 
           expected values.
        """
        assert 'paging' in js_response
        js_paging = js_response['paging']

        if pb_paging.next:
             assert 'next_position' in js_paging

        if next_link is not None:
            assert 'next' in js_paging
            self.assert_valid_url(js_paging['next'], next_link)
        else:
            assert 'next' not in js_paging
    
    def assert_valid_error(self, response, expected_code):
        """Asserts a response has only an error dict with an 
           expected code
        """
        assert 'error' in response
        assert len(response) == 1

        error = response['error']
        assert 'code' in error
        assert error['code'] == expected_code
        assert 'title' in error
        assert  isinstance(error['title'], str)
        assert 'message' in error
        assert isinstance(error['message'], str)
    
    def assert_valid_data_list(self, response, expected_length):
        """Asserts a response has a data list of dicts of an 
           expected length.
        """
        assert 'data' in response
        data = response['data']
        assert isinstance(data, list)
        assert expected_length == len(data)
        self.assert_items(data, dict)
    
    def assert_valid_url(self, url, expected_ending=''):
        """Asserts a url is valid, and ends with the expected value
        """
        expected_ending = 'limit={}'%(DEFAULT_LIMIT)
        print(expected_ending)
        assert isinstance(url, str)
        assert url.startswith('http')
        assert url.endswith(expected_ending)
     
                        
    def assert_check_block_seq(self, blocks, expected_blocks, expected_batches, expected_txns):
        """Asserts block is constructed properly after submitting batches
        """
        if not isinstance(blocks, list):
                blocks = [blocks]
        
        consensus_algo = CONSENSUS_ALGO
        
        ep = list(zip(blocks, expected_blocks, expected_batches, expected_txns))
        
        for block, expected_block , expected_batch, expected_txn in ep:
            assert isinstance(block, dict)
            assert expected_block == block['header_signature']
            assert isinstance(block['header'], dict)
            assert consensus_algo ==  b64decode(block['header']['consensus'])
            batches = block['batches']
            assert isinstance(batches, list)
            assert len(batches) == 1
            assert isinstance(batches, dict)
            self.assert_check_batch_seq(batches, expected_batch, expected_txn)
            
    def assert_check_batch_seq(self, batches, expected_batches, expected_txns, 
                               payload, signer_key):
        """Asserts batch is constructed properly
        """
        
        if not isinstance(batches, list):
                batches = [batches]
        
        if not isinstance(expected_batches, list):
                expected_batches = [expected_batches]
        
        if not isinstance(expected_txns, list):
                expected_txns = [expected_txns]
           
        for batch, expected_batch , expected_txn in zip(batches, expected_batches , expected_txns):
            assert expected_batch == batch['header_signature']
            assert isinstance(batch['header'], dict)
            txns = batch['transactions']
            assert isinstance(txns, list)
            assert len(txns) == 1
            self.assert_items(txns, dict)
            self.assert_check_transaction_seq(txns, expected_txn, 
                                              payload[0], signer_key)
            

    def assert_check_transaction_seq(self, txns , expected_ids, 
                                     payload, signer_key):
        """Asserts transactions are constructed properly
        """        
        if not isinstance(txns, list):
                txns = [txns]
        
        if not isinstance(expected_ids, list):
                expected_ids = [expected_ids]
                                
        for txn, expected_id in zip(txns, expected_ids):
            assert expected_id == txn['header_signature']
            assert isinstance(txn['header'], dict)
            self.assert_check_payload(txn, payload)
            self.assert_check_family(txn)
            self.assert_check_nonce(txn)   
            self.assert_check_dependency(txn)
            self.assert_check_content(txn)
            self.assert_signer_public_key(txn, signer_key)
            self.assert_batcher_public_key(txn, signer_key)
        
    def assert_check_state_seq(self, state, expected):
        """Asserts state is updated properly
        """
        pass
