# # Copyright 2018 Intel Corporation
# #
# # Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at
# #
# #     http://www.apache.org/licenses/LICENSE-2.0
# #
# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# # See the License for the specific language governing permissions and
# # limitations under the License.
# # ------------------------------------------------------------------------------
# 
# import pytest
# import logging
# import json
# import urllib.request
# import urllib.error
# import base64
# import argparse
# import cbor
# import subprocess
# import shlex
# import requests
# import time
# 
# 
# from sawtooth_intkey.intkey_message_factory import IntkeyMessageFactory
# from sawtooth_intkey.client_cli.intkey_workload import do_workload
# 
# from fixtures import setup
# 
# LOGGER = logging.getLogger(__name__)
# LOGGER.setLevel(logging.INFO)
# WAIT = 300
# 
# WORKLOAD_TIME = 5
# 
# BLOCK_TO_CHECK_CONSENSUS = 1
# 
# INTKEY_PREFIX = '1cf126'
# XO_PREFIX = '5b7349'
# 
# 
# pytestmark = pytest.mark.scenario
#              
# def test_rest_api_post_mul_val():
#     """Tests that transactions are submitted and committed for
#     each block that are created by submitting intkey batches
#     """
#     LOGGER.info('Starting test for batch post')
#     LOGGER.info("Creating batches")
#     batches = make_batches('abcd')
#         
#     LOGGER.info("Submitting batches to the handlers")
#     initial_state_length = len(get_state_list())
#         
#     for i, batch in enumerate(batches):
#         response = post_batch(batch)
#         block_list = get_blocks()
#         state_list = get_state_list()
#         transaction_list = get_transactions()
#         batch_ids = [block['header']['batch_ids'][0] for block in block_list]
#         state_addresses = [state['address'] for state in state_list]
#         state_head_list = [get_state(address)['head'] for address in state_addresses]
#         final_state_length= len(get_state_list())
#                  
#         if response['data'][0]['status'] == 'COMMITTED':
#             LOGGER.info('Batch is committed')           
#             assert response['data'][0]['id'] in batch_ids, "Block is not created for the given batch"
#             assert  len(set(state_head_list)) == 1, "State head is not common for all the created blocks"
#         else:
#             LOGGER.info('Batch submission failed')
#             if any(['message' in response['data'][0]['invalid_transactions'][0]]):
#                 message = response['data'][0]['invalid_transactions'][0]['message']
#                 LOGGER.info(message)
#                  
#             assert response['data'][0]['id'] not in batch_ids, "Block should not be created when batch submission fails"
#             assert initial_state_length == final_state_length, "State should not be updated when batch submission fails"
#               
# 
# def test_rest_api_mul_val_intk_xo():
#     """Tests that transactions are submitted and committed for
#     each block that are created by submitting intkey and XO batches
#     """
#     node_list = [{_get_client_address()}]
#       
#     LOGGER.info('Starting Test for Intkey and Xo as payload')
#       
#     LOGGER.info("Creating intkey batches")
#     batches = make_batches('abcd')
#       
#     LOGGER.info("Submitting intkey batches to the handlers")
#     for i, batch in enumerate(batches):
#         response = post_batch(batch)
#       
#     LOGGER.info("Creating keys for xo users")
#         
#     for username in ('aditya', 'singh'):
#         _send_cmd('sawtooth keygen {} --force'.format(username))
#             
#         
#     LOGGER.info("Submitting xo batches to the handlers")
#     
#             
#     xo_cmds = (
#             'xo create game-1 --username aditya',
#             'xo take game-1 1 --username singh',
#             'xo take game-1 4 --username aditya',
#             'xo take game-1 2 --username singh',
#         )
#         
#     for cmd in xo_cmds:
#             _send_cmd(
#                 '{} --url {} --wait {}'.format(
#                     cmd,
#                     _get_client_address(),
#                     WAIT))
#     xo_cli_cmds = (
#             'xo list',
#             'xo show game-1',
#         )
#         
#     for cmd in xo_cli_cmds:
#             _send_cmd(
#                 '{} --url {}'.format(
#                     cmd,
#                     _get_client_address()))
#       
#     xo_delete_cmds = (
#             'xo delete game-1 --username aditya',
#         )
#   
#     for cmd in xo_delete_cmds:
#         _send_cmd(
#             '{} --url {} --wait {}'.format(
#                 cmd,
#                 _get_client_address(),
#                 WAIT))
#    
#     node_list = _get_node_list()
#       
#     chains = _get_node_chain(node_list)
#     check_for_consensus(chains , BLOCK_TO_CHECK_CONSENSUS)
# 
# 
# # def test_rest_mul_val_workload():
# #     rest_client = _get_client_address()
# #     workload_process = subprocess.Popen(shlex.split(
# #             'intkey workload -u {}'.format(
# #                 rest_client)))
# # 
# #     # run workload for WORKLOAD_TIME seconds
# #     time.sleep(WORKLOAD_TIME)
# # 
# #     subprocess.run(shlex.split(
# #         'sawtooth block list --url {}'.format(rest_client)))
# 
# #     blocks = rest_client.list_blocks()
#  
# #     # if workload is working, expect at least
# #     # MINIMUM_BLOCK_COUNT blocks to have been created
# #     self.assertGreaterEqual(
# #         len(list(blocks)),
# #         MINIMUM_BLOCK_COUNT,
# #         'Not enough blocks; something is probably wrong with workload')
# # 
# #     workload_process.terminate()
