import pytest
import logging
import json
import urllib.request
import urllib.error
import base64
import argparse
import cbor
import subprocess
import shlex
import requests
import hashlib
import os


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

def get_blocks():
    response = query_rest_api('/blocks')
    return response['data']

def get_batches(head_id=None , id=None , start=None , limit=None , reverse=None):  
    if all(v is not None for v in [head_id , id]):
        response = query_rest_api('/batches?head={}&id={}'.format(head_id , id))
        return response
    if all(v is not None for v in [start , limit]):
        response = query_rest_api('/batches?start={}&limit={}'.format(start , limit))
        return response
    if limit is not None:
        response = query_rest_api('/batches?limit=%s'% limit)
        return response 
    if start is not None:
        response = query_rest_api('/batches?start=%s'% start)
        return response 
    if head_id is not None:
        response = query_rest_api('/batches?head=%s'% head_id)
        return response 
    if id is not None:
        response = query_rest_api('/batches?id=%s'% id)
        return response
    if reverse:
        response = query_rest_api('/batches?reverse')
        return response
    else:
        response = query_rest_api('/batches')
        return response

def get_batch(batch_id):
    response = query_rest_api('/batches/%s' % batch_id)
    return response['data']

def get_transactions():
    response = query_rest_api('/transactions')
    return response['data']

def get_transaction(transaction_id):
    response = query_rest_api('/transactions/%s' % transaction_id)
    return response['data']

def get_state_list(head_id=None , id=None , start=None , limit=None , reverse=None):
    if all(v is not None for v in [head_id , id]):
        response = query_rest_api('/state?head={}&id={}'.format(head_id , id))
        return response
    if all(v is not None for v in [start , limit]):
        response = query_rest_api('/state?start={}&limit={}'.format(start , limit))
        return response
    if limit is not None:
        response = query_rest_api('/state?limit=%s'% limit)
        return response 
    if start is not None:
        response = query_rest_api('/state?start=%s'% start)
        return response 
    if head_id is not None:
        response = query_rest_api('/state?head=%s'% head_id)
        return response 
    if id is not None:
        response = query_rest_api('/state?id=%s'% id)
        return response
    if reverse:
        response = query_rest_api('/state?reverse')
        return response
    else:
        response = query_rest_api('/state')
        return response

def get_state(address):
    response = query_rest_api('/state/%s' % address)
    return response

def post_batch(batch):
    headers = {'Content-Type': 'application/octet-stream'}

    response = query_rest_api(
        '/batches', data=batch, headers=headers)
    
    response = submit_request('{}&wait={}'.format(response['link'], WAIT))
    return response

def query_rest_api(suffix='', data=None, headers=None):
    if headers is None:
        headers = {}
    url = _get_client_address() + suffix
    return submit_request(urllib.request.Request(url, data, headers))

def submit_request(request):
    response = urllib.request.urlopen(request).read().decode('utf-8')
    return json.loads(response)

def _delete_genesis():
    folder = '/var/lib/sawtooth'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def _get_node_chain(node_list):
    chain_list = []
    for node in node_list:
        try:
            result = requests.get(node + "/blocks").json()
            chain_list.append(result['data'])
        except:
            LOGGER.warning("Couldn't connect to %s REST API", node)
    return chain_list
    
def check_for_consensus(chains , block_num):
    LOGGER.info("Checking Consensus on block number %s" , block_num)
    blocks = []
    for chain in chains:
        if chain is not None:
            block = chain[-(block_num + 1)]
            blocks.append(block)
        else:
            return False
    block0 = blocks[0]
    for block in blocks[1:]:
        if block0["header_signature"] != block["header_signature"]:
            LOGGER.error("Validators not in consensus on block %s", block_num)
            LOGGER.error("BLOCK DUMP: %s", blocks)
            return False
        else:
            LOGGER.info('Validators in Consensus on block number %s' , block_num)
    return True


def _get_node_list():
    client_address = _get_client_address()
    node_list = [_make_http_address(peer) for peer in _get_peers_list(client_address)]
    node_list.append(_get_client_address())
    return node_list
        

