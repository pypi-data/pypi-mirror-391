# encoding: utf-8
"""
..  _xml:

XML Method
----------
"""
__author__ = "Richard Smith"
__date__ = "19 Aug 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging
import os.path

# Python imports
from collections import defaultdict

# Package imports
from typing import Any

from lxml import etree  # nosec B410
from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod
from extraction_methods.core.types import Input, KeyOutputKey

LOGGER = logging.getLogger(__name__)


class XMLProperty(KeyOutputKey):
    """
    Model for XML property.

    """

    attribute: str = Field(
        default="",
        description="Attribute of the XML property.",
    )


class XMLInput(Input):
    """
    Model for XML Input.
    """

    input_term: str = Field(
        default="$uri",
        description="Term for method to run on.",
    )
    # template: str = Field(
    #     description="Template to follow.",
    # )
    properties: list[XMLProperty] = Field(
        description="List of properties to retrieve from the document.",
    )
    # filter_expr: str = Field(
    #     description="Regex to match against files to limit the attempts to known files.",
    # )
    namespaces: dict[str, str] = Field(
        description="Map of namespaces.",
    )


class XMLExtract(ExtractionMethod):
    """
    Method: ``xml``

    Description:
        Processes XML documents to extract metadata

    Configuration Options:
    .. list-table::

        - ``input_term``: Term for method to run on.
        - ``template``: ``REQUIRED`` Template to follow.
        - ``properties``: ``REQUIRED`` List of properties to retrieve from the document.
        - ``namespaces``: ``REQUIRED`` Map of namespaces.

    Extraction Keys:
        Extraction keys should be a map.

        .. list-table::

            * - Name
              - Description
            * - ``key``
              - Key of the property. Passed to
                `xml.etree.ElementTree.find() <https://docs.python.org/3/library/xml.etree.elementtree.html?highlight=find#xml.etree.ElementTree.ElementTree.find>`_
                and also supports `xpath formatted <https://docs.python.org/3/library/xml.etree.elementtree.html#xpath-support>`_ accessors
            * - ``output_key``
              - Key to output to.
            * - ``attribute``
              - Allows you to select from the element attribute. In the absence of this value, the default behaviour is to access the text value of the key.
                In some cases, you might want to access and attribute of the element.

    Example configuration:
    .. code-block:: yaml

        - method: xml
          inputs:
            properties:
              - name: start_datetime
                key: './/gml:beginPosition'
                attribute: start

    # noqa: W605
    """

    input_class = XMLInput

    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        # Extract the keys
        try:

            if os.path.isfile(self.input.input_term):
                xml_file = etree.parse(self.input.input_term)

            else:
                xml_file = etree.XML(self.input.input_term.encode("ascii", "ignore"))

        except (etree.ParseError, FileNotFoundError, TypeError):
            return body

        output: dict[str, list[str]] = defaultdict(list)

        for prop in self.input.properties:
            values = xml_file.findall(
                prop.key,
                self.input.namespaces,
            )

            for value in values:
                if value is not None:

                    if prop.attribute:
                        v = value.get(prop.attribute, "")

                    else:
                        v = value.text

                    if v and v not in output[prop.output_key]:
                        output[prop.output_key].append(v.strip())

            if output[prop.output_key]:
                body[prop.output_key] = (
                    output[prop.output_key][0]
                    if len(output[prop.output_key]) == 1
                    else output[prop.output_key]
                )

        return body
