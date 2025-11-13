# encoding: utf-8
"""
..  _facet-prefix:

Facet Prefix Method
-------------------
"""
__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Package imports
from typing import Any

from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class FacetPrefixInput(Input):
    """
    Model for Facet Prefix Input.
    """

    prefix: str = Field(
        description="Prefix to be added.",
    )
    keys: list[str] = Field(
        description="list of keys that require prefix.",
    )


class FacetPrefixExtract(ExtractionMethod):
    """
    Method: ``facet_prefix``

    Description:
        In some cases, you may wish add a prefix to some or all of the facets
        based on the vocabulary they're from.

    Configuration Options:
    .. list-table::

        - ``prefix``: Prefix to be added.
        - ``keys``: List of keys that require prefix.

    Example Configuration:
    .. code-block:: yaml

        - method: facet_prefix
          inputs:
            prefix: cmip6
            keys:
              - start_time
              - model
    """

    input_class = FacetPrefixInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        for term in self.input.keys:
            try:
                value = body.pop(term)
                body[f"{self.input.prefix}:{term}"] = value

            except KeyError:
                pass

        return body
