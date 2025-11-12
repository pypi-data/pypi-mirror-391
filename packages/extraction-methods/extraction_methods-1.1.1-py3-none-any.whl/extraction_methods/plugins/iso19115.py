# encoding: utf-8
"""
..  _iso19115:

ISO 19115 Method
----------------
"""
__author__ = "Richard Smith"
__date__ = "28 Jul 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

# Python imports
import logging
from typing import Any

# Third party imports
import httpx
from lxml.etree import ElementTree as ET  # nosec B410
from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input, KeyOutputKey

LOGGER = logging.getLogger(__name__)


class ISO19115Input(Input):
    """
    Model for ISO19115 Date Input.
    """

    url: str = Field(
        description="Url for record store.",
    )
    dates: list[KeyOutputKey] = Field(
        description="list of dates to extract.",
    )
    request_timeout: int = Field(
        default=15,
        description="request time out.",
    )


iso19115_ns = {
    "gmd": "http://www.isotc211.org/2005/gmd",
    "gml": "http://www.opengis.net/gml/3.2",
    "gco": "http://www.isotc211.org/2005/gco",
    "gmx": "http://www.isotc211.org/2005/gmx",
    "srv": "http://www.isotc211.org/2005/srv",
    "xlink": "http://www.w3.org/1999/xlink",
}


class ISO19115Extract(ExtractionMethod):
    """
    Method: ``iso19115``

    Description:
        Takes a URL and calls out to URL to retrieve the iso19115 record.

    Configuration Options:
    .. list-table::

        - ``url``: ``REQUIRED`` URL to record store.
        - ``date_terms``: List of name, key, format of date terms to retrieve from the response.

    Example configuration:
    .. code-block:: yaml

        - method: iso19115
          inputs:
            url: $url
            dates:
              - key: './/gml:beginPosition'
                output_key: start_datetime
    """

    input_class = ISO19115Input

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        # Retrieve the ISO 19115 record
        response = httpx.get(self.input.url, timeout=self.input.request_timeout)

        if not response.status_code == 200:
            LOGGER.debug(
                "Request %s failed with response: %s", self.input.url, response.text
            )
            return body

        iso_record = ET.fromstring(response.text)

        # Extract the keys
        for extraction_term in self.input.dates:
            value = iso_record.find(extraction_term.key, iso19115_ns)

            if value is not None:
                body[extraction_term.output_key] = value.text

        return body
