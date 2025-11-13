# encoding: utf-8
"""
..  _elasticsearch-aggregation:

Elasticsearch Aggregation Method
--------------------------------
"""
__author__ = "Rhys Evans"
__date__ = "24 May 2022"
__copyright__ = "Copyright 2018 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"
__contact__ = "rhys.r.evans@stfc.ac.uk"

import logging
from collections import defaultdict
from typing import Any

# Third party imports
from elasticsearch import Elasticsearch
from pydantic import Field

from extraction_methods.core.extraction_method import ExtractionMethod
from extraction_methods.core.types import Input, KeyOutputKey

LOGGER = logging.getLogger(__name__)


class ElasticsearchAggregationInput(Input):
    """
    Model for Elasticsearch Aggregation Input.
    """

    index: str = Field(
        description="Name of the index holding the STAC entities.",
    )
    id_term: str = Field(
        description="Term used for agregating the STAC entities.",
    )
    client_kwargs: dict[str, Any] = Field(
        default={},
        description="Parameters passed to elasticsearch client.",
    )
    search_query: dict[str, Any] = Field(
        default={
            "bool": {
                "must_not": [{"term": {"categories.keyword": {"value": "hidden"}}}],
                "must": [{"term": {"path": {"value": "$uri"}}}],
            }
        },
        description="Session parameters passed to elasticsearch client.",
    )
    geo_bound: list[KeyOutputKey] = Field(
        default=[],
        description="list of terms for which the minimum of their aggregate should be returned.",
    )
    first: list[KeyOutputKey] = Field(
        default=[],
        description="list of terms for which the first record's value should be returned.",
    )
    min: list[KeyOutputKey] = Field(
        default=[],
        description="list of terms for which the minimum of their aggregate should be returned.",
    )
    max: list[KeyOutputKey] = Field(
        default=[],
        description="list of terms for which the maximum of their aggregate should be returned.",
    )
    sum: list[KeyOutputKey] = Field(
        default=[],
        description="list of terms for which the sum of their aggregate should be returned.",
    )
    mean: list[KeyOutputKey] = Field(
        default=[],
        description="list of terms for which the mean of their summed aggregate should be returned.",
    )
    bucket: list[KeyOutputKey] = Field(
        default=[],
        description="list of terms for which the list of their aggregate should be returned.",
    )
    request_tiemout: int = Field(
        default=15,
        description="Time out for search.",
    )
    allow_multiple: bool = Field(
        default=True,
        description="True if multiple labels are allowed.",
    )
    output_key: str = Field(
        default="label",
        description="key to output to.",
    )


