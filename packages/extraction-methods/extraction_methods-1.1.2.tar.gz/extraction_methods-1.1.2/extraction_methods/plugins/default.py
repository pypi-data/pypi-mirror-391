# encoding: utf-8
"""
..  _default:

Default Method
--------------
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


# Python imports
import logging
from typing import Any

from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class DefaultInput(Input):
    """
    Model for Default Method Input.
    """

    defaults: dict[str, Any] = Field(
        description="Defaults to be added.",
    )


class DefaultExtract(ExtractionMethod):
    """
    Method: ``default``

    Description:
        Takes a set of default facets.

    Configuration Options:
    .. list-table::

        - ``defaults``: Dictionary of defaults to be added

    Example configuration:
    .. code-block:: yaml

        - method: default
          inputs:
            defaults:
                mip_era: CMIP6
    """

    input_class = DefaultInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        return body | self.input.defaults  # type: ignore[no-any-return]
