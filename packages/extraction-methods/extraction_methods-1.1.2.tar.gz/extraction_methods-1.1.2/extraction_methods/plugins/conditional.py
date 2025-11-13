# encoding: utf-8
"""
..  _conditional:

Conditional Extraction
----------------------
"""
__author__ = "Rhys Evans"
__date__ = "27 Oct 2025"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"

import logging
from typing import Any

# Third party imports
from pydantic import Field

from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    ExtractionMethodConf,
    update_input,
)
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class ConditionalInput(Input):
    """
    Model for Conditional Method Input.
    """

    condition: str = Field(
        description="Condition to decide on which methods are run.",
    )
    true_methods: list[ExtractionMethodConf] = Field(
        default=[],
        description="Extraction methods to run if contition is true.",
    )
    false_methods: list[ExtractionMethodConf] = Field(
        default=[],
        description="Extraction methods to run if contition is false.",
    )


class ConditionalExtract(ExtractionMethod):
    """
    Method: ``conditional``

    Description:
        Method to run set of extraction methods given a condition.

    Configuration Options:
    .. list-table::

        - ``condition``: Condition to decide on which methods are run
        - ``true_methods``: Extraction methods to run if contition is true
        - ``false_methods``: Extraction methods to run if contition is false

    Configuration Example:
    .. code-block:: yaml

        - method: conditional
          inputs:
            condition: $foo == bar
            true_methods:
              - method: default
                inputs:
                  defaults:
                    hello: world
            false_methods:
              - method: default
                inputs:
                  defaults:
                    hello: there
    """

    input_class = ConditionalInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        condition = ""
        for term in self.input.condition.split(" "):

            if term[0] == self.input.exists_key:
                term = body.get(term[1:], None)

                if isinstance(term, str):
                    term = f"'{term}'"

            condition += f" {term}"

        extraction_methods = (
            self.input.true_methods
            if bool(eval(condition))  # nosec B307
            else self.input.false_methods
        )

        for extraction_method in extraction_methods:
            body = extraction_method._run(body)

        return body
