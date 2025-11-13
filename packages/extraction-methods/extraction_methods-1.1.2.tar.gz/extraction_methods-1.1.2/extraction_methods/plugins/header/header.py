# encoding: utf-8
"""
..  _header:

Header Method
-------------
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging
from typing import Any

from pydantic import Field

from extraction_methods.core.extraction_method import (
    ExtractionMethod,
    SetEntryPointsMixin,
    update_input,
)
from extraction_methods.core.types import Backend, Input

LOGGER = logging.getLogger(__name__)


class HeaderInput(Input):
    """
    Model for Header Method Input.
    """

    backend: Backend = Field(
        description="Backend and inputs to run.",
    )


class HeaderExtract(ExtractionMethod, SetEntryPointsMixin):
    """
    Method: ``header``

    Description:
        Takes a header backend to run and returns the updated body
        from the configured backend.

    Configuration Options:
    .. list-table::

        - ``backend``: Specify which backend

    Example configuration:
    .. code-block:: yaml

        - method: header
          inputs:
            backend:
                name: xarray
                inputs:
                  kwargs:
                    decode_times: False
                  attributes:
                    - name: institution
                    - name: sensor
    """

    input_class = HeaderInput
    entry_point_group = "extraction_methods.header.backends"

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        backend_entry_point = self.entry_points[self.input.backend.name].load()
        backend = backend_entry_point(**self.input.backend.inputs)
        body = backend._run(body)

        return body
