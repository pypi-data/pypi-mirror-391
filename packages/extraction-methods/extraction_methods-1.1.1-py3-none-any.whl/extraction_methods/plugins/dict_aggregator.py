# encoding: utf-8
"""
..  _dict-aggregator:

Dictionary Aggregator Method
----------------------------
"""
__author__ = "Rhys Evans"
__date__ = "24 May 2022"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"

import itertools
import logging
from typing import Any

from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input, KeyOutputKey

LOGGER = logging.getLogger(__name__)


class DictAggregatorInput(Input):
    """
    Model for Dictionary Aggregator Method Input.
    """

    input_term: str | dict[str, Any] = Field(
        default="$assets",
        description="term for method to run on.",
    )
    min: list[KeyOutputKey] = Field(
        default=[],
        description="list of terms for which the minimum of their aggregate should be returned.",
    )
    max: list[KeyOutputKey] = Field(
        default=[],
        description="list of terms for which the maximum of their aggregate should be returned.",
    )
    sum: list[KeyOutputKey] = Field(
        default=[],
        description="list of terms for which the sum of their aggregate should be returned.",
    )
    mean: list[KeyOutputKey] = Field(
        default=[],
        description="list of terms for which the mean of their summed aggregate should be returned.",
    )
    bucket: list[KeyOutputKey] = Field(
        default=[],
        description="list of terms for which the list of their aggregate should be returned.",
    )


class DictAggregatorExtract(ExtractionMethod):
    """
    Method: ``dict_aggregator``

    Description:
        Aggregate information within dictionary.

    Configuration Options:
    .. list-table::

        - ``min``: list of terms for which the minimum of their aggregate should be returned
        - ``max``: list of terms for which the maximum of their aggregate should be returned
        - ``sum``: list of terms for which the sum of their aggregate should be returned
        - ``list``: list of terms for which a list of their aggregage should be returned
        - ``mean``: list of terms for which a list of their aggregage should be returned

    Configuration Example:
    .. code-block:: yaml

        - method: dict_aggregator
          inputs:
            min:
              - start_time
            max:
              - end_time
            sum:
              - size
            list:
              - term1
              - term2
    """

    input_class = DictAggregatorInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        for value in self.input.input_term.values():
            for list_term in self.input.list_terms:
                if list_term.key in value:
                    body.setdefault(list_term.output_key, []).append(
                        value[list_term.key]
                    )

            for sum_term in itertools.chain(
                self.input.sum_terms, self.input.mean_terms
            ):
                if sum_term.key in value:
                    body.setdefault(sum_term.output_key, 0)
                    body[sum_term.output_key] += value[sum_term.key]

            for min_term in self.input.min_terms:
                if min_term.key in value and (
                    min_term.output_key not in body
                    or value[min_term.key] < body[min_term.output_key]
                ):
                    body[min_term.output_key] = value[min_term.key]

            for max_term in self.input.max_terms:
                if max_term.key in value and (
                    max_term.output_key not in body
                    or value[max_term.key] < body[max_term.output_key]
                ):
                    body[max_term.output_key] = value[max_term.key]

        for mean_term in self.input.mean_terms:
            body[mean_term.output_key] /= len(self.input.input_term)

        return body