def _get_peers_list(rest_client, fmt='json'):
    cmd_output = _run_peer_command(
        'sawtooth peer list --url {} --format {}'.format(
            rest_client,
            fmt))

    if fmt == 'json':
        parsed = json.loads(cmd_output)

    elif fmt == 'csv':
        parsed = cmd_output.split(',')

    return set(parsed)

def _get_node_chains(node_list):
    chain_list = []
    for node in node_list:
        try:
            result = requests.get(node + "/blocks").json()
            chain_list.append(result['data'])
        except:
            LOGGER.warning("Couldn't connect to %s REST API", node)
    return chain_list
    
def check_for_consensus(chains , block_num):
    LOGGER.info("Checking Consensus on block number %s" , block_num)
    blocks = []
    for chain in chains:
        if chain is not None:
            block = chain[-(block_num + 1)]
            blocks.append(block)
        else:
            return False
    block0 = blocks[0]
    for block in blocks[1:]:
        if block0["header_signature"] != block["header_signature"]:
            LOGGER.error("Validators not in consensus on block %s", block_num)
            LOGGER.error("BLOCK DUMP: %s", blocks)
            return False
        else:
            LOGGER.info('Validators in Consensus on block number %s' , block_num)
    return True

def _run_peer_command(command):
    return subprocess.check_output(
        shlex.split(command)
    ).decode().strip().replace("'", '"')

def _send_cmd(cmd_str):
    LOGGER.info('Sending %s', cmd_str)

    subprocess.run(
        shlex.split(cmd_str),
        check=True)

def _make_http_address(node_number):
    node = node_number.replace('tcp' , 'http')
    node_number = node.replace('8800' , '8008')
    return node_number

def _get_client_address():  
    command = "ifconfig lo | grep 'inet addr' | cut -d ':' -f 2 | cut -d ' ' -f 1"
    node_ip = subprocess.check_output(command , shell=True).decode().strip().replace("'", '"')
    return 'http://' + node_ip + ':8008'

def _start_validator():
    LOGGER.info('Starting the validator')
    cmd = "sudo -u sawtooth sawtooth-validator -vv"
    subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    
def _stop_validator():
    LOGGER.info('Stopping the validator')
    cmd = "sudo kill -9  $(ps aux | grep 'sawtooth-validator' | awk '{print $2}')"
    subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)

def make_intkey_address(name):
    return INTKEY_ADDRESS_PREFIX + hashlib.sha512(
        name.encode('utf-8')).hexdigest()[-64:]


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


def create_intkey_transaction(verb, name, value, deps, signer):
    payload = IntKeyPayload(
        verb=verb, name=name, value=value)

    # The prefix should eventually be looked up from the
    # validator's namespace registry.
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



def _expand_block(cls, block):
    """Deserializes a Block's header, and the header of its Batches.
    """
    cls._parse_header(BlockHeader, block)
    if 'batches' in block:
        block['batches'] = [cls._expand_batch(b) for b in block['batches']]
    return block


def _expand_batch(cls, batch):
    """Deserializes a Batch's header, and the header of its Transactions.
    """
    cls._parse_header(BatchHeader, batch)
    if 'transactions' in batch:
        batch['transactions'] = [
            cls._expand_transaction(t) for t in batch['transactions']]
    return batch


def _expand_transaction(cls, transaction):
    """Deserializes a Transaction's header.
    """
    return cls._parse_header(TransactionHeader, transaction)


def _parse_header(cls, header_proto, resource):
    """Deserializes a resource's base64 encoded Protobuf header.
    """
    header = header_proto()
    try:
        header_bytes = base64.b64decode(resource['header'])
        header.ParseFromString(header_bytes)
    except (KeyError, TypeError, ValueError, DecodeError):
        header = resource.get('header', None)
        LOGGER.error(
            'The validator sent a resource with %s %s',
            'a missing header' if header is None else 'an invalid header:',
            header or '')
        raise errors.ResourceHeaderInvalid()

    resource['header'] = cls._message_to_dict(header)
    return resource

