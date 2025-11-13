# encoding: utf-8
"""
..  _extraction-methods:

Extraction Method Models
------------------------
"""
__author__ = "Rhys Evans"
__date__ = "07 Jun 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from importlib.metadata import EntryPoints, entry_points
from typing import Any, Optional

import yaml
from pydantic import BaseModel

from .types import DummyInput, Input

LOGGER = logging.getLogger(__name__)

extraction_method_defaults = {}


class ExtractionMethodConf(BaseModel):
    """STAC extraction method model."""

    method: str
    inputs: Optional[dict[str, Any]] = {}

    _extraction_methods: EntryPoints = entry_points(group="extraction_methods")

    def __repr__(self) -> str:
        return yaml.dump(self.model_dump())

    def _run(self, body: dict[str, Any]) -> dict[str, Any]:
        extraction_method = self._extraction_methods[self.method].load()
        extraction_method = extraction_method(self)

        return extraction_method._run(body)  # type: ignore[no-any-return]


def update_input(
    func: Callable[[Any, dict[str, Any]], Any],
) -> Callable[[Any, dict[str, Any]], Any]:
    """
    Wrapper to update inputs with body values before run.

    :param func: function that wrapper is to be run on
    :type func: Callable

    :return: function that wrapper is to be run on
    :rtype: Callable
    """

    def wrapper(self, body: dict[str, Any]) -> Any:  # type: ignore[no-untyped-def]
        self._input.update_attrs(body)
        return func(self, body)

    return wrapper


def set_extraction_method_defaults(conf_defaults: dict[str, Any]) -> None:
    """
    Function to set global extraction_method_defaults variable.
    """
    global extraction_method_defaults
    extraction_method_defaults = conf_defaults


class SetInput:
    """
    Class to set input attribute from kwargs.
    """

    input_class: Any = Input
    dummy_input_class: Any = DummyInput

    def __init__(
        self, extraction_method_conf: ExtractionMethodConf, *args: Any, **kwargs: Any
    ) -> None:
        """
        Set ``input`` attribute to instance of ``dummy_input_class`` with
        default values overrided by kwargs.

        :param args: fuction arguments
        :type func: Any
        :param kwargs: fuction keyword arguments
        :type func: Any
        """
        global extraction_method_defaults

        input_defaults = {
            key: value.get_default()
            for key, value in self.input_class.model_fields.items()
            if value.get_default()
        }

        inputs = (
            input_defaults
            | extraction_method_defaults.get(extraction_method_conf.method, {})
            | extraction_method_conf.inputs
            | kwargs
        )

        self._input = self.dummy_input_class(**inputs)


class SetEntryPointsMixin:
    """
    Mixin to set ``entry_points`` attribute.
    """

    entry_point_group: str
    entry_points: EntryPoints

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Set ``entry_points`` attribute with entrypoints in ``entry_point_group`` attribute.

        :param args: fuction arguments
        :type func: Any
        :param kwargs: fuction keyword arguments
        :type func: Any
        """
        super().__init__(*args, **kwargs)

        self.entry_points = entry_points(group=self.entry_point_group)


class ExtractionMethod(SetInput, ABC):
    """
    Class to act as a base for all extracion methods. Defines the basic method signature
    and ensure compliance by all subclasses.
    """

    def _run(self, body: dict[str, Any]) -> dict[str, Any]:
        """
        Update ``input`` attribute then run the method.

        :param body: current generated properties
        :type body: dict

        :return: updated body dict
        :rtype: dict
        """

        self._input.update_attrs(body)
        self.input = self.input_class(**self._input.model_dump())

        return self.run(body)

    @abstractmethod
    def run(self, body: dict[str, Any]) -> dict[str, Any]:
        """
        Run the method.

        :param body: current generated properties
        :type body: dict

        :return: updated body dict
        :rtype: dict
        """


class Backend(SetInput, ABC):
    """
    Class to act as a base for Backends. Defines the basic method signature
    and ensure compliance by all subclasses.
    """

    def _run(self, body: dict[str, Any]) -> Iterator[dict[str, Any]]:
        """
        Update ``input`` attribute then run the backend.

        :param body: current generated properties
        :type body: dict

        :return: updated body dict
        :rtype: dict
        """

        self._input.update_attrs(body)
        self.input = self.input_class(**self._input.dict())

        return self.run(body)

    @abstractmethod
    def run(self, body: dict[str, Any]) -> Iterator[dict[str, Any]]:
        """
        Run the backend.

        :param body: current generated properties
        :type body: dict

        :return: updated body dict
        :rtype: dict
        """
