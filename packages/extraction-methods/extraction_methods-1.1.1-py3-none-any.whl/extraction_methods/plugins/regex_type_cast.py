# encoding: utf-8
"""
..  _regex-type-cast:

Regex Type Cast Method
----------------------
"""
__author__ = "Rhys Evans"
__date__ = "8 Jul 2024"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"


# Python imports
import ast
import logging
import re
from typing import Any

from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class RegexCastType(Input):
    """
    Model for Regex Cast Type.
    """

    regex: str = Field(
        description="Regex to test against.",
    )
    cast_type: str = Field(
        description="Python type to cast to.",
    )


class RegexTypeCastInput(Input):
    """
    Model for Regex Cast Type Input.
    """

    regex_casts: list[RegexCastType] = Field(
        description="Regex and cast type combinations.",
    )


class RegexTypeCastExtract(ExtractionMethod):
    """
    Method: ``regex_type_cast``

    Description:
        Takes a list of regex and cast type combinations. Any existing properties
        that full match a regex are cast to the associated type.

    Configuration Options:
    .. list-table::

        - ``regex_casts``: Regex and cast type combinations.

    Example configuration:
    .. code-block:: yaml

        - method: regex_type_cast
          inputs:
            regex_casts:
              - regex: clound_cover
                cast_type: int

    # noqa: W605
    """

    input_class = RegexTypeCastInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        output = body.copy()
        for key in body.keys():
            for regex_cast in self.input.regex_casts:
                if re.fullmatch(rf"{regex_cast.regex}", key):
                    cast_type = ast.literal_eval(regex_cast.cast_type)
                    output[key] = cast_type(body[key])

        return output
