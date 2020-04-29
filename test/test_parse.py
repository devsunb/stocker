import os
import unittest

from stocker.util.parse import parse_config, parse_headers_string


class TestParse(unittest.TestCase):
    def test_parse_config(self):
        path = 'test_parse_config.yaml'
        test_config_text = 'a: "a"\nb: 1\nc: True'
        test_config = {'a': 'a', 'b': 1, 'c': True}
        with open(path, 'w') as f:
            f.write(test_config_text)
        self.assertDictEqual(test_config, parse_config(path))
        os.remove(path)

    def test_parse_headers_string(self):
        test_headers_string = 'a: a\nb: 0:1:2'
        test_headers = {'a': 'a', 'b': '0:1:2'}
        self.assertDictEqual(test_headers, parse_headers_string(test_headers_string))
