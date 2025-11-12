# encoding: utf-8
"""
..  _extraction-types:

Extraction Method Types
-----------------------
"""
__author__ = "Rhys Evans"
__date__ = "07 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"

from typing import Any

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class KeyOutputKey(BaseModel):
    """
    Model for ``key`` and ``output key`` pairs.
    """

    key: str
    output_key: str = ""

    @model_validator(mode="after")
    def set_default_key(self) -> Self:
        """Set the default for key"""
        if self.output_key == "":
            self.output_key = self.key
        return self


class Input(BaseModel):
    """
    Model for method input.
    """

    exists_key: str = Field(
        default="$",
        description="Key to signify a previously extracted terms.",
    )

    exists_delimiter: str = Field(
        default=".",
        description="Delimiter for nested exists terms.",
    )


class DummyInput(Input, extra="allow"):
    """
    Dummy input used before attributes are updated.
    """

    def update_attr(self, value: Any, body: dict[str, Any]) -> Any:
        """
        Update attribute using the ``exists key``.

        :param value: current attribute value
        :type value: Any
        :param body: current generated properties
        :type body: dict

        :return: updated attribute
        :rtype: Any
        """
        if isinstance(value, str) and value and value[0] == self.exists_key:
            return body.get(value[1:], value)

        if isinstance(value, dict):
            return self.update_dict_attr(value, body)

        if isinstance(value, list):
            return self.update_list_attr(value, body)

        return value

    def update_dict_attr(
        self, input_dict: dict[str, Any], body: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Update nested dictionary attributes.

        :param input_dict: attribute dictionary to update
        :type input_dict: dict
        :param body: current generated properties
        :type body: dict

        :return: updated dictionary attribute
        :rtype: dict
        """
        for key, value in input_dict.items():
            input_dict[key] = self.update_attr(value, body)

        return input_dict

    def update_list_attr(
        self, input_list: list[Any], body: dict[str, Any]
    ) -> list[Any]:
        """
        Update list of attributes.

        :param input_list: attribute list to update
        :type input_list: list
        :param body: current generated properties
        :type body: list

        :return: updated list attribute
        :rtype: list
        """
        for key, value in enumerate(input_list):
            input_list[key] = self.update_attr(value, body)

        return input_list

    def update_attrs(self, body: dict[str, Any]) -> None:
        """
        Update instance attributes with body.

        :param body: current generated properties
        :type body: dict
        """
        for key, value in self.model_dump(exclude={"exists_key"}).items():
            setattr(self, key, self.update_attr(value, body))


class Backend(BaseModel):
    """
    Model for Backend configuration.
    """

    method: str = Field(
        description="Name of backend.",
    )
    inputs: dict[str, Any] = Field(
        default={},
        description="Inputs for backend.",
    )
