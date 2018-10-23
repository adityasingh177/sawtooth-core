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
import base64
import argparse
import cbor
import hashlib
import os
import time
import random
import string
import urllib


from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_rest_api.protobuf.validator_pb2 import Message
from sawtooth_rest_api.protobuf import client_batch_submit_pb2
from sawtooth_rest_api.protobuf import client_batch_pb2
from sawtooth_rest_api.protobuf import client_list_control_pb2

from sawtooth_rest_api.protobuf.batch_pb2 import Batch
from sawtooth_rest_api.protobuf.batch_pb2 import BatchList
from sawtooth_rest_api.protobuf.batch_pb2 import BatchHeader
from sawtooth_rest_api.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_rest_api.protobuf.transaction_pb2 import Transaction

from google.protobuf.message import DecodeError
from google.protobuf.json_format import MessageToDict
from utils import batch_count, transaction_count, get_batch_statuses, post_batch, get_reciepts,get_transactions, get_state_list

INTKEY_ADDRESS_PREFIX = hashlib.sha512(
    'intkey'.encode('utf-8')).hexdigest()[0:6]
    
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
    
WAIT = 300


class IntKeyPayload(object):
    def __init__(self, verb, name, value):
        self._verb = verb
        self._name = name
        self._value = value

        self._cbor = None
        self._sha512 = None

    def to_hash(self):
        return {
            'Verb': self._verb,
            'Name': self._name,
            'Value': self._value
        }

    def to_cbor(self):
        if self._cbor is None:
            self._cbor = cbor.dumps(self.to_hash(), sort_keys=True)
        return self._cbor

    def sha512(self):
        if self._sha512 is None:
            self._sha512 = hashlib.sha512(self.to_cbor()).hexdigest()
        return self._sha512
    
