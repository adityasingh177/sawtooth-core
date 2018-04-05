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
import os
import unittest
import tempfile
import shutil


from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_cli import keygen
from sawtooth_cli.exceptions import CliException


class TestKeygen(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._parser = None
        cls._key_dir = None
        cls._priv_filename = None
        cls._pub_filename = None
        cls._key_name = 'test_key'

    def setUp(self):
        self._parser = argparse.ArgumentParser(add_help=False)
        self._key_dir = tempfile.mkdtemp()
        self._priv_filename = os.path.join(self._key_dir,
                                          self._key_name + '.priv')
        self._pub_filename = os.path.join(self._key_dir,
                                         self._key_name + '.pub')
        parent_parser = argparse.ArgumentParser(prog='test_keygen',
                                                add_help=False)
        subparsers = self._parser.add_subparsers(title='subcommands',
                                                 dest='command')
        keygen.add_keygen_parser(subparsers, parent_parser)

    def tearDown(self):
        self.remove_key_files()
        shutil.rmtree(self._key_dir)

    def _parse_keygen_command(self, *args):
        cmd_args = ['keygen']
        cmd_args += args
        return self._parser.parse_args(cmd_args)

    def test_writes_valid_key(self):
        """Remove existing test files before creating new keys.
        """
        self.remove_key_files()
        args = self._parse_keygen_command(self._key_name,
                     '--key-dir', self._key_dir)
        keygen.do_keygen(args)
        private_key = _read_signing_keys(self._priv_filename)
        self.assertIsNotNone(private_key)

    def test_wrong_directory(self):
        self.remove_key_files()
        key_dir = os.path.join(self._key_dir, "temp")
        args = self._parse_keygen_command(self._key_name, '--key-dir', key_dir)
        self.assertRaises(CliException, keygen.do_keygen, args)

    def test_default_directory(self):
        key_dir = os.path.join(os.path.expanduser('~'), '.sawtooth', 'keys')
        _test_priv_filename = os.path.join(key_dir,
                                          self._key_name + '.priv')
        shutil.rmtree(key_dir)
        args = self._parse_keygen_command('--force', self._key_name)
        keygen.do_keygen(args)
        private_key = _read_signing_keys(_test_priv_filename)
        self.assertIsNotNone(private_key)

    def test_default_directory_quiet(self):
        key_dir = os.path.join(os.path.expanduser('~'), '.sawtooth', 'keys')
        _test_priv_filename = os.path.join(key_dir,
                                          self._key_name + '.priv')
        shutil.rmtree(key_dir)
        args = self._parse_keygen_command('--force',
                                          self._key_name, '-q')
        keygen.do_keygen(args)
        private_key = _read_signing_keys(_test_priv_filename)
        self.assertIsNotNone(private_key)

    def test_force_write(self):
        """Write key files to be overwritten by test of --force option.
        """
        self.remove_key_files()
        args = self._parse_keygen_command(self._key_name,
                                           '--key-dir', self._key_dir)
        keygen.do_keygen(args)
        args = self._parse_keygen_command(self._key_name,
                                          '--key-dir', self._key_dir, '--force')
        keygen.do_keygen(args)
        private_key = _read_signing_keys(self._priv_filename)
        self.assertIsNotNone(private_key)

    def test_file_exists(self):
        """Write key files to be overwritten by test of --force option.
        """
        self.remove_key_files()
        args = self._parse_keygen_command(self._key_name,
                                           '--key-dir', self._key_dir)
        keygen.do_keygen(args)
        self.assertRaises(CliException, keygen.do_keygen, args)

    def remove_key_files(self):
        '''Removes the key files.
        '''
        try:
            os.remove(self._priv_filename)
            os.remove(self._pub_filename)
        except FileNotFoundError:
            pass

def _read_signing_keys(key_filename):
    """Reads the given file as a HEX formatted key.

    Args:
        key_filename: The filename where the key is stored.

    Returns:
        tuple (str, str): the public and private key pair

    Raises:
        CliException: If unable to read the file.
    """

    filename = key_filename

    with open(filename, 'r') as key_file:
        signing_key = key_file.read().strip()

        return Secp256k1PrivateKey.from_hex(signing_key)
