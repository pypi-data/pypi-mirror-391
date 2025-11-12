# encoding: utf-8
"""
..  _ncml-header:

NCML Header Backend
-------------------
"""
__author__ = "David Huard"
__date__ = "June 2022"
__copyright__ = "Copyright 2022 Ouranos"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "huard.david@ouranos.ca"

import logging
import subprocess  # nosec B404
from typing import Any
from urllib.parse import urlparse

import httpx
from lxml.etree import XMLParser, fromstring  # nosec B410
from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input, KeyOutputKey

LOGGER = logging.getLogger(__name__)


class NcMLHeaderInput(Input):
    """
    Model for NcML Header Input.
    """

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )
    request_params: dict[str, Any] = Field(
        default={"catalog": None, "dataset": None},
        description="params for request.",
    )
    namespaces: dict[str, str] = Field(
        default={"ncml": "http://www.unidata.ucar.edu/namespaces/netcdf/ncml-2.2"},
        description="NcML namespaces.",
    )
    attributes: list[KeyOutputKey] = Field(
        default=[],
        description="attributes to be extracted.",
    )
    request_timeout: int = Field(
        default=15,
        description="request time out.",
    )


class NcMLHeader(ExtractionMethod):
    """
    Method: ``ncml``

    Description:
        NcML backend for header method.

    Configuration Options:
    .. list-table::

        - ``input_term``:term for method to run on
        - ``request_params``:params for request
        - ``namespaces``:NcML namespaces
        - ``attributes``:attributes to be extracted
        - ``request_timeout``:request time out

    Example configuration:
    .. code-block:: yaml

        - method: ncml
          inputs:
            input_term: hello_world
    """

    input_class = NcMLHeaderInput

    def get_ncml(self) -> bytes:
        """Get the NcML file description."""

        parse_result = urlparse(self.input.input_term)

        if parse_result.netloc:
            return self.get_ncml_from_thredds()

        return self.get_ncml_from_fs()

    def get_ncml_from_thredds(self) -> bytes:
        """Read NcML response from THREDDS server.

        Returns
        -------
        bytes
        NcML content
        """

        r = httpx.get(
            self.input.input_term,
            params=self.input.request_params,
            timeout=self.input.request_timeout,
        )
        r.raise_for_status()
        return r.content

    def get_ncml_from_fs(self) -> bytes:
        """Return NcML file description using `ncdump` utility."""

        cmd = ["ncdump", "-hx", self.input.input_term]
        proc = subprocess.Popen(
            cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )  # nosec B603
        if proc.stdout:
            return proc.stdout.read()
        else:
            return b""

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:
        # Convert response to an XML etree.Element
        content = self.get_ncml()
        elemement = fromstring(
            content, parser=XMLParser(encoding="UTF-8")
        )  # nosec B320

        for attribute in self.input.attributes:

            # Execute xpath expression
            value = elemement.xpath(attribute.key, namespaces=self.input.namespaces)

            if value:
                body[attribute.output_key] = value[0]

        return body
