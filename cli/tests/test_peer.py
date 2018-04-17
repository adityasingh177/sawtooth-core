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

import argparse
import unittest
import logging
import time

from sawtooth_cli.rest_client import RestClient
from sawtooth_cli import peer

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
        
        parent_parser = argparse.ArgumentParser(prog='test_peer',
                                                add_help=False)

        subparsers = self._parser.add_subparsers(title='subcommands',
                                                 dest='command')

        peer.add_peer_list_parser(subparsers, parent_parser)
    
    def _parse_peer_command(self, *args):
        cmd_args = ['peer']
        cmd_args += args
        return self._parser.parse_args(cmd_args)
    
    def test_peer_list(self):
        """ test for list of peers with different formats"""
        args = self._parse_peer_command('list' , '--url', self._rest_endpoint)
        time.sleep(3)
        peer.do_peer_list(args)
