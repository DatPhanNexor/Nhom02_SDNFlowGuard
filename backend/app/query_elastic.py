from elasticsearch import Elasticsearch


def get_documents_by_ip(elk_host, username, password, ip_address):
    """Retrieve documents from relevant Elasticsearch indices matching ip_address."""
    kwargs = {}
    if username and password:
        kwargs["basic_auth"] = (username, password)

    es = Elasticsearch(elk_host, **kwargs)
    if not es.ping():
        raise ConnectionError(f"Unable to connect to Elasticsearch at {elk_host}")

    indices_and_fields = {
        "ad-logs*": "host.ip.keyword",
        "dns-logs*": "host.ip.keyword",
        "elastiflow*": "client.ip.keyword",
        "cowrie-logs*": "host.ip.keyword",
        "sdnflowguard-events-*": "switch_id.keyword",
    }

    results = {}
    for index, field in indices_and_fields.items():
        query = {
            "query": {"match": {field: ip_address}},
            "sort": [{"@timestamp": {"order": "desc"}}],
        }
        try:
            response = es.search(index=index, body=query, size=50)
            documents = [hit["_source"] for hit in response["hits"]["hits"]]
            results[index] = documents
        except Exception as exc:
            results[index] = f"Error querying index: {str(exc)}"
    return results
