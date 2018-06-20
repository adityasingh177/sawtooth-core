import pytest
import sys
import platform
import inspect
 
ALL = set("darwin linux win32".split())
 
  
def pytest_addoption(parser):
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
 
# def pytest_pycollect_makeitem(collector, name, obj):
#     if _is_coroutine(obj):
#         wrappped = pytest.mark.asyncio(obj)
#         return pytest.Function(name=name, parent=collector)
 
 
# def pytest_configure(config):
#     # register an additional marker
#     config.addinivalue_line("markers",
#         "env(name): mark test to run only on named environment")
#   
def pytest_runtest_setup(item):
    envnames = [mark.args[0] for mark in item.iter_markers(name='env')]
    option = item.config.getoption("-E")
    option = item.config.getoption("-O")
    if option:
        if option not in envnames:
            pytest.skip("test requires env in %r" % envnames)
 
       
#     supported_platforms = ALL.intersection(mark.name for mark in item.iter_markers())
#     plat = platform.platform()
#     print(platform.system())
#     print(platform.release())
#     print(platform.linux_distribution())
#     print(platform.version())
#     if supported_platforms and plat not in supported_platforms:
#         pytest.skip("cannot run on platform %s" % (plat))
