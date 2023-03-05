import requests

from .a.very.nested.package.deep_module import print_low_level
from .yet_another_module import another_helper


def try_request():
    another_helper()
    print_low_level()
    try:
        requests.get("localhost: 3000")
    except:
        pass
