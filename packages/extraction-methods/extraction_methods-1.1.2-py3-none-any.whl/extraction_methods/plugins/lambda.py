# encoding: utf-8
"""
..  _lambda:

Lambda Method
-------------
"""
__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging
from typing import Any

from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class LambdaInput(Input):  # type: ignore[no-redef]
    """
    Model for Lambda Input.
    """

    function: str = Field(
        description="lambda function to be run.",
    )
    args: list[Any] = Field(
        default=[],
        description="list of arguments for function.",
    )
    kwargs: dict[str, Any] = Field(
        default={},
        description="dictionary of key word arguments for function.",
    )
    output_key: str = Field(
        default="label",
        description="key to output to.",
    )


class LambdaExtract(ExtractionMethod):
    """
    Method: ``lambda``

    Description:
        Accepts a dictionary. String values are popped from the dictionary and
        are put back into the dictionary with the ``key`` specified.

    Configuration Options:
    .. list-table::

        - ``function``: ``REQUIRED`` lambda function to be run.
        - ``output_key``: Optional name of the key you would like to output else
                          response will be merged.
        - ``args``: Optional list of arguments for function.
                    Use $ for previously extracted terms
        - ``kwargs``: Optional dictionary of key word arguments for function.
                      Use $ for previously extracted terms

    Example Configuration:
    .. code-block:: yaml

        - method: lambda
          inputs:
            function: 'lambda x: x * x'
            args:
              - hello
              - $world
            kwargs:
              hello: world
              goodbye: all
    """

    input_class = LambdaInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        output_body = body.copy()

        function = eval(self.input.function)  # nosec B307

        result = function(*self.input.args, **self.input.kwargs)

        if self.input.output_key:
            output_body[self.input.output_key] = result

        elif isinstance(result, dict):
            output_body |= result

        return output_body
