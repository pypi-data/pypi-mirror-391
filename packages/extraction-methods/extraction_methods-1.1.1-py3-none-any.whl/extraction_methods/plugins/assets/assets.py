# encoding: utf-8
"""
..  _assets:

STAC Assets Extraction
----------------------
"""
__author__ = "Rhys Evans"
__date__ = "24 May 2022"
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
    SetEntryPointsMixin,
    update_input,
)
from extraction_methods.core.types import Backend, Input

LOGGER = logging.getLogger(__name__)


class AssetInput(Input):
    """
    Model for Asset Method Input.
    """

    backend: Backend = Field(
        description="Backend and inputs to run.",
    )
    extraction_methods: list[ExtractionMethodConf] = Field(
        default=[],
        description="Extraction methods to run on assets.",
    )
    output_key: str = Field(
        default="assets",
        description="term for method to output to.",
    )


class AssetExtract(SetEntryPointsMixin, ExtractionMethod):
    """
    Method: ``assets``

    Description:
        Method to generate a dictionary of STAC Assets.

    Configuration Options:
    .. list-table::

        - ``backend``: Backend name and inputs
        - ``extraction_methods``: Extraction methods to run on assets
        - ``output_key``: key to output to

    Configuration Example:
    .. code-block:: yaml

        - method: assets
          inputs:
            backend:
              name: elasticsearch
              inputs:
                connection_kwargs:
                  hosts: ['host1:9200','host2:9200']
            extraction_methods:
              - method: default
                inputs:
                  defaults:
                    hello: world
    """

    input_class = AssetInput
    entry_point_group: str = "extraction_methods.assets.backends"

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        output = {}
        backend_entry_point = self.entry_points[self.input.backend.method].load()
        backend = backend_entry_point(self.input.backend)
        assets = backend._run(body)

        for asset in assets:
            for extraction_method in self.input.extraction_methods:
                asset = extraction_method._run(asset)
            output[asset["href"]] = asset

        body[self.input.output_key] = body.get(self.input.output_key, {}) | output

        return body
