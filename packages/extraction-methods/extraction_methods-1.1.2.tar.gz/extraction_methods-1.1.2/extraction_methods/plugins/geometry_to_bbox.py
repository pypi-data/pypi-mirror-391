# encoding: utf-8
"""
..  _geometry-to-bbox:

Geometry to Bounding Box Method
-------------------------------
"""
__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging

# Package imports
from typing import Any

from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class GeometryToBboxInput(Input):
    """
    Model for Geometry to Bounding Box Input.
    """

    geometry: dict[str, Any] = Field(  # type: ignore[assignment]
        default="$geometry",
        description="geometry to be converted to bbox.",
    )
    output_key: str = Field(
        default="bbox",
        description="key to output to.",
    )


class GeometryToBboxExtract(ExtractionMethod):
    """
    Method: ``geometry_to_bbox``

    Description:
        Accepts a geometry with type and list of coordinates to `RFC 7946,
        section 5 <https://tools.ietf.org/html/rfc7946#section-5>`_ formatted bbox.

    Configuration Options:
    .. list-table::

        - ``geometry``: ``REQUIRED`` geometry to be converted to bbox.
        - ''output_key'': key to output to.

    Example Configuration:
    .. code-block:: yaml

        - method: geometry_to_bbox
          inputs:
            geometry:
              type: point
              coordinates:
                - 20
                - 0
    """

    input_class = GeometryToBboxInput

    def point(self, coordinates: list[float]) -> list[float]:
        """
        Get point bbox

        :param coordinates: list of coordinates
        :type coordinates: list

        :return: bounding box of coordinates
        :rtype: list
        """

        return [
            coordinates[0],
            coordinates[1],
            coordinates[0],
            coordinates[1],
        ]

    def line(self, coordinates: list[list[float]]) -> list[float]:
        """
        Get line bbox

        :param coordinates: list of coordinates
        :type coordinates: list

        :return: bounding box of coordinates
        :rtype: list
        """

        bbox = self.point(coordinates[0])

        for coordinate in coordinates[1:]:

            if coordinate[0] < bbox[0]:
                bbox[0] = coordinate[0]

            elif coordinate[0] > bbox[2]:
                bbox[2] = coordinate[0]

            if coordinate[1] < bbox[1]:
                bbox[1] = coordinate[1]

            elif coordinate[1] > bbox[3]:
                bbox[3] = coordinate[1]

        return bbox

    def polygon(self, coordinates: list[list[float]]) -> list[float]:
        """
        Get polygon bbox

        :param coordinates: list of coordinates
        :type coordinates: list

        :return: bounding box of coordinates
        :rtype: list
        """

        return self.line(coordinates[1:])

    def multi(self, coordinate_type: str, coordinates: list[Any]) -> list[float]:
        """
        Get polygon bbox

        :param coordinate_type: type of coordinates
        :type coordinate_type: str
        :param coordinates: list of coordinates
        :type coordinates: list

        :return: bounding box of coordinates
        :rtype: list
        """

        bboxes = [
            self.get_bbox(coordinate_type.lstrip("Multi"), coordinate)
            for coordinate in coordinates
        ]
        return [
            min(bbox[0] for bbox in bboxes),
            max(bbox[2] for bbox in bboxes),
            min(bbox[1] for bbox in bboxes),
            max(bbox[3] for bbox in bboxes),
        ]

    def get_bbox(self, coordinate_type: str, coordinates: list[Any]) -> list[float]:
        """
        Get bbox from geometry

        :param coordinate_type: type of coordinates
        :type coordinate_type: str
        :param coordinates: list of coordinates
        :type coordinates: list

        :return: bounding box of coordinates
        :rtype: list
        """

        if coordinate_type == "Point":
            return self.point(coordinates)

        if coordinate_type == "Line":
            return self.line(coordinates)

        if coordinate_type == "Polygon":
            return self.polygon(coordinates[0])

        if coordinate_type.startswith("Multi"):
            return self.multi(coordinate_type, coordinates)

        return []

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        body[self.input.output_key] = self.get_bbox(
            self.input.geometry["type"], self.input.geometry["coordinates"]
        )

        return body
