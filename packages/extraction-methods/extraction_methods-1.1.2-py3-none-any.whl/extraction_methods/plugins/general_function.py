# encoding: utf-8
"""
..  general-function:

General Function Method
-----------------------
"""
__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import importlib
import logging

# Package imports
from typing import Any

from pydantic import BaseModel, Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class Function(BaseModel):  # type: ignore[no-redef]
    """
    Model for Fuction.
    """

    name: str = Field(
        description="Name of function.",
    )
    args: list[Any] = Field(
        default=[],
        description="list of arguments for function.",
    )
    kwargs: dict[str, Any] = Field(
        default={},
        description="dictionary of key word arguments for function.",
    )


class GeneralFunctionInput(Input):
    """
    Model for General Fuction Input.
    """

    function: Function = Field(
        description="Function to be run name maybe seperatated my delimieter.",
    )
    delimiter: str = Field(
        default=".",
        description="text delimiter to put between module/function names.",
    )
    output_key: str = Field(
        default="",
        description="key to output to, else response will be merged with body.",
    )


class GeneralFunctionExtract(ExtractionMethod):
    """
    Method: ``general_function``

    Description:
        Accepts a dictionary. String values are popped from the dictionary and
        are put back into the dictionary with the ``key`` specified.

    Configuration Options:
    .. list-table::

        - ``function``: ``REQUIRED`` Function to be run ``name``, ``args``, and ``kwargs``.
        - ``delimiter``: Optional text delimiter to put between module/function
                        names ``Default`` "."
        - ``output_key``: Optional name of the key you would like to output else
                          response will be merged.

    Example Configuration:
    .. code-block:: yaml

        - method: general_function
          inputs:
            funtion:
              name: import.path.to.the.fuction
              args:
                - hello
                - world
              kwargs:
                hello: world
                foo: bar
    """

    input_class = GeneralFunctionInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:
        output_body = body.copy()

        module_name, function_name = self.input.function.name.rsplit(
            self.input.delimiter, 1
        )

        module = importlib.import_module(module_name)

        function = getattr(module, function_name)

        result = function(*self.input.function.args, **self.input.function.kwargs)

        if self.input.output_key:
            output_body[self.input.output_key] = result

        elif isinstance(result, dict):
            output_body |= result

        return output_body
