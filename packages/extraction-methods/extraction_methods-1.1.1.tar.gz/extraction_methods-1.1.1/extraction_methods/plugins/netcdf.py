# encoding: utf-8
"""
..  _netcdf:

NetCDF Method
-------------
"""
__author__ = "Richard Smith"
__date__ = "19 Aug 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

# Python imports
import logging
from typing import Any

import xarray
from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input, KeyOutputKey

LOGGER = logging.getLogger(__name__)


class NetCDFInput(Input):
    """
    Model for NetCDF Input.
    """

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )
    variable_id: str = Field(
        default="$uri",
        description="lambda function to be run.",
    )
    variable_attributes: list[KeyOutputKey] = Field(
        default=[],
        description="list of variable attributes to extract.",
    )
    global_attributes: list[KeyOutputKey] = Field(
        default=[],
        description="list of global attributes to extract.",
    )
    cf_attributes: list[KeyOutputKey] = Field(
        default=[],
        description="list of cf attributes to extract.",
    )
    rio_attributes: list[KeyOutputKey] = Field(
        default=[],
        description="list of rio attributes to extract.",
    )


LOGGER = logging.getLogger(__name__)


class NetCDFExtract(ExtractionMethod):
    """
    Method: ``netcdf``

    Description:  Processes XML documents to extract metadata

    Configuration Options:
    .. list-table::

        - ``extraction_keys``: List of keys to retrieve from the document.
        - ``filter_expr``: Regex to match against files to limit the attempts to known files
        - ``namespaces``: Map of namespaces

    Extraction Keys:
        Extraction keys should be a map.

        .. list-table::

            * - Name
              - Description
            * - ``output_key``
              - Name of the outputted attribute
            * - ``key``
              - Access key to extract the required data. Passed to
                `xml.etree.ElementTree.find() <https://docs.python.org/3/library/xml.etree.elementtree.html?highlight=find#xml.etree.ElementTree.ElementTree.find>`_
                and also supports `xpath formatted <https://docs.python.org/3/library/xml.etree.elementtree.html#xpath-support>`_ accessors
            * - ``attribute``
              - Allows you to select from the element attribute. In the absence of this value, the default behaviour is to access the text value of the key.
                In some cases, you might want to access and attribute of the element

    Example configuration:
    .. code-block:: yaml

        - method: xml
          inputs:
            filter_expr: '\.manifest$'
            extraction_keys:
              - name: start_datetime
                key: './/gml:beginPosition'
                attribute: start

    # noqa: W605
    """

    input_class = NetCDFInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        dataset = xarray.open_dataset(self.input.input_term, decode_coords="all")

        if self.input.variable_attributes:
            variable = dataset[self.input.variable_id]
            variable_attrs = variable.attrs

            for variable_attribute in self.input.variable_attributes:
                body[variable_attribute.output_key] = variable_attrs.get(
                    variable_attribute.key, None
                )

        if self.input.global_attributes:
            global_attrs = dataset.attrs

            for global_attribute in self.input.global_attributes:
                body[global_attribute.output_key] = global_attrs.get(
                    global_attribute.key, None
                )

        if self.input.cf_attributes:
            cf_attrs = dataset.cf

            for cf_attribute in self.input.cf_attributes:
                try:
                    body[cf_attribute.output_key] = cf_attrs[cf_attribute.key]

                except KeyError:
                    body[cf_attribute.output_key] = None

        if self.input.rio_attributes:
            rio_attrs = dataset.rio

            for rio_attribute in self.input.rio_attributes:
                body[rio_attribute.output_key] = getattr(
                    rio_attrs, rio_attribute.key, None
                )

        return body
