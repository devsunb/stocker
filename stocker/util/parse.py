import logging

import yaml

logger = logging.getLogger('stocker')


def parse_config(path):
    with open(path, 'r') as f:
        config = yaml.load(f.read(), Loader=yaml.Loader)
    return config


def parse_headers_string(headers_string):
    headers = {}
    for line in headers_string.split('\n'):
        key, value = line.split(': ', 1)
        headers[key] = value
    logger.debug('headers parsed: {}'.format(headers))
    return headers
