# encoding: utf-8
"""
..  _regex-label:

Regex Label Method
------------------
"""
__author__ = "Rhys Evans"
__date__ = "8 Jul 2024"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"


# Python imports
import logging
import re
from typing import Any

from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class RegexLabelInput(Input):
    """
    Model for Regex Label Input.
    """

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )
    label: str = Field(
        description="Label to add if regex passes.",
    )
    regex: str = Field(
        description="Regex to test against.",
    )
    allow_multiple: bool = Field(
        default=True,
        description="True if multiple labels are allowed.",
    )
    output_key: str = Field(
        default="label",
        description="Term for method to output to.",
    )


class RegexLabelExtract(ExtractionMethod):
    """
    Method: ``regex_label``

    Description:
        Adds label if full match of regex.

    Configuration Options:
    .. list-table::

        - ``input_term``: term for method to run on.
        - ``label``: ``REQUIRED`` Label to add if regex passes.
        - ``regex``: ``REQUIRED`` Regex to test against.
        - ``allow_multiple``: True if multiple labels are allowed.
        - ``output_key``: Term for method to output to.

    Example configuration:
    .. code-block:: yaml

        - method: regex_label
          inputs:
            label: metadata
            regex: README
            allow_multiple: true

    # noqa: W605
    """

    input_class = RegexLabelInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        if re.fullmatch(rf"{self.input.regex}", self.input.input_term):
            if self.input.allow_multiple:
                body.setdefault(self.input.output_key, []).append(self.input.label)

            else:
                body[self.input.output_key] = self.input.label

        return body
