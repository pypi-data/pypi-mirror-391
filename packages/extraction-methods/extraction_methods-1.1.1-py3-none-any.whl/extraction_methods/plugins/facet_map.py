# encoding: utf-8
"""
..  _facet-map:

Facet Map Method
----------------
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


class FacetMapInput(Input):
    """
    Model for Facet Map Input.
    """

    term_map: dict[str, str] = Field(
        default={},
        description="Dictionary of terms to be mapped.",
    )


class FacetMapExtract(ExtractionMethod):
    """
    Method: ``facet_map``

    Description:
        In some cases, you may wish to map the header attributes to different
        facets. This method takes a map and converts the facet labels into those
        specified.

    Configuration Options:
    .. list-table::

        - ``term_map``: Dictionary of terms to map.

    Example Configuration:
    .. code-block:: yaml

        - method: facet_map
          inputs:
            term_map:
                old_key: new_key
                time_coverage_start: start_time
    """

    input_class = FacetMapInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        for old_key, new_key in self.input.term_map:
            try:
                value = body.pop(old_key)
                body[new_key] = value

            except KeyError:
                pass

        return body
