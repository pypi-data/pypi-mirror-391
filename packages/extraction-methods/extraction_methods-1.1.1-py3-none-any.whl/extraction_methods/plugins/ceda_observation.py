# encoding: utf-8
"""
..  _ceda-observation:

CEDA Observation Method
-----------------------
"""
__author__ = "Richard Smith"
__date__ = "11 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging
from typing import Any

# Third party imports
import httpx
from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class CEDAObservationInput(Input):
    """
    Model for CEDA Observation Method Input.
    """

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )
    request_timeout: int = Field(
        default=15,
        description="request time out.",
    )
    output_key: str = Field(
        default="uuid",
        description="key to output to.",
    )


class CEDAObservationExtract(ExtractionMethod):
    """
    Method: ``ceda_observation``

    Description:
        Returns a ceda observation record for the ``input_term``.

    Configuration Options:
    .. list-table::

        - ``input_term``: ``REQUIRED`` term for method to run on

    Example Configuration:
    .. code-block:: yaml

        - method: ceda_observation
          inputs:
            input_term: $url
    """

    input_class = CEDAObservationInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:
        r = httpx.get(self.input.input_term, timeout=self.input.request_timeout)

        if r.status_code == 200:
            response = r.json()
            record_type = response.get("record_type")
            url = response.get("url")

            if record_type == "Dataset" and url:
                body[self.input.output_key] = url.split("/")[-1]

        return body
