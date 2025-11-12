# encoding: utf-8
"""
..  _elasticsearch-assets:

Elasticsearch Assets Backend
----------------------------
"""
__author__ = "Rhys Evans"
__date__ = "24 May 2022"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"

import logging
from typing import Any, Iterator

# Third party imports
from elasticsearch import Elasticsearch as Elasticsearch_client
from pydantic import Field

from extraction_methods.core.extraction_method import Backend, update_input
from extraction_methods.core.types import Input

LOGGER = logging.getLogger(__name__)


class ElasticsearchAssetsInput(Input):
    """
    Model for Elasticsearch Assets Backend Input.
    """

    index: str = Field(
        description="Elasticsearch index to search on.",
    )
    client_kwargs: dict[str, Any] = Field(
        default={},
        description="Elasticsearch connection kwargs.",
    )
    request_timeout: int = Field(
        default=60,
        description="Request timeout for search.",
    )
    body: dict[str, Any] = Field(
        description="Body for Elasticsearch search request.",
    )
    href_term: str = Field(
        default="path",
        description="term to use for href.",
    )


class ElasticsearchAssets(Backend):
    """
    Method: ``elasticsearch_assets``

    Description:
        Using an ID. Generate a summary of information for higher level entities.

    Configuration Options:
    .. list-table::

        - ``index``: Name of the index holding the STAC entities
        - ``client_kwargs``: Parameters to pass to
          `elasticsearch.Elasticsearch<https://elasticsearch-py.readthedocs.io/en/7.10.0/api.html>`_
        - ``request_timeout``: Timeout for the Elasticsearch request.
        - ``body``: list of terms for which their aggregate bbox should be returned.
        - ``id_term``: Term used for agregating the STAC entities

    Configuration Example:
    .. code-block:: yaml

        - name: elasticsearch
          inputs:
            index: ceda-index
            id_term: item_id
            client_kwargs:
                hosts: ['host1:9200','host2:9200']
            fields:
                - roles
    """

    input_class = ElasticsearchAssetsInput

    @update_input
    def run(self, body: dict[str, Any]) -> Iterator[dict[str, Any]]:

        es = Elasticsearch_client(**self.input.client_kwargs)

        es_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "regexp": {
                                f"{self.input.search_field}.keyword": {
                                    "value": self.input.regex,
                                }
                            }
                        },
                        {"exists": {"field": "md5"}},
                    ],
                    "must_not": [{"exists": {"field": "removed"}}],
                },
            },
            "_source": [self.input.href_term, self.input.search_field]
            + [extra_field.key for extra_field in self.input.extra_fields],
        }

        # Run search
        result = es.search(
            index=self.input.index,
            body=es_body,
            timeout=f"{self.input.request_timeout}s",
        )

        for hit in result["hits"]["hits"]:
            source = hit["_source"]
            asset = {
                "href": source[self.input.href_term],
            }

            for field in self.input.extra_fields:
                if value := source.get(field.key):
                    asset[field.output_key] = value

            yield asset
