# encoding: utf-8
"""
..  _path-parts:

Path Parts Method
-----------------
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


# Python imports
import logging
from pathlib import Path
from typing import Any

from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class PathPartsInput(Input):
    """
    Model for Path Parts Input.
    """

    path: str = Field(
        default="$uri",
        description="path for method to run on.",
    )
    skip: int = Field(
        default=0,
        description="number of path parts to skip.",
    )


class PathPartsExtract(ExtractionMethod):
    """
    Method: ``path_parts``

    Description:
        Extracts the parts of a given path skipping ``skip`` number
        of top level parts.

    Configuration Options:
    .. list-table::

        - ``skip``: The number of path parts to skip. ``default: 0``

    Example configuration:
    .. code-block:: yaml

        - method: path_parts
          inputs:
            input_term: $uri
            skip: 2
    """

    input_class = PathPartsInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        path = Path(self.input.path)

        parts = list(path.parts)[self.input.skip :]

        body["filename"] = parts.pop()

        dir_level = 1
        for part in parts:
            body[f"_dir{dir_level}"] = part
            dir_level += 1

        return body