class Transactions:
    def __init__(self, invalidtype):
        self.signer = get_signer()
        self.data = {}
        self.invalidtype = invalidtype
        
    def get_batch_valinv_txns(self):
        """Setup method for posting batches and returning the 
           response
        """
        txns = [
            self.create_intkey_transaction("set",[],30, self.signer),
            self.create_intkey_transaction("set",[],30, self.signer),
            self.create_invalid_intkey_transaction("set",[],30, self.signer, self.invalidtype),
        ]
        self.data = self.get_txns_commit_data(txns,self.signer, self.data)
        return self.data

    def get_batch_invval_txns(self):
        """Setup method for posting batches and returning the 
           response
        """
        txns = [
            self.create_invalid_intkey_transaction("set",[],30, self.signer, self.invalidtype),
            self.create_intkey_transaction("set",[],30, self.signer),
            self.create_intkey_transaction("set",[],30, self.signer),
        ]
        self.data = self.get_txns_commit_data(txns,self.signer, self.data)
        return self.data
        
    def get_batch_invalid_txns(self):
        """Setup method for posting batches and returning the 
           response
        """  
          
        txns = [
                self.create_invalid_intkey_transaction("set",[],30, self.signer, self.invalidtype),
                self.create_invalid_intkey_transaction("set",[],30, self.signer, self.invalidtype),
                self.create_invalid_intkey_transaction("set",[],30, self.signer, self.invalidtype),
            ]

        self.data = self.get_txns_commit_data(txns,self.signer, self.data)
        return self.data
    
    def get_batch_valid_one_txns(self):
        """Setup method for posting batches and returning the 
           response
        """
        txns = [
            self.create_intkey_transaction("set",[],30, self.signer),
        ]
        self.data = self.get_txns_commit_data(txns,self.signer, self.data)
        return self.data
    
    def get_batch_valid_txns(self):
        """Setup method for posting batches and returning the 
           response
        """
        txns = [
            self.create_intkey_transaction("set",[],30, self.signer),
            self.create_intkey_transaction("set",[],30, self.signer),
            self.create_intkey_transaction("set",[],30, self.signer),
        ]
        self.data = self.get_txns_commit_data(txns,self.signer, self.data)
        return self.data
    
    def get_batch_same_txns(self):
        """Setup method for posting batches and returning the 
           response
        """
        txns = [
            self.create_intkey_same_transaction("set",[],30, self.signer),
            self.create_intkey_same_transaction("set",[],30, self.signer),
            self.create_intkey_same_transaction("set",[],30, self.signer),
        ]
        self.data = self.get_txns_commit_data(txns,self.signer, self.data)
        return self.data
    
    def get_batch_invalid_txns_fam_name(self):
        """Setup method for posting batches and returning the 
           response
        """  
          
        txns = [
                self.create_invalid_intkey_transaction("set",[],30, self.signer, self.invalidtype),
                self.create_invalid_intkey_transaction("set",[],30, self.signer, self.invalidtype),
                self.create_invalid_intkey_transaction("set",[],30, self.signer, self.invalidtype),
            ]

        self.data = self.get_txns_commit_data(txns,self.signer, self.data)
        return self.data
         
    def get_txns_commit_data(self, txns, signer, data):
        """Setup method for posting batches and returning the 
           response
        """
        expected_trxn_ids  = []
        expected_batch_ids = []
        expected_trxns  = {}
        expected_batches = []
        initial_batch_length = batch_count()
        initial_transaction_length = transaction_count()
    
        LOGGER.info("Creating intkey transactions with set operations")
        
        for txn in txns:
            dict = MessageToDict(
                    txn,
                    including_default_value_fields=True,
                    preserving_proto_field_name=True)
    
            trxn_id = dict['header_signature']
            expected_trxn_ids.append(trxn_id)
        
        self.data['expected_trxn_ids'] = expected_trxn_ids
        expected_trxns['trxn_id'] = [dict['header_signature']]
        expected_trxns['payload'] = [dict['payload']]
        #print(expected_trxns['trxn_id'])
        print(expected_trxns['payload'])
        
    
        LOGGER.info("Creating batches for transactions 3trn/batch")
    
        batches = [create_batch(txns, signer)]
        for batch in batches:
            dict = MessageToDict(
                    batch,
                    including_default_value_fields=True,
                    preserving_proto_field_name=True)
    
            batch_id = dict['header_signature']
            expected_batches.append(batch_id)
        length_batches = len(expected_batches)
        length_transactions = len(expected_trxn_ids)
        data['expected_txns'] = expected_trxns['trxn_id'][::-1]
        
        post_batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]
        try:
            for batch in post_batch_list:
                response = post_batch(batch)
                batch_id = dict['header_signature']
                expected_batches.append(batch_id)
                self.data['response'] = response['data'][0]['status'] 
                print(response)
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is not reachable")
            json_data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(json_data['error']['title'])
            LOGGER.info(json_data['error']['message']) 
            LOGGER.info(json_data['error']['code'])             
            self.data['code'] = json_data['error']['code'] 

        self.state_addresses = [state['address'] for state in get_state_list()['data']]
        self.data['state_address'] = self.state_addresses
        self.data['initial_batch_length'] = initial_batch_length
        self.data['initial_trn_length'] = initial_transaction_length
        self.data['expected_batch_length'] = initial_batch_length + length_batches
        self.data['expected_trn_length'] = initial_transaction_length + length_transactions
        return self.data   
    
    def create_intkey_transaction(self, verb, deps, count, signer):
            words = random_word_list(count)
            name=random.choice(words)    
            payload = IntKeyPayload(
                verb=verb,name=name,value=21)

            addr = make_intkey_address(name)
            data = self.get_txns_data(addr,deps, payload)
            return data
    def create_intkey_same_transaction(self, verb, deps, count, signer):
            name='a'   
            payload = IntKeyPayload(
                verb=verb,name=name,value=1)
        
            addr = make_intkey_address(name)
            data = self.get_txns_data(addr,deps, payload)
            return data
        
    def create_invalid_intkey_transaction(self, verb, deps, count, signer, invalidtye):
        words = random_word_list(count)
        name=random.choice(words) 
        
        if invalidtye=="addr":  
            payload = IntKeyPayload(
                verb=verb,name=name,value=1)
            
            INVALID_INTKEY_ADDRESS_PREFIX = hashlib.sha512(
            'invalid'.encode('utf-8')).hexdigest()[0:6]
        
            addr = INVALID_INTKEY_ADDRESS_PREFIX + hashlib.sha512(
                name.encode('utf-8')).hexdigest()[-64:]
                
        if invalidtye=="invaddr":  
            payload = IntKeyPayload(
                verb=verb,name=name,value=1)
            
            INVALID_INTKEY_ADDRESS_PREFIX = hashlib.sha512(
            'invalid'.encode('utf-8')).hexdigest()[0:6]
        
            addr = INVALID_INTKEY_ADDRESS_PREFIX + hashlib.sha512(
                name.encode('utf-8')).hexdigest()[-62:]
            
        elif invalidtye=="min":   
            payload = IntKeyPayload(
                verb=verb,name=name,value=-1)
            addr = make_intkey_address(name)
        
        elif invalidtye=="str":    
            payload = IntKeyPayload(
                verb=verb,name=name,value="str")
            addr = make_intkey_address(name)
            
        elif invalidtye=="max":    
            payload = IntKeyPayload(
                verb=verb,name=name,value=4294967296)
            addr = make_intkey_address(name)
            
        elif invalidtye=="attr":    
            payload = IntKeyPayload(
                verb="verb",name=name,value=1)
            addr = make_intkey_address(name)
            
        elif invalidtye=="fn":    
            payload = IntKeyPayload(
                verb="verb",name=name,value=1)
            addr = make_intkey_address(name)
            header = TransactionHeader(
            signer_public_key=self.signer.get_public_key().as_hex(),
            family_name='abcd',
            family_version='1.0',
            inputs=[addr],
            outputs=[addr],
            dependencies=deps,
            payload_sha512=payload.sha512(),
            batcher_public_key=self.signer.get_public_key().as_hex())
    
            header_bytes = header.SerializeToString()
    
            signature = self.signer.sign(header_bytes)
    
            transaction = Transaction(
                header=header_bytes,
                payload=payload.to_cbor(),
                header_signature=signature)
            return transaction
            
        data = self.get_txns_data(addr,deps, payload)
        return data
   
    def get_txns_data(self, addr, deps, payload):
    
        header = TransactionHeader(
            signer_public_key=self.signer.get_public_key().as_hex(),
            family_name='intkey',
            family_version='1.0',
            inputs=[addr],
            outputs=[addr],
            dependencies=deps,
            payload_sha512=payload.sha512(),
            batcher_public_key=self.signer.get_public_key().as_hex())
    
        header_bytes = header.SerializeToString()
    
        signature = self.signer.sign(header_bytes)
    
        transaction = Transaction(
            header=header_bytes,
            payload=payload.to_cbor(),
            header_signature=signature)
    
        return transaction
    

