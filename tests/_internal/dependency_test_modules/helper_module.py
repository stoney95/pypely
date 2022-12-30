import requests

from .yet_another_module import another_helper
from .a.very.nested.package.deep_module import print_low_level

def try_request():
    another_helper()
    print_low_level()
    try:
        requests.get("localhost: 3000")
    except:
        pass