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
#   
import pytest
import logging
import json
import urllib.request
import urllib.error
  
from conftest import setup
from utils import get_state_list, get_reciepts, post_receipts
from base import RestApiBaseTest
from fixtures import setup_batch_multiple_transaction
  
  
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
  
pytestmark = [pytest.mark.get , pytest.mark.receipts]

RECEIPT_NOT_FOUND = 80
RECEIPT_WRONG_CONTENT_TYPE = 81
RECEIPT_BODY_INVALID = 82
RECEIPT_Id_QUERYINVALID = 83
INVALID_RESOURCE_ID = 60
  
  
class TestReceiptsList(RestApiBaseTest):
    """This class tests the receipt list with different parameters
    """
    def test_api_get_reciept_invalid_id(self):
        """Tests the reciepts after submitting invalid transaction
        """
        transaction_id="s"
        try:   
            response = get_reciepts(transaction_id)
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is Unreachable")
            response = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(response['error']['title'])
            LOGGER.info(response['error']['message'])
            assert response['error']['code'] == INVALID_RESOURCE_ID
            assert response['error']['title'] == 'Invalid Resource Id'
                 
    def test_api_get_reciepts_multiple_transactions(self, setup_batch_multiple_transaction):
        """Test the get reciepts for multiple transaction.
        """
        transaction_list=""
        li=setup_batch_multiple_transaction
        for txn in li:
            transaction_list=txn+","+transaction_list
         
        trans_list = str(transaction_list)[:-1]
        try:
            response = get_reciepts(trans_list)
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is Unreachable")
            response = json.loads(error.fp.read().decode('utf-8'))
         
        for res,txn in zip(response['data'],reversed(li)):
           assert str(res['id']) == txn
            
    def test_api_get_reciepts_single_transactions(self,setup):
        """Tests get reciepts response for single transaction"""
         
        expected_transaction=setup['expected_txns']
         
        transaction_id=str(expected_transaction)[2:-2]
        try:   
             response = get_reciepts(transaction_id)
        except urllib.error.HTTPError as error:
             LOGGER.info("Rest Api is Unreachable")
             response = json.loads(error.fp.read().decode('utf-8'))
             LOGGER.info(response['error']['title'])
             LOGGER.info(response['error']['message'])
             assert response['error']['code'] == RECEIPT_NOT_FOUND
             assert response['error']['title'] == 'Invalid Resource Id'
         
    def test_api_post_reciepts_single_transactions(self,setup):
      """Test post reciepts response for single transaction"""
          
      expected_transaction=setup['expected_txns']
         
      transaction_json=json.dumps(expected_transaction).encode()
      try:   
           response = post_receipts(transaction_json)
      except urllib.error.HTTPError as error:
           LOGGER.info("Rest Api is Unreachable")
           response = json.loads(error.fp.read().decode('utf-8'))
           LOGGER.info(response['error']['title'])
           LOGGER.info(response['error']['message'])
           assert response['error']['code'] == INVALID_RESOURCE_ID
           assert response['error']['title'] == 'Invalid Resource Id'
          
    def test_api_post_reciepts_invalid_transactions(self):
      """test reciepts post for invalid transaction"""
          
      expected_transaction="few"
      transaction_json=json.dumps(expected_transaction).encode()
      try:   
           response = post_receipts(transaction_json)
      except urllib.error.HTTPError as error:
           LOGGER.info("Rest Api is Unreachable")
           response = json.loads(error.fp.read().decode('utf-8'))
           LOGGER.info(response['error']['title'])
           LOGGER.info(response['error']['message'])
           assert response['error']['code'] == RECEIPT_BODY_INVALID
           assert response['error']['title'] == 'Bad Receipts Request'
          
    def test_api_post_reciepts_multiple_transactions(self, setup_batch_multiple_transaction):
       """Test the post reciepts response for multiple transaction.
       """
     
       transaction_list=setup_batch_multiple_transaction
       
       json_list=json.dumps(transaction_list).encode() 

       try:
           response= post_receipts(json_list)
       except urllib.error.HTTPError as error:
           LOGGER.info("Rest Api is Unreachable")
           response = json.loads(error.fp.read().decode('utf-8'))
           
       for res,txn in zip(response['data'], transaction_list):
           assert str(res['id']) == txn