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
import hashlib

from google.protobuf.json_format import MessageToDict


from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory

from sawtooth_validation.message_factory.intkey_message_factory\
                        import IntkeyMessageFactory

from sawtooth_validation.val_factory import Transaction


class ApiTxns(Transaction):
    def __init__(self,signer):
        signer=self.get_signer()
        self.factory=IntkeyMessageFactory(signer=signer)
        
    def get_signer(self):
        context = create_context('secp256k1')
        private_key = context.new_random_private_key()
        signer = CryptoFactory(context).new_signer(private_key)
        return signer
    
    def create_batch(self,txns):
        return self.factory._create_batch(txns)
    
    def _create_txn(self,txn):
        return self.factory.create_payload(address,payload)
        
    def _create_empty_txn(self):
        signer = get_signer()
        header = BatchHeader(
            signer_public_key=signer.get_public_key().as_hex(),
            transaction_ids=[])
    
        header_bytes = header.SerializeToString()
    
        signature = signer.sign(header_bytes)
    
        batch = Batch(
            header=header_bytes,
            transactions=[],
            header_signature=signature)
        
        return batch
    
    def _create_invalid_txn(self):
        payload=self.payload
        signer = get_signer()
        data = {}
        expected_trxns  = {}
        expected_batches = []
        address = _get_client_address()
        
        LOGGER.info("Creating intkey transactions with set operations")
        
        txns = [
            create_invalid_intkey_transaction("set", [] , 50 , signer),
        ]
        
        for txn in txns:
            dict = MessageToDict(
                    txn,
                    including_default_value_fields=True,
                    preserving_proto_field_name=True)
                    
            expected_trxns['trxn_id'] = [dict['header_signature']]
    
        
        LOGGER.info("Creating batches for transactions 1trn/batch")
    
        batches = [create_batch([txn], signer) for txn in txns]
        
        for batch in batches:
            dict = MessageToDict(
                    batch,
                    including_default_value_fields=True,
                    preserving_proto_field_name=True)
    
            batch_id = dict['header_signature']
            expected_batches.append(batch_id)
        
        data['expected_txns'] = expected_trxns['trxn_id'][::-1]
        data['expected_batches'] = expected_batches[::-1]
        data['address'] = address
    
        post_batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]
        
        for batch in post_batch_list:
            try:
                response = post_batch(batch)
            except urllib.error.HTTPError as error:
                LOGGER.info("Rest Api is not reachable")
                response = json.loads(error.fp.read().decode('utf-8'))
                LOGGER.info(response['error']['title'])
                LOGGER.info(response['error']['message'])