class ElasticsearchAggregationExtract(ExtractionMethod):
    """
    Method: ``elasticsearch_aggregation``

    Description:
        Using an ID. Generate a summary of information for higher level entities.

    Configuration Options:
    .. list-table::

        - ``index``: Name of the index holding the STAC entities
        - ``id_term``: Term used for agregating the STAC entities
        - ``client_kwargs``: Session parameters passed to
        `elasticsearch.Elasticsearch<https://elasticsearch-py.readthedocs.io/en/7.10.0/api.html>`_
        - ``bbox``: list of terms for which their aggregate bbox should be returned
        - ``min``: list of terms for which the minimum of their aggregate should be returned
        - ``max``: list of terms for which the maximum of their aggregate should be returned
        - ``sum``: list of terms for which the sum of their aggregate should be returned
        - ``list``: list of terms for which a list of their aggregage should be returned

    Configuration Example:
    .. code-block:: yaml

        - method: elasticsearch_aggregation
          inputs:
            index: ceda-index
            id_term: item_id
            client_kwargs:
              hosts: ['host1:9200','host2:9200']
            bbox:
              - bbox
            min:
              - start_time
            max:
              - end_time
            sum:
              - size
            list:
              - term1
              - term2
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.es = Elasticsearch(**self.input.client_kwargs)

    @staticmethod
    def basic_aggregation(agg_type: str, facet: KeyOutputKey) -> dict[str, Any]:
        """
        Query to retrieve the minimum value from docs.

        :param agg_type: type of aggregation
        :type agg_type: str
        :param facet: facet to aggregate
        :type facet: KeyOutputKey

        :return: basic aggregation query
        :rtype: dict
        """
        return {facet.key: {agg_type: {"field": facet.key}}}

    @staticmethod
    def facet_composite_aggregation(facet: KeyOutputKey) -> dict[str, Any]:
        """
        Generate the composite aggregation for the facet.

        :param facet: facet to aggregate
        :type facet: KeyOutputKey

        :return: composite aggregation query
        :rtype: dict
        """
        return {
            facet.key: {
                "composite": {
                    "sources": [{facet.key: {"terms": {"field": facet.key}}}],
                    "size": 100,
                }
            }
        }

    def extract_facet(self, aggregations: dict[str, Any], facet: KeyOutputKey) -> Any:
        """
        Function to extract the given facets from the aggregation.

        :param input_dict: aggregations
        :type input_dict: dict
        :param facet: facet to be extracted
        :type body: KeyOutputKey

        :return: extracted facet
        :rtype: Any
        """
        if aggregation := aggregations.get(facet.key):

            if facet_value := aggregation.get("value_as_string"):
                return facet_value

            if facet_value := aggregation.get("bounds"):
                return facet_value

            if facet_value := aggregation.get("value"):
                return facet_value

    def extract_first_facet(
        self, properties: dict[str, Any], facet: KeyOutputKey
    ) -> Any:
        """
        Function to extract the given default facets from the first hit.

        :param properties: properties from first record
        :type properties: dict
        :param facet: current facet to be extracted
        :type KeyOutputKey: dict

        :return: extracted facet
        :rtype: Any
        """
        if facet_value := properties.get(facet.key):
            return facet_value

    def extract_facet_lists(
        self,
        query: dict[str, Any],
        aggregations: dict[str, Any],
        facets: list[KeyOutputKey],
    ) -> dict[str, Any]:
        """
        Function to extract the lists of given facets from the aggregation.

        :param query: attribute dictionary to update
        :type query: dict
        :param aggregations: current generated properties
        :type aggregations: dict
        :param facets: facets to be extracted
        :type facets: list

        :return: extracted list facets
        :rtype: dict
        """
        output = defaultdict(list)
        base_query = self.base_query()

        while True:
            next_query = self.base_query()
            for facet in facets:
                if aggregation := aggregations.get(facet.key):
                    output[facet.output_key].extend(
                        [bucket["key"][facet.key] for bucket in aggregation["buckets"]]
                    )

                    if hasattr(aggregation, "after_key"):
                        next_query["aggs"] |= query["aggs"][facet.key]
                        next_query["aggs"][facet.key]["composite"]["sources"][
                            "after"
                        ] = {facet.key: aggregation["after_key"][facet.key]}

            if next_query == base_query:
                break

            result = self.es.search(index=self.input.index, body=next_query)
            aggregations = result["aggregations"]

        return output

    def base_query(self) -> dict[str, Any]:
        """
        Base query to filter the results to a single collection.

        :return: base query
        :rtype: dict
        """
        return {
            "query": self.input.search_query,
            "aggs": {},
            "size": 1,
        }

    def construct_query(self) -> dict[str, Any]:
        """
        Function to create the initial elasticsearch query.

        :return: aggregation query
        :rtype: dict
        """
        query = self.base_query()

        for bbox_term in self.input.bbox:
            query["aggs"].update(self.basic_aggregation("geo_bounds", bbox_term))

        for min_term in self.input.min:
            query["aggs"].update(self.basic_aggregation("min", min_term))

        for max_term in self.input.max:
            query["aggs"].update(self.basic_aggregation("max", max_term))

        for sum_term in self.input.sum:
            query["aggs"].update(self.basic_aggregation("sum", sum_term))

        for bucket_term in self.input.bucket:
            query["aggs"].update(self.facet_composite_aggregation(bucket_term))

        return query

    def extract_metadata(
        self, query: dict[str, Any], result: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Function to extract the required metadata from the returned query result.

        :param query: previous query
        :type query: dict
        :param result: resutls from previous query
        :type result: dict

        :return: metadata
        :rtype: dict
        """
        output = {}

        properties = result["hits"]["hits"][0]["_source"]["properties"]
        aggregations = result["aggregations"]

        for facet in self.input.first:
            if facet_value := self.extract_first_facet(properties, facet):
                output[facet.output_key] = facet_value

        for facet in (
            self.input.geo_bounds + self.input.min + self.input.max + self.input.sum
        ):
            if facet_value := self.extract_facet(aggregations, facet):
                output[facet.output_key] = facet_value

        list_output = self.extract_facet_lists(query, aggregations, self.input.bucket)

        output |= list_output

        return output

    def run(self, body: dict[str, Any]) -> dict[str, Any]:

        query = self.construct_query()

        LOGGER.info("Querying Elasticsearch: %s", query)

        # Run query
        result = self.es.search(
            index=self.input.index, body=query, timeout=f"{self.input.request_tiemout}s"
        )

        # Extract metadata
        output = self.extract_metadata(query, result)

        return body | output
