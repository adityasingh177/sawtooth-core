
class RestApiBaseTest(object):
    def assert_items(self, items, cls):
            """Asserts that all items in a collection are instances of a class
            """
            for item in items:
                assert isinstance(item, cls)
    
    def assert_has_valid_head(self, response, expected):
            """Asserts a response has a head string with an expected value
            """
            assert 'head' in response
            head = response['head']
            assert isinstance(head, str)
            assert head == expected
    
    def assert_has_valid_link(self, response, expected_ending):
            """Asserts a response has a link url string with an expected ending
            """
            assert link in response['link']
            self.assert_valid_url(link, expected_ending)
            
    
    def assert_has_valid_paging(self, js_response, pb_paging,
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
    
    def assert_has_valid_error(self, response, expected_code):
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
    
    def assert_has_valid_data_list(self, response, expected_length):
        """Asserts a response has a data list of dicts of an expected length.
        """
        assert 'data' in response
        data = response['data']
        assert isinstance(data, list)
        assert expected_length == len(data)
        self.assert_items(data, dict)
    
    def assert_has_valid_url(self, url, expected_ending=''):
        """Asserts a url is valid, and ends with the expected value
        """
        assert isinstance(url, str)
        assert url.startswith('http')
        assert url.endswith(expected_ending)
     
                        
    def aasert_check_block_seq(blocks, *expected_ids):
        if not isinstance(blocks, list):
                blocks = [blocks]
        
        consensus = None
    
        for block, expected_id in zip(blocks, expected_ids):
            assert isinstance(block, dict)
            assert expected_id == block['header_signature']
            assert isinstance(block['header'], dict)
            assert consensus ==  b64decode(block['header']['consensus'])
    
            batches = block['batches']
            assert isinstance(batches, list)
            assert len(batches) == 1
            assert isinstance(batches, dict)
            assert check_batch_seq(batches, expected_id)
        
        return True
    
    def assert_check_batch_seq(signer_key , batches , *expected_ids):
        if not isinstance(batches, list):
                batches = [batches]
    
        for batch, expected_id in zip(batches, expected_ids):
            assert expected_id == batch['header_signature']
            assert isinstance(batch['header'], dict)
            
    
            txns = batch['transactions']
            assert isinstance(txns, list)
            assert len(txns) == 1
            assert isinstance(txns, dict)
            assert check_transaction_seq(txns, expected_id) == True
        
        return True
    
    def assert_check_transaction_seq(txns , *expected_ids):
        if not isinstance(txns, list):
                txns = [txns]
        
        payload = None
    
        for txn, expected_id in zip(txns, expected_ids):
            assert expected_id == txn['header_signature']
            assert payload == b64decode(txn['payload'])
            assert isinstance(txn['header'], dict)
            assert expected_id == txn['header']['nonce']
        
        return True
    
    def assert_check_batch_nonce(self, response):
        pass
    
    def assert_check_family(self, response):
        assert 'family_name' in response
        assert 'family_version' in response
    
    def assert_check_dependency(self, response):
        pass
    
    def assert_check_content(self, response):
        pass
    
    def assert_check_payload_algo(self):
        pass
    
    def assert_check_payload(self, response):
        pass
    
    def assert_batcher_public_key(self, signer_key , batch):
        assert 'public_key' == batch['header']['signer_public_key']
    
    def assert_signer_public_key(self, signer_key , batch):
        assert 'public_key' == batch['header']['signer_public_key']
    
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