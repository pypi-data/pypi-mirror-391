# encoding: utf-8
"""
..  _intake-assets:

Intake Assets Backend
---------------------
"""
__author__ = "Richard Smith"
__date__ = "23 Sep 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"

# Python imports
import logging
from typing import Any, Iterator

# Thirdparty imports
import intake
from pydantic import Field

from extraction_methods.core.extraction_method import Backend, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class IntakeESMAssetsInput(Input):
    """
    Model for IntakeESM Assets Backend Input.
    """

    input_term: str = Field(
        default="$uri",
        description="term for method to run on.",
    )
    href_term: str = Field(
        default="path",
        description="term to use for href.",
    )
    datastore_kwargs: dict[str, Any] = Field(
        default={},
        description="kwargs to open datastore.",
    )
    search_kwargs: dict[str, Any] = Field(
        default={},
        description="kwargs for search.",
    )


class IntakeESMAssets(Backend):
    """
    Method: ``intake_assets``

    Description:
        Performs Search on intake catalog to provide a stream of assets for procesing.
        Uses an `Intake catalog <https://intake.readthedocs.io/>`_
        as a source for file objects.

    Configuration Options:
    .. list-table::

        - ``input_term``: The URI of a path or URL to an ESM collection JSON
          file. ``DEFAULT``: ``$uri``
        - ``href_term``: The column header which contains the URI to the file
          object. ``DEFAULT``: ``path``
        - ``catalog_kwargs``: Optional kwargs to pass to `intake.open_esm_datastore
          <https://intake-esm.readthedocs.io/en/latest
          /api.html#intake_esm.core.esm_datastore>`_
        - ``search_kwargs``: Optional kwargs to pass to `esm_datastore.search
          <https://intake-esm.readthedocs.io/en/latest
          /api.html#intake_esm.core.esm_datastore.search>`_

    Example Configuration:
    .. code-block:: yaml

        - method: intake_esm
          inputs:
            href_term: url
    """

    input_class = IntakeESMAssetsInput

    @update_input
    def run(self, body: dict[str, Any]) -> Iterator[dict[str, Any]]:

        catalog = intake.open_esm_datastore(
            self.input.input_term, **self.input.datastore_kwargs
        )

        if search_kwargs := self.input.search_kwargs:
            catalog = catalog.search(**search_kwargs)

        for _, row in catalog.df.iterrows():
            if href := getattr(row, self.input.href_term):
                yield {
                    "href": href,
                }
