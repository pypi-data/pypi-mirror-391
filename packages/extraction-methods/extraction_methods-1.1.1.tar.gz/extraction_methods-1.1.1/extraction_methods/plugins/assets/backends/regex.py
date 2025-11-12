# encoding: utf-8
"""
..  _regex-assets:

Regex Assets Backend
--------------------
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import glob
import logging
from typing import Any, Iterator

from pydantic import Field

from extraction_methods.core.extraction_method import Backend, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class RegexAssetsInput(Input):
    """
    Model for Regex Assets Backend Input.
    """

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )


class RegexAssets(Backend):
    """
    Method: ``regex_assets``

    Description:
        Takes a regex glob and yields a dictionary for each matching path.

    Configuration Options:
    .. list-table::

        - ``input_term``:The regular expression to match against the path

    Example configuration:
    .. code-block:: yaml

        - method: regex
          inputs:
            input_term: ^(?:[^_]*_){2}(?P<datetime>\d*)

    # noqa: W605
    """

    input_class = RegexAssetsInput

    @update_input
    def run(self, body: dict[str, Any]) -> Iterator[dict[str, Any]]:

        for path in glob.iglob(self.input.input_term):
            yield {
                "href": path,
            }
