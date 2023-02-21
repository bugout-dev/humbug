from typing import Any, Dict
import unittest

from . import blacklist


class TestGenerateFilterParametersByKeyFunction(unittest.TestCase):
    """
    Tests for blacklist.generate_filter_parameters_by_key_fn.
    """

    def test_exact_matches(self):
        params: Dict[str, Any] = {"good": 1, "bad": "lol"}
        blacklist_fn = blacklist.generate_filter_parameters_by_key_fn(["bad"])
        filtered_params = blacklist_fn(params)
        self.assertDictEqual(filtered_params, {"good": "1"})

    def test_case_insensitive_matches(self):
        params: Dict[str, Any] = {"good": 1, "BAD": "lol"}
        blacklist_fn = blacklist.generate_filter_parameters_by_key_fn(["Bad"])
        filtered_params = blacklist_fn(params)
        self.assertDictEqual(filtered_params, {"good": "1"})
