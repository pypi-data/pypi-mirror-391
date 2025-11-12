# encoding: utf-8
"""
..  _remove:

Remove Method
-------------
"""
__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging
import re
from collections.abc import KeysView
from typing import Any

from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class RemoveInput(Input):
    """
    Model for Remove Input.
    """

    keys: list[str] = Field(
        description="list of keys to remove.",
    )
    delimiter: str = Field(
        default=".",
        description="delimiter for nested term.",
    )


class RemoveExtract(ExtractionMethod):
    """
    Method: ``remove``

    Description:
        remove keys from body.

    Configuration Options:
    .. list-table::

        - ``keys``: ``REQUIRED`` list of keys to remove.
        - ``delimiter``: delimiter for nested key.

    Example Configuration:
    .. code-block:: yaml

        - method: remove
          inputs:
            keys:
            - hello
            - world
    """

    input_class = RemoveInput

    def matching_keys(self, keys: KeysView[str], key_regex: str) -> list[str]:
        """
        Find all keys that match regex

        :param keys: dictionary keys to test
        :type keys: KeysView
        :param key_regex: regex to test against
        :type key_regex: str

        :return: matching keys
        :rtype: list
        """

        regex = re.compile(key_regex)

        return list(filter(regex.match, keys))

    def remove_key(self, body: dict[str, Any], key_parts: list[str]) -> dict[str, Any]:
        """
        Remove nested terms

        :param body: current body
        :type body: dict
        :param key_parts: key parts seperated by delimiter
        :type key_parts: list

        :return: dict
        :rtype: update body
        """

        for key in self.matching_keys(body.keys(), key_parts[0]):

            if len(key_parts) > 1:
                body[key] = self.remove_key(body[key], key_parts[1:])

            else:
                del body[key]

        return body

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        for key in self.input.keys:
            body = self.remove_key(body, key.split(self.input.delimiter))

        return body
