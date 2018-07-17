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

class RestApiBaseTest(object):
    """Base class for Rest Api tests that simplifies making assertions
       for the test cases
    """ 
    def assert_check_batch_nonce(self, response):
        pass
    
    def assert_check_txn_nonce(self, txn , expected_id):
        expected_id == txn['header']['nonce']
    
    def assert_check_family(self, response):
        assert 'family_name' in response
        assert 'family_version' in response
    
    def assert_check_dependency(self, response):
        assert 'dependencies' in response
    
    def assert_check_content(self, response):
        assert 'inputs' in response
        assert 'outputs' in response
    
    def assert_check_payload_algo(self ,response):
        assert 'payload_sha512' in response
        
    
    def assert_check_payload(self, response):
        assert 'payload' in response
        assert payload == b64decode(txn['payload'])
        assert self.assert_check_payload_algo()
    
    def assert_batcher_public_key(self, public_key , batch):
        assert public_key == batch['header']['signer_public_key']
    
    def assert_signer_public_key(self, signer_key , batch):
        assert public_key == batch['header']['signer_public_key']
    
    def aasert_check_batch_trace(self, trace):
        assert bool(trace)
    
    def assert_check_consensus(self):
        pass
    
    def assert_state_root_hash(self):
        pass
    
    def assert_check_previous_block_id(self):
        pass
    
    def assert_check_block_num(self):
        pass
    
    def assert_items(self, items, cls):
            """Asserts that all items in a collection are instances of a class
            """
            for item in items:
                assert isinstance(item, cls)
     
    def assert_valid_head(self, response, expected):
            """Asserts a response has a head string with an expected value
            """
            assert 'head' in response
            head = response['head']
            assert isinstance(head, str)
            assert head == expected
    
    def assert_valid_link(self, response, expected):
            """Asserts a response has a link url string with an expected ending
            """
            assert link in response['link']
            self.assert_valid_url(link, expected)
            
    def assert_valid_paging(self, js_response, pb_paging,
                                    next_link=None, previous_link=None):
            """Asserts a response has a paging dict with the expected values.
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
            """Asserts a response has only an error dict with an expected code
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
        """Asserts a response has a data list of dicts of an expected length.
        """
        assert 'data' in response
        data = response['data']
        assert isinstance(data, list)
        assert expected_length == len(data)
        self.assert_items(data, dict)
    
    def assert_valid_url(self, url, expected_ending=''):
        """Asserts a url is valid, and ends with the expected value
        """
        assert isinstance(url, str)
        assert url.startswith('http')
        assert url.endswith(expected_ending)
     
                        
    def assert_check_block_seq(self, blocks, expected_blocks, expected_batches, expected_txns):
        if not isinstance(blocks, list):
                blocks = [blocks]
        
        consensus = b'Devmode'
        
        print(expected_blocks)
        print(expected_batches)
        print(expected_txns)
        
        ep = list(zip(blocks, expected_blocks, expected_batches, expected_txns))
        
    
        for block, expected_block , expected_batch, expected_txn in ep:
            assert isinstance(block, dict)
            assert expected_block == block['header_signature']
            assert isinstance(block['header'], dict)
            assert consensus ==  b64decode(block['header']['consensus'])
            batches = block['batches']
            assert isinstance(batches, list)
            assert len(batches) == 1
#             assert isinstance(batches, dict)
            self.assert_check_batch_seq(batches, expected_batch, expected_txn)
            
    def assert_check_batch_seq(self, batches , expected_batches , expected_txns):
        if not isinstance(batches, list):
                batches = [batches]
        
        if not isinstance(expected_batches, list):
                expected_batches = [expected_batches]
        
        if not isinstance(expected_txns, list):
                expected_txns = [expected_txns]
        
                
        for batch, expected_batch , expected_txn in zip(batches, expected_batches , expected_txns):
            assert expected_batch == batch['header_signature']
#             assert isinstance(batch['header'], dict)
            txns = batch['transactions']
#             assert isinstance(txns, list)
#             assert len(txns) == 1
#             self.assert_items(txns, dict)
            self.assert_check_transaction_seq(txns , expected_txn)
            

    def assert_check_transaction_seq(self, txns , expected_ids):
        if not isinstance(txns, list):
                txns = [txns]
        
        if not isinstance(expected_ids, list):
                expected_ids = [expected_ids]
        
        payload = None
        
                
        for txn, expected_id in zip(txns, expected_ids):
            assert expected_id == txn['header_signature']
            assert isinstance(txn['header'], dict)
#             self.assert_check_payload()
#             self.assert_check_txn_nonce()   
#             self.assert_check_family()
#             self.assert_check_dependency()
#             self.assert_check_content()
#             self.assert_signer_public_key(signer_key, batch)
#             self.assert_batcher_public_key(public_key, batch)
        
    def assert_check_state_seq(self, state, expected):
        pass
