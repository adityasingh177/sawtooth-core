# Copyright 2017 Intel Corporation
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

import argparse
import unittest
import logging
import time

from sawtooth_cli.rest_client import RestClient
from sawtooth_cli import batch

LOGGER = logging.getLogger(__name__)


REST_API = "rest-api:8008"



class TestBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._parser = None
        cls.REST_ENDPOINT = "http://" + REST_API
            
    def setUp(self):
        self._parser = argparse.ArgumentParser(add_help=False)
        
        self._rest_endpoint = self.REST_ENDPOINT \
            if self.REST_ENDPOINT.startswith("http://") \
            else "http://{}".format(self.REST_ENDPOINT)
        
        parent_parser = argparse.ArgumentParser(prog='test_batch',
                                                add_help=False)

        subparsers = self._parser.add_subparsers(title='subcommands',
                                                 dest='command')

        batch.add_batch_parser(subparsers, parent_parser)
    
    def _parse_batch_command(self, *args):
        cmd_args = ['batch']
        cmd_args += args
        return self._parser.parse_args(cmd_args)
        
    def test_batch_list_default(self):
        args = self._parse_batch_command('list' , '--url', self._rest_endpoint)
        time.sleep(3)
        batch.do_batch(args)
      
    def test_batch_list_csv(self):
        args = self._parse_batch_command('list' , '--url', self._rest_endpoint , '--format' , 'csv')
        time.sleep(3)
        batch.do_batch(args) 
        
    def test_batch_list_yaml(self):
        args = self._parse_batch_command('list' , '--url', self._rest_endpoint , '--format' , 'yaml')
        time.sleep(3)
        batch.do_batch(args) 
     
    def test_batch_list_json(self):
        args = self._parse_batch_command('list' , '--url', self._rest_endpoint , '--format' , 'json')
        time.sleep(3)
        batch.do_batch(args)
              
    def test_batch_show(self):
        args = self._parse_batch_command('list' , '--url', self._rest_endpoint , '--format' , 'json')
        keys = ('batch_id', 'txns', 'signer')
         
        def parse_batch_row(batch):
            return (
                batch['header_signature'],
                len(batch.get('transactions', [])),
                batch['header']['signer_public_key'])
         
         
        rest_client = RestClient(args.url, args.user)
        batches = rest_client.list_batches()
         
        time.sleep(3)
         
        data = [{k: d for k, d in zip(keys, parse_batch_row(b))}
                for b in batches]
         
        batch_id = data[0]['batch_id']
         
     
        args = self._parse_batch_command('show' , batch_id , '--url', self._rest_endpoint , '--format' , 'json')
        batch.do_batch(args) 
         
        args = self._parse_batch_command('show' , batch_id , '--url', self._rest_endpoint , '--format' , 'yaml')
        batch.do_batch(args)
     
    def test_batch_status(self):
        args = self._parse_batch_command('list' , '--url', self._rest_endpoint , '--format' , 'json')
        keys = ('batch_id', 'txns', 'signer')
           
        def parse_batch_row(batch):
            return (
                batch['header_signature'],
                len(batch.get('transactions', [])),
                batch['header']['signer_public_key'])
           
           
        rest_client = RestClient(args.url, args.user)
        batches = rest_client.list_batches()
           
        time.sleep(3)
           
        data = [{k: d for k, d in zip(keys, parse_batch_row(b))}
                for b in batches]
           
        batch_id = data[0]['batch_id']
           
       
        args = self._parse_batch_command('status' , batch_id , '--url', self._rest_endpoint , '--format' , 'json')
        batch.do_batch(args)
        args = self._parse_batch_command('status' , batch_id , '--url', self._rest_endpoint , '--format' , 'yaml')
        batch.do_batch(args)
    
    def test_batch_submit(self):
        pass
          