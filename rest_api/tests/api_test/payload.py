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