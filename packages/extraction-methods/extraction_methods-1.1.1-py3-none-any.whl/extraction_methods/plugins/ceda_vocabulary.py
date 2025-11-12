# encoding: utf-8
"""
..  _ceda-vocabulary:

CEDA Vocabulary Method
----------------------
"""
__author__ = "Richard Smith"
__date__ = "27 May 2021"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "richard.d.smith@stfc.ac.uk"


# Python imports
import logging
from typing import Any

import httpx
from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class CEDAVocabularyInput(Input):
    """
    Model for CEDA Vocab Method Input.
    """

    url: str = Field(
        description="URL of vocabulary server.",
    )
    namespace: str = Field(
        description="Namespace for vocab terms.",
    )
    strict: bool = Field(
        default=False,
        description="True if values should be validated.",
    )
    terms: list[str] = Field(
        default=[],
        description="terms to be validated.",
    )
    request_timeout: int = Field(
        default=15,
        description="request time out.",
    )


class CEDAVocabularyExtract(ExtractionMethod):
    """
    Method: ``ceda_vocabulary``

    Description:
        Validates and sorts properties into vocabs and generates
        the `general` vocab for specified properties.

    Configuration Options:
    .. list-table::

        - ``url``: ``REQUIRED`` url of vocabulary server
        - ``namespace``: ``REQUIRED`` namespace of vocab for terms
        - ``terms``: Terms to be validated
        - ``strict``: Boolean on whether values should be validated
        - ``request_timeout``: request time out

    Example configuration:
    .. code-block:: yaml

        - method: ceda_vocabulary
          inputs:
            url: vocab.ceda.ac.uk
            namespace: cmip6
            strict: False
            terms:
              - start_time
              - model
    """

    input_class = CEDAVocabularyInput

    @update_input
    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        properties = body

        if "unspecified_vocab" in body:
            properties = body["unspecified_vocab"]

        req_data = {
            "namespace": self.input.namespace,
            "terms": self.input.terms,
            "properties": properties,
            "strict": self.input.strict,
        }

        response = httpx.post(
            self.input.url,
            json=req_data,
            timeout=self.input.request_timeout,
        )

        if response.status_code != 200:
            raise Exception(
                f"Bad response from vocab server: {response.status_code}, reason: {response.text}"
            )

        json_response = response.json()

        if json_response["error"]:
            raise Exception(f"Vocab request failed, reason: {json_response['text']}")

        body = body | json_response["result"]

        if "vocabs" in body:
            body["vocabs"].append(self.input.namespace)

        else:
            body["vocabs"] = self.input.namespace

        return body
