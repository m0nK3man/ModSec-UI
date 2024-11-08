# libs/elasticsearch_client.py
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from libs.var import ELASTICSEARCH_CONFIG, TIME_RANGES, LOGS_CONFIG

class ElasticsearchClient:
    def __init__(self):
        self.es = Elasticsearch(
            [ELASTICSEARCH_CONFIG['HOST']],
            basic_auth=(
                ELASTICSEARCH_CONFIG['USER'],
                ELASTICSEARCH_CONFIG['PASSWORD']
            ),
            verify_certs=False,
            ssl_show_warn=False
        )
        self.index_pattern = ELASTICSEARCH_CONFIG['INDEX_PATTERN']
        self.max_results = ELASTICSEARCH_CONFIG['MAX_RESULTS']

    def get_logs(self, time_range=LOGS_CONFIG['DEFAULT_TIME_RANGE'], 
                size=None, search_query=None):
        """
        Query Elasticsearch for ModSecurity logs
        """
        try:
            # Use provided size or default from config
            size = size or self.max_results
            
            # Calculate time range
            now = datetime.utcnow()
            if time_range.endswith('m'):
                from_time = now - timedelta(minutes=int(time_range[:-1]))
            elif time_range.endswith('h'):
                from_time = now - timedelta(hours=int(time_range[:-1]))
            elif time_range.endswith('d'):
                from_time = now - timedelta(days=int(time_range[:-1]))
            
            # Base query
            query = {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": from_time.isoformat(),
                                    "lte": now.isoformat()
                                }
                            }
                        }
                    ]
                }
            }

            # Add search query if provided
            if search_query:
                query["bool"]["must"].append({
                    "query_string": {
                        "query": search_query,
                        "fields": ["message", "rule_id", "request.headers.host", 
                                 "client_ip", "request.uri"]
                    }
                })

            # Execute search
            response = self.es.search(
                index=self.index_pattern,
                body={
                    "query": query,
                    "sort": [{"@timestamp": {"order": "desc"}}],
                    "size": size
                }
            )

            # Process and format results
            logs = []
            for hit in response['hits']['hits']:
                source = hit['_source']
                log_entry = {
                    'timestamp': source.get('@timestamp'),
                    'rule_id': source.get('rule_id', 'N/A'),
                    'message': source.get('message', 'N/A'),
                    'severity': source.get('severity', 'N/A'),
                    'client_ip': source.get('client_ip', 'N/A'),
                    'request_uri': source.get('request', {}).get('uri', 'N/A'),
                    'request_method': source.get('request', {}).get('method', 'N/A'),
                    'hostname': source.get('request', {}).get('headers', {}).get('host', 'N/A')
                }
                logs.append(log_entry)

            return logs

        except Exception as e:
            print(f"Error querying Elasticsearch: {e}")
            return []

    def get_stats(self, time_range=LOGS_CONFIG['DEFAULT_TIME_RANGE']):
        """
        Get statistics about ModSecurity events
        """
        try:
            now = datetime.utcnow()
            if time_range.endswith('m'):
                from_time = now - timedelta(minutes=int(time_range[:-1]))
            elif time_range.endswith('h'):
                from_time = now - timedelta(hours=int(time_range[:-1]))
            elif time_range.endswith('d'):
                from_time = now - timedelta(days=int(time_range[:-1]))

            response = self.es.search(
                index=self.index_pattern,
                body={
                    "query": {
                        "range": {
                            "@timestamp": {
                                "gte": from_time.isoformat(),
                                "lte": now.isoformat()
                            }
                        }
                    },
                    "aggs": {
                        "severity_breakdown": {
                            "terms": {
                                "field": "severity.keyword",
                                "size": LOGS_CONFIG['MAX_STATS_ITEMS']
                            }
                        },
                        "top_rules": {
                            "terms": {
                                "field": "rule_id.keyword",
                                "size": LOGS_CONFIG['MAX_STATS_ITEMS']
                            }
                        },
                        "top_ips": {
                            "terms": {
                                "field": "client_ip.keyword",
                                "size": LOGS_CONFIG['MAX_STATS_ITEMS']
                            }
                        }
                    },
                    "size": 0
                }
            )

            return {
                'severity_breakdown': response['aggregations']['severity_breakdown']['buckets'],
                'top_rules': response['aggregations']['top_rules']['buckets'],
                'top_ips': response['aggregations']['top_ips']['buckets']
            }

        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
