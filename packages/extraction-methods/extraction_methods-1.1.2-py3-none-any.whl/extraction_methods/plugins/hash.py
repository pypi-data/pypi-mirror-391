# encoding: utf-8
"""
..  _hash:

Hash Method
-----------
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


# Python imports
import hashlib
import logging

# Package imports
from typing import Any

from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class HashInput(Input):
    """
    Model for Hash Input.
    """

    hash_str: str = Field(
        description="string to be hashed.",
    )
    output_key: str = Field(
        description="key to output to.",
    )


class HashExtract(ExtractionMethod):
    """
    Method: ``hash``

    Description:
        Hashes input string.

    Configuration Options:
    .. list-table::

        - ``hash_str``: string to be hashed.
        - ``output_key``: key to output to.

    Example configuration:
    .. code-block:: yaml

        method: hash
          inputs:
            hash_str: $model
            output_key: hashed_terms
    """

    input_class = HashInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        body[self.input.output_key] = hashlib.md5(
            self.input.input_term.encode("utf-8"), usedforsecurity=False
        ).hexdigest()

        return body
