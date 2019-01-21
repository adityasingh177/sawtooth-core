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

from sawtooth_validation.message_factory.supplychain_message_factory\
                        import SupplyChainMessageFactory

from sawtooth_validation.message_factory.smallbank_message_factory\
                        import SmallBankMessageFactory

from sawtooth_validation.val_factory import Transaction

AGENT = 'ae'
PROPERTY = 'ea'
PROPOSAL = 'aa'
RECORD = 'ec'
RECORD_TYPE = 'ee'
                        
                             
class SmallBankDependentTxns(Transaction):
    def __init__(self):
        signer = self.get_signer()
        self.factory=SmallBankMessageFactory(signer=signer)

    def get_signer(self):
        context = create_context('secp256k1')
        private_key = context.new_random_private_key()
        signer = CryptoFactory(context).new_signer(private_key)
        return signer
    
    def create_batch(self,txns):
        return self.factory._create_batch(txns)
    
    def _create_txn(self,txn):
        return self.factory.create_payload(address,payload)
        
        
    def _calculate_address(self,cust1):
        NAMESPACE= hashlib.sha512('smallbank'.encode('utf-8')).hexdigest()[0:6] 
        CUST_HEX= hashlib.sha512(str(cust1).encode('utf-8')).hexdigest()[0:64]
        addr1=NAMESPACE+CUST_HEX
        return addr1
    
    def _create_account(self,cust_id,name,amount,deps=None):
        acc = self.factory.create_account(cust_id,name,amount)
        address=[self._calculate_address(cust_id)]
        print(deps)
        txn = self.factory.create_payload(address,acc,deps)
        return txn
    
    
    def _create_send_payment(self,source_cust_id, dest_cust_id,amount,deps=None):
        acc = self.factory.send_payment(source_cust_id,dest_cust_id,amount)
        print(acc)
        address1=self._calculate_address(source_cust_id)
        address2=self._calculate_address(dest_cust_id)
        address_list=[address1,address2]
        print(address_list)
        txn = self.factory.create_payload(address_list,acc,deps)
        return txn
        
    
    def _create_deposit_checking(self,cust_id,amount,deps=None):
        acc = self.factory.deposit_checking(cust_id,amount)
        print(acc)
        address=[self._calculate_address(cust_id)]
        txn = self.factory.create_payload(address,acc,deps)
        return txn
    

class SupplyChainDependentTxns(Transaction):
    def __init__(self):
        signer = self.get_signer()
        self.factory=SupplyChainMessageFactory(signer=signer)
        self.public_key = self.factory._factory.get_public_key()

    def get_signer(self):
        context = create_context('secp256k1')
        private_key = context.new_random_private_key()
        signer = CryptoFactory(context).new_signer(private_key)
        return signer
    
    def create_batch(self,txns):
        return self.factory._create_batch(txns)
    
    def _create_txn(self,txn):
        return self.factory.create_payload(address,payload)
    
        
    def _calculate_address(self):
        NAMESPACE= hashlib.sha512('supplychain'.encode('utf-8')).hexdigest()[0:6] 
        address=NAMESPACE+AGENT+hashlib.sha512(self.public_key.encode('utf-8')).hexdigest()
        return address
    
    def _create_agent(self,name,deps=None):
        agent = self.factory.create_agent(name)
        print(agent)
        address=[self._calculate_address()]
        print(deps)
        txn = self.factory.create_payload(address,agent,deps)
        return txn


class SmallBankCyclicTxns(Transaction):
    def __init__(self,signer):
        context = create_context('secp256k1')
        private_key = context.new_random_private_key()
        signer = CryptoFactory(context).new_signer(private_key)
        self.payload=SmallBankMessageFactory(signer=signer)
    
    def get_signer(self):
        context = create_context('secp256k1')
        private_key = context.new_random_private_key()
        signer = CryptoFactory(context).new_signer(private_key)
        return signer
    
    def create_batch(self,txns):
        return self.factory._create_batch(txns)
    
    def _create_txn(self,txn):
        return self.factory.create_payload(address,payload)
    

class SupplyChainCyclicTxns(Transaction):
    def __init__(self,signer):
        context = create_context('secp256k1')
        private_key = context.new_random_private_key()
        signer = CryptoFactory(context).new_signer(private_key)
        self.payload=SmallBankMessageFactory(signer=signer)
    
    def get_signer(self):
        context = create_context('secp256k1')
        private_key = context.new_random_private_key()
        signer = CryptoFactory(context).new_signer(private_key)
        return signer
    
    def create_batch(self,txns):
        return self.factory._create_batch(txns)
    
    def _create_txn(self,txn):
        return self.factory.create_payload(address,payload)

    

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