def create_intkey_transaction(verb, deps, count, signer):
    words = random_word_list(count)
    name=random.choice(words)    
    payload = IntKeyPayload(
        verb=verb,name=name,value=1)

    addr = make_intkey_address(name)

    header = TransactionHeader(
        signer_public_key=signer.get_public_key().as_hex(),
        family_name='intkey',
        family_version='1.0',
        inputs=[addr],
        outputs=[addr],
        dependencies=deps,
        payload_sha512=payload.sha512(),
        batcher_public_key=signer.get_public_key().as_hex())

    header_bytes = header.SerializeToString()

    signature = signer.sign(header_bytes)

    transaction = Transaction(
        header=header_bytes,
        payload=payload.to_cbor(),
        header_signature=signature)

    return transaction

def create_invalid_intkey_transaction(verb, deps, count, signer):
    words = random_word_list(count)
    name=random.choice(words)    
    payload = IntKeyPayload(
        verb=verb,name=name,value=1)
    
    INVALID_INTKEY_ADDRESS_PREFIX = hashlib.sha512(
    'invalid'.encode('utf-8')).hexdigest()[0:6]

    addr = INVALID_INTKEY_ADDRESS_PREFIX + hashlib.sha512(
        name.encode('utf-8')).hexdigest()[-64:]

    header = TransactionHeader(
        signer_public_key=signer.get_public_key().as_hex(),
        family_name='intkey',
        family_version='1.0',
        inputs=[addr],
        outputs=[addr],
        dependencies=deps,
        payload_sha512=payload.sha512(),
        batcher_public_key=signer.get_public_key().as_hex())

    header_bytes = header.SerializeToString()

    signature = signer.sign(header_bytes)

    transaction = Transaction(
        header=header_bytes,
        payload=payload.to_cbor(),
        header_signature=signature)

    return transaction

def create_intkey_same_transaction(verb, deps, count, signer):
    name='a'   
    payload = IntKeyPayload(
        verb=verb,name=name,value=1)

    addr = make_intkey_address(name)

    header = TransactionHeader(
        signer_public_key=signer.get_public_key().as_hex(),
        family_name='intkey',
        family_version='1.0',
        inputs=[addr],
        outputs=[addr],
        dependencies=deps,
        payload_sha512=payload.sha512(),
        batcher_public_key=signer.get_public_key().as_hex())

    header_bytes = header.SerializeToString()

    signature = signer.sign(header_bytes)

    transaction = Transaction(
        header=header_bytes,
        payload=payload.to_cbor(),
        header_signature=signature)

    return transaction


def create_batch(transactions, signer):
    transaction_signatures = [t.header_signature for t in transactions]

    header = BatchHeader(
        signer_public_key=signer.get_public_key().as_hex(),
        transaction_ids=transaction_signatures)

    header_bytes = header.SerializeToString()

    signature = signer.sign(header_bytes)

    batch = Batch(
        header=header_bytes,
        transactions=transactions,
        header_signature=signature)

    return batch

def get_signer():
    context = create_context('secp256k1')
    private_key = context.new_random_private_key()
    crypto_factory = CryptoFactory(context)
    return crypto_factory.new_signer(private_key)


def make_intkey_address(name):
    return INTKEY_ADDRESS_PREFIX + hashlib.sha512(
        name.encode('utf-8')).hexdigest()[-64:]


def random_word():
    return ''.join([random.choice(string.ascii_letters) for _ in range(0, 6)])


def random_word_list(count):
    if os.path.isfile('/usr/share/dict/words'):
        with open('/usr/share/dict/words', 'r') as fd:
            return [x.strip() for x in fd.readlines()[0:count]]
    else:
        return [random_word() for _ in range(0, count)]