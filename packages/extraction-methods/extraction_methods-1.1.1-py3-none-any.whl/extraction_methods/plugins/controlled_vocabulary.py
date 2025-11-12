# encoding: utf-8
"""
..  _controlled-vocabulary:

Controlled Vocabulary Method
----------------------------
"""
__author__ = "David Huard"
__date__ = "June 2022"
__copyright__ = "Copyright 2022 Ouranos"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "huard.david@ouranos.ca"


import importlib

# Python imports
import logging
from typing import Any

from jsonschema import ValidationError
from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class ControlledVocabularyInput(Input):
    """
    Model for Contrilled Vocabulary Method Input.
    """

    model: str = Field(
        description="pydantic.BaseModel subclass to be imported at run-time, e.g. `package.module.class_name`.",
    )
    strict: bool = Field(
        default=False,
        description="If True, raise ValidationError, otherwise simply log ValidationError messages.",
    )


class ControlledVocabularyExtract(ExtractionMethod):
    """
    Method: ``controlled_vocabulary``

    Description:
        Compare properties to a controlled vocabulary defined by a pydantic.BaseModel.

    Configuration Options:
    .. list-table::

        - ``model``: pydantic.BaseModel subclass to be imported at run-time, e.g. `package.module.class_name`
        - ``strict``: If True, raise ValidationError, otherwise simply log ValidationError messages

    Example Configuration:
        .. code-block:: yaml

            - name: controlled_vocabulary
              inputs:
                model: my_cv.collections.CMIP5
                strict: False
    """

    input_class = ControlledVocabularyInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:
        # Import data model
        scopes = self.input.model.split(".")
        module_str = ".".join(scopes[:-1])

        module = importlib.import_module(module_str)
        klass = getattr(module, scopes[-1])

        # Get metadata attributes
        properties = body

        # Instantiate data model
        try:
            cv = klass(**properties)
            body = cv.dict()

        except ValidationError as exc:
            LOGGER.warning(exc)

            if self.input.strict:
                raise exc

        return body
