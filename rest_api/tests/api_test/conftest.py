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
import sys
import platform
import inspect
import logging
import urllib
import json
import os

from payload import Setup
                  
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@pytest.fixture(scope="session")
def setup(request):
    """Setup method for posting batches and returning the 
       response
    """
    LOGGER.info("Starting Setup method for posting batches using intkey as payload")
    data = {}
    ctx = Setup() 
    tasks=[] 
    txns = ctx._create_transactions()
    batches = ctx._create_batches(txns)
    expected_data = ctx._expected_data(txns,batches)
    post_batch_list = ctx._create_batch_list(batches)    
    ctx._submit_batches(post_batch_list)
    data = ctx._post_data(txns,batches)
    data.update(expected_data)
    return data
                  
 
def pytest_addoption(parser):
    """Contains parsers for pytest cli commands
    """
    parser.addoption(
        "--get", action="store_true", default=False, help="run get tests"
    )
     
    parser.addoption(
        "--post", action="store_true", default=False, help="run post tests"
    )
     
    parser.addoption(
        "--sn", action="store_true", default=False, help="run scenario based tests"
    )
    
    parser.addoption("--batch", action="store", metavar="NAME",
        help="only run batch tests."
    )
    
    parser.addoption("--transaction", action="store", metavar="NAME",
        help="only run transaction tests."
    )
    
    parser.addoption("--state", action="store", metavar="NAME",
        help="only run state tests."
    )
    
    parser.addoption("--block", action="store", metavar="NAME",
        help="only run state tests."
    )
     
    parser.addoption("-E", action="store", metavar="NAME",
        help="only run tests matching the environment NAME."
    )
     
    parser.addoption("-N", action="store", metavar="NAME",
        help="only run tests matching the Number."
    )
     
    parser.addoption("-O", action="store", metavar="NAME",
        help="only run tests matching the OS release version."
    )

   
def pytest_collection_modifyitems(config, items):
    """Filters tests based on markers when parameters passed
       through the cli
    """
    try:
        num = int(config.getoption("-N"))
    except:
        num = None
 
    selected_items = []
    deselected_items = []
    if config.getoption("--get"):        
        for item in items:
            for marker in list(item.iter_markers()):
                if marker.name == 'get':
                    selected_items.append(item)
                else:
                    deselected_items.append(item)
 
        items[:] = selected_items[:num]
        return items
    elif config.getoption("--post"):   
        for item in items:
            for marker in item.iter_markers():
                if marker.name == 'post':
                    selected_items.append(item)
                else:
                    deselected_items.append(item)
  
        items[:] = selected_items[:num]
        return items
    elif config.getoption("--sn"):  
        for item in items:
            for marker in item.iter_markers():
                if marker.name == 'scenario':
                    selected_items.append(item)
                else:
                    deselected_items.append(item)
  
        items[:] = selected_items[:num]
        return items
    else:
        selected_items = items[:num]
        items[:] = selected_items
        return items