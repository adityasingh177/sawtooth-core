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
import urllib.request
import urllib.error
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
import base64
import argparse
import cbor
import subprocess
import shlex
import requests
import hashlib
import os
import time
import socket
import netifaces

    
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
    
WAIT = 300


def get_blocks(head_id=None , id=None , start=None , limit=None , reverse=None):  
    if all(v is not None for v in [head_id , id]):
        response = query_rest_api('/blocks?head={}&id={}'.format(head_id , id))
        return response
    if all(v is not None for v in [start , limit]):
        response = query_rest_api('/blocks?start={}&limit={}'.format(start , limit))
        return response
    if limit is not None:
        response = query_rest_api('/blocks?limit=%s'% limit)
        return response 
    if start is not None:
        response = query_rest_api('/blocks?start=%s'% start)
        return response 
    if head_id is not None:
        response = query_rest_api('/blocks?head=%s'% head_id)
        return response 
    if id is not None:
        response = query_rest_api('/blocks?id=%s'% id)
        return response
    if reverse:
        response = query_rest_api('/blocks?reverse')
        return response
    else:
        response = query_rest_api('/blocks')
        return response


def get_batches(head_id=None , id=None , start=None , limit=None, reverse=None):  
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

def get_batch_id(batch_id):
    response = query_rest_api('/batches/%s' % batch_id)
    return response

def get_block_id(block_id):
    response = query_rest_api('/blocks/%s' % block_id)
    return response

def get_transaction_id(transaction_id):
    response = query_rest_api('/transactions/%s' % transaction_id)
    return response

def get_peers():
    response = query_rest_api('/peers')
    return response

def get_transactions(head_id=None , id=None , start=None , limit=None , reverse=None):
    if all(v is not None for v in [head_id , id]):
        response = query_rest_api('/transactions?head={}&id={}'.format(head_id , id))
        return response
    if all(v is not None for v in [start , limit]):
        response = query_rest_api('/transactions?start={}&limit={}'.format(start , limit))
        return response
    if limit is not None:
        response = query_rest_api('/transactions?limit=%s'% limit)
        return response 
    if start is not None:
        response = query_rest_api('/transactions?start=%s'% start)
        return response 
    if head_id is not None:
        response = query_rest_api('/transactions?head=%s'% head_id)
        return response 
    if id is not None:
        response = query_rest_api('/transactions?id=%s'% id)
        return response
    if reverse:
        response = query_rest_api('/transactions?reverse')
        return response
    else:
        response = query_rest_api('/transactions')
        return response

def get_state_list(head_id=None , address=None , start=None , limit=None , reverse=None):
    if all(v is not None for v in [head_id , address]):
        response = query_rest_api('/state?head={}&address={}'.format(head_id , address))
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
    if address is not None:
        response = query_rest_api('/state?address=%s'% address)
        return response
    if reverse:
        response = query_rest_api('/state?reverse')
        return response
    else:
        response = query_rest_api('/state')
        return response

def get_state_address(address):
    response = query_rest_api('/state/%s' % address)
    return response

def post_batch(batch, headers="None"):
    if headers=="True":
        headers = {'Content-Type': 'application/json'}  
    else:
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
    command = "hostname -I | awk '{print $1}'"
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


def _start_settings_tp():
    LOGGER.info('Starting settings-tp')
    cmd = " sudo -u sawtooth  settings-tp -vv "
    subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)

def _stop_settings_tp():
    LOGGER.info('Stopping the settings-tp')
    cmd = "sudo kill -9  $(ps aux | grep 'settings-tp' | awk '{print $2}')"
    subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE) 

def _create_genesis():
    LOGGER.info("creating the genesis data")
    _create_genesis_batch()
    os.chdir("/home/aditya")
    cmd = "sawadm genesis config-genesis.batch"
    subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    
    
def _create_genesis_batch():
    LOGGER.info("creating the config genesis batch")
    os.chdir("/home/aditya")
    cmd = "sawset genesis --force"
    subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    
    
def post_batch_statuses(batch):
    headers = {'content-type': 'application/json'}
    response = query_rest_api(
        '/batch_statuses', data=batch, headers=headers)
    return response

def get_batch_statuses(batch_ids=None, wait=None):
    try:
        batches = ",".join(batch_ids)
    except:
        batches = None
    
    if batches:
        if wait == 'default':
            response = query_rest_api('/batch_statuses?wait&id={}'.format(batches))
            return response
        elif wait:
            response = query_rest_api('/batch_statuses?id={}&wait={}'.format(batches,wait))
            return response
        else:
            response = query_rest_api('/batch_statuses?id=%s' % batches)
            return response       
    else:
        response = query_rest_api('/batch_statuses')
        return response
    
def get_state_limit(limit):
    response = query_rest_api('/state?limit=%s' % limit)
    return response


def get_reciepts(reciept_id):
    response = query_rest_api('/receipts?id=%s' % reciept_id)
    return response

def post_receipts(receipts):
    headers = {'Content-Type': 'application/json'}
    response = query_rest_api('/receipts', data=receipts, headers=headers)
    return response

def batch_count():
    batch_list = get_batches()
    count = len(batch_list['data'])
    try:
        next_position = batch_list['paging']['next_position']
    except:
        next_position = None
    
    while(next_position):
        batch_list = get_batches(start=next_position)
        try:
            next_position = batch_list['paging']['next_position']
        except:
            next_position = None
        
        count += len(batch_list['data'])
    return count   

def transaction_count():
    transaction_list = get_transactions()
    count = len(transaction_list['data'])
    try:
        next_position = transaction_list['paging']['next_position']
    except:
        next_position = None
    
    while(next_position):
        transaction_list = get_transactions(start=next_position)
        try:
            next_position = transaction_list['paging']['next_position']
        except:
            next_position = None
        
        count += len(transaction_list['data'])
    return count 

def _create_expected_link(expected_ids):
    for id in expected_ids:
        link = '{}/batch_statuses?id={},{}'.format(address, id)
    return link

def _get_batch_list(response):
    batch_list = response['data']
    
    try:
        next_position = response['paging']['next_position']
    except:
        next_position = None
        
    while(next_position):
        response = get_batches(start=next_position)
        data_list = response['data']
        try:
            next_position = response['paging']['next_position']
        except:
            next_position = None
                      
        batch_list += data_list
            
    return batch_list


def _get_transaction_list(response):
    transaction_list = response['data']
    
    try:
        next_position = response['paging']['next_position']
    except:
        next_position = None
        
    while(next_position):
        response = get_transactions(start=next_position)
        data_list = response['data']
        try:
            next_position = response['paging']['next_position']
        except:
            next_position = None
                      
        transaction_list += data_list
            
    return transaction_list
