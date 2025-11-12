# encoding: utf-8
"""
..  _datetime-bound-to-centroid:

Datetime Bound to Centroid Method
---------------------------------
"""
__author__ = "Richard Smith"
__date__ = "28 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


import logging
from datetime import datetime
from typing import Any

from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class DatetimeBoundToCentroidInput(Input):
    """
    Model for Datetime Bound to Centroid Method Input.
    """

    start_datetime: str = Field(
        default="$start_datetime",
        description="Start datetime bound.",
    )
    start_format: str = Field(
        default="%Y-%m-%dT%H:%M:%S",
        description="Format for start datetime.",
    )
    end_datetime: str = Field(
        default="$end_datetime",
        description="End datetime bound.",
    )
    end_format: str = Field(
        default="%Y-%m-%dT%H:%M:%S",
        description="Format of end datetime.",
    )
    output_key: str = Field(
        default="datetime",
        description="key to output to.",
    )
    output_format: str = Field(
        default="%Y-%m-%dT%H:%M:%SZ",
        description="format of output.",
    )


class DatetimeBoundToCentroidExtract(ExtractionMethod):
    """
    Method: ``datetime_bound_to_centroid``

    Description:
        Accepts a dictionary of coordinate values and converts to `RFC 7946, section 5 <https://tools.ietf.org/html/rfc7946#section-5>`_
        formatted bbox.

    Configuration Options:
    .. list-table::

        - ``start_datetime``: Start datetime bound
        - ``start_format``: Format of the start datetime
        - ``end_datetime``: End datetime bound
        - ``end_format``: Format of the end datetime
        - ``output_key``: Term for method to output to
        - ``output_format``: Format of the output datetime

    Example Configuration:
    .. code-block:: yaml

        - method: datetime_bound_to_centroid
          inputs:
            start_datetime: $start_date
            end_datetime: 2022-02-02
            end_format: %Y-%m-%d
            output_key: polygon
    """

    input_class = DatetimeBoundToCentroidInput

    def strip_time(self, datetime_str: str, datetime_format: str) -> "datetime":
        """
        strip datetime from value.

        :param datetime_str: string to convert to datetime
        :type datetime_str: str
        :param datetime_format: format of datetime string
        :type datetime_format: str

        :return: datetime object
        :rtype: datetime
        """
        try:
            return datetime.strptime(datetime_str, datetime_format)

        except ValueError as v:
            if len(v.args) > 0 and v.args[0].startswith("unconverted data remains: "):
                datetime_str = datetime_str[: -(len(v.args[0]) - 26)]
                return datetime.strptime(datetime_str, datetime_format)

            raise v

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        start_datetime = self.strip_time(
            self.input.start_datetime, self.input.start_format
        )
        end_datetime = self.strip_time(self.input.end_datetime, self.input.end_format)

        centroid_datetime = start_datetime + (end_datetime - start_datetime) / 2

        body[self.input.output_key] = centroid_datetime.strftime(
            self.input.output_format
        )

        return body
