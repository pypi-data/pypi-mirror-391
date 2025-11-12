# encoding: utf-8
"""
..  _geometry:

Geometry Method
---------------
"""
__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Package imports
from typing import Any, Literal

from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class GeometryInput(Input):
    """
    Model for Geometry Input.
    """

    type: Literal[
        "Point",
        "LineString",
        "Polygon",
        "MultiPointString",
        "MultiLineString",
        "MultiPolygon",
    ] = Field(
        description="Type of geometry to be produced.",
    )
    coordinates: list[Any] = Field(
        description="list of coordinates to convert to geometry. Ordering is respected.",
    )
    output_key: str = Field(
        default="geometry",
        description="key to output to.",
    )


class GeometryExtract(ExtractionMethod):
    """
    Method: ``geometry``

    Description:
        Accepts a dictionary of coordinate values and converts to `RFC 7946, <https://tools.ietf.org/html/rfc7946>`_
        formatted geometry.

    Configuration Options:
    .. list-table::

        - ``type``: ``REQUIRED`` Type of geometry to be produced.
        - ``coordinates``: ``REQUIRED`` list of coordinates to convert to geometry. Ordering is respected.
        - ``output_key``: key to output to.

    Example Configuration:
    .. code-block:: yaml

        - name: geometry
          inputs:
            type: line
            coordinates:
              -
                - 0
                - 0
              -
                - $lon_2
                - $lat_2
    """

    input_class = GeometryInput

    def point(self, coordinates: list[str | float]) -> list[float]:
        """
        Get point coordinates

        :param coordinates: list of coordinates
        :type coordinates: list

        :return: coordinates
        :rtype: list
        """

        return [
            float(coordinates[0]),
            float(coordinates[1]),
        ]

    def line(self, coordinates: list[list[str | float]]) -> list[list[float]]:
        """
        Get line coordinates

        :param coordinates: list of coordinates
        :type coordinates: list

        :return: coordinates
        :rtype: list
        """

        return [self.point(coordinate) for coordinate in coordinates]

    def polygon(self, coordinates: list[list[str | float]]) -> list[list[list[float]]]:
        """
        Get polygon coordinates

        :param coordinates: list of coordinates
        :type coordinates: list

        :return: coordinates
        :rtype: list
        """

        output = self.line(coordinates)

        if output[0] != output[-1]:
            # Add the first point to the end to complete the shape
            output.append(output[0])

        return [output]

    def multi(self, coordinate_type: str, coordinates: list[Any]) -> list[Any]:
        """
        Get polygon coordinates

        :param coordinate_type: type of coordinates
        :type coordinate_type: str
        :param coordinates: list of coordinates
        :type coordinates: list

        :return: coordinates
        :rtype: list
        """

        return [
            self.get_coordinates(coordinate_type.lstrip("Multi"), coordinate)
            for coordinate in coordinates
        ]

    def get_coordinates(
        self, coordinate_type: str, coordinates: list[Any]
    ) -> list[Any]:
        """
        Get coordinates

        :param coordinate_type: type of coordinates
        :type coordinate_type: str
        :param coordinates: list of coordinates
        :type coordinates: list

        :return: coordinates
        :rtype: list
        """

        if coordinate_type == "Point":
            return self.point(coordinates)

        if coordinate_type == "Line":
            return self.line(coordinates)

        if coordinate_type == "Polygon":
            return self.polygon(coordinates)

        if coordinate_type.startswith("Multi"):
            return self.multi(coordinate_type, coordinates)

        return []

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        try:
            body[self.input.output_key] = {
                "type": self.input.type,
                "coordinates": self.get_coordinates(
                    self.input.type,
                    self.input.coordinates,
                ),
            }

        except KeyError:
            LOGGER.warning(
                "Unable to convert to a line geometry.",
                exc_info=True,
            )

        return body
