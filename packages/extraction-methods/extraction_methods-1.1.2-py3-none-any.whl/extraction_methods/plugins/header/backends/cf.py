# encoding: utf-8
"""
..  _cf-header:

CF Header Backend
-----------------
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging
from typing import Any

import cf
from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input, KeyOutputKey

LOGGER = logging.getLogger(__name__)


class CfHeaderInput(Input):
    """
    Model for CF Header Input.
    """

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )
    read_kwargs: dict[str, Any] = Field(
        default={},
        description="kwargs for cf read.",
    )
    attributes: list[KeyOutputKey] = Field(
        default=[],
        description="attributes to be extracted.",
    )


class CfHeader(ExtractionMethod):
    """
    Method: ``cf``

    Description:
        CF backend for header method.

    Configuration Options:
    .. list-table::

        - ``input_term``:term for method to run on
        - ``read_kwargs``:kwargs for cf read
        - ``attributes``:attributes to be extracted

    Example configuration:
    .. code-block:: yaml

        - method: cf
          inputs:
            input_term: hello_world
    """

    input_class = CfHeaderInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:
        field_list = cf.read(self.input.input_term, **self.input.read_kwargs)

        properties: dict[str, Any] = {}
        for field in field_list:
            properties |= field.properties()
            if field.nc_global_attributes():
                properties["global_attributes"] = field.nc_global_attributes()

        for attribute in self.input.attributes:
            if (
                "global_attributes" in properties
                and properties["global_attributes"][attribute.key]
            ):
                body[attribute.output_key] = properties["global_attributes"][
                    attribute.key
                ]
            elif attribute in properties:
                body[attribute.output_key] = properties[attribute.key]

        return body
