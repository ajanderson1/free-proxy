from .free_proxy import validate_proxy
import random

import logging
log = logging.getLogger(__name__)

def get_first_valid_proxy(proxies) -> dict:
    """ ✅  Returns the first valid proxy from the list of passed in proxies """
    if proxies is None:
        log.error("No proxies passed in")
        raise ValueError("No proxies passed in")
    random.shuffle(proxies)
    for proxy in proxies:
        if validate_proxy(proxy):
            return proxy
    log.error("No *valid* proxies found")
    raise ValueError("No *valid* proxies found")
