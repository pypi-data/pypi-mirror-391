# encoding: utf-8
"""
..  _xarray-header:

Xarray Header Backend
---------------------
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging
from typing import Any

import xarray as xr
from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input, KeyOutputKey

LOGGER = logging.getLogger(__name__)


class XarrayHeaderInput(Input):
    """
    Model for Xarray Header Method Input.
    """

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )
    dataset_kwargs: dict[str, Any] = Field(
        default={},
        description="kwargs to open dataset.",
    )
    attributes: list[KeyOutputKey] = Field(
        default=[],
        description="attributes to be extracted.",
    )


class XarrayHeader(ExtractionMethod):
    """
    Method: ``xarray``

    Description:
        Xarray backend for header method.

    Configuration Options:
    .. list-table::

        - ``input_term``:term for method to run on
        - ``dataset_kwargs``:kwargs to open dataset
        - ``attributes``:attributes to be extracted

    Example configuration:
    .. code-block:: yaml

        - method: xarray
          inputs:
            input_term: hello_world
    """

    input_class = XarrayHeaderInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        ds = xr.open_dataset(self.input.input_term, **self.input.dataset_kwargs)

        for attribute in self.input.attributes:
            value = ds.attrs.get(attribute.key)

            if value:
                body[attribute.output_key] = value

        return body
