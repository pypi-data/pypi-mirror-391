# encoding: utf-8
"""
..  _open-zip:

Open Zip Method
---------------
"""
__author__ = "Richard Smith"
__date__ = "19 Aug 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

import logging
import zipfile
from typing import Any

from pydantic import Field, model_validator
from typing_extensions import Self

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input, KeyOutputKey

LOGGER = logging.getLogger(__name__)


class ZipInput(Input):
    """
    Model for Zip Input.
    """

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )
    inner_files: list[KeyOutputKey] = Field(
        default=[],
        description="list of inner zipped files to be read.",
    )
    output_key: str = Field(
        default="",
        description="key to output to.",
    )

    @model_validator(mode="after")
    def check_root_read(self) -> Self:
        if not self.output_key and not self.inner_files:
            raise ValueError("`output_key` required if no `inner_files` defined")
        return self


class ZipExtract(ExtractionMethod):
    """
    Method: ``open_zip``

    Description:
        Open a zip file and read inner files

    Configuration Options:
    .. list-table::

        - ``input_term``: List of keys to retrieve from the document.
        - ``inner_files``: Lost of inner zipped files to be read.
        - ``output_key``: key to output to.

    Example configuration:
    .. code-block:: yaml

        - method: open_zip
          inputs:
            input_term: /path/to/a/file
            inner_files:
              - key: hello.txt
                output_key: world

    # noqa: W605
    """

    input_class = ZipInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        # Extract the keys
        with zipfile.ZipFile(self.input.input_term) as z:
            if not self.input.inner_files:
                body[self.input.output_key] = z.read()  # type: ignore[call-arg]

            else:
                output: dict[str, Any] = {}

                for inner_file in self.input.inner_files:
                    output[inner_file.output_key] = z.read(inner_file.key)

                if self.input.output_key:
                    body[self.input.output_key] = output

                else:
                    body |= output

        return body
