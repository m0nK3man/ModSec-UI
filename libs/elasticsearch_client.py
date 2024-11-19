# libs/elasticsearch_client.py
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from libs.var import ELASTICSEARCH_CONFIG, LOGS_CONFIG
import pytz

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

    def get_logs(self, size=5000, search_query=None, start_time=None, end_time=None):
        try:
            # Use provided size or default from config
            size = size or self.max_results

            # Set up timezone
            tz_utc = pytz.UTC
            tz_utc7 = pytz.timezone('Asia/Bangkok')  # UTC+7 timezone

            # Calculate time range
            now = datetime.now(tz_utc7)  # Get current time in UTC+7

            if start_time and end_time:
                # Convert ISO format strings to timezone-aware datetimes
                from_time = datetime.fromisoformat(start_time)
                to_time = datetime.fromisoformat(end_time)

                # If the input times are naive (no timezone info), assume they're in UTC+7
                if from_time.tzinfo is None:
                    from_time = tz_utc7.localize(from_time)
                if to_time.tzinfo is None:
                    to_time = tz_utc7.localize(to_time)
            else:
                 print(f"Start and end time NULL")
                 return []

            # Convert times to UTC for Elasticsearch query
            from_time_utc = from_time.astimezone(tz_utc)
            to_time_utc = to_time.astimezone(tz_utc)

            # Base query
            query = {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": from_time_utc.isoformat(),
                                    "lte": to_time_utc.isoformat()
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
                        "fields": ["message", "rule_id", "request.headers.host", "client_ip", "request.uri"]
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
                # Extracting details from the log structure
                messages = source.get('transaction', {}).get('messages', [])
                for msg in messages:
                    request_host = source.get('transaction', {}).get('request', {}).get('headers', {}).get('Host', source.get('transaction', {}).get('request', {}).get('headers', {}).get('host', 'N/A'))
                    client_info = source.get('transaction', {}).get('request', {}).get('headers', {}).get('Clientinfo', source.get('transaction', {}).get('request', {}).get('headers', {}).get('clientinfo', 'N/A'))
                    user_agent = source.get('transaction', {}).get('request', {}).get('headers', {}).get('User-Agent', source.get('transaction', {}).get('request', {}).get('headers', {}).get('user-agent', 'N/A'))
                    log_entry = {
                        'timestamp': source.get('transaction', {}).get('time_stamp'),
                        'rule_id': msg.get('details', {}).get('ruleId', 'N/A'),  # Rule ID from message details
                        'severity': msg.get('details', {}).get('severity', 'N/A'),  # Severity from message details
                        # Merge 'client_ip' and 'client_info' fields
                        'client_ip': f"{source.get('transaction', {}).get('client_ip', 'N/A')}---{client_info}",
                        'request_host': f"{request_host}---{source.get('transaction', {}).get('request', {}).get('uri', 'N/A')}",
                        'http_code': source.get('transaction', {}).get('response', {}).get('http_code', 'N/A'),
                        'user_agent': user_agent,
                        # Merging 'detail' and 'message' fields
                        'message': f"{msg.get('message', 'N/A')}---{msg.get('details', {}).get('data', 'N/A')}"
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
                                "field": "transaction.messages.details.severity.keyword",
                                "size": LOGS_CONFIG['MAX_STATS_ITEMS']
                            }
                        },
                        "top_rules": {
                            "terms": {
                                "field": "transaction.messages.details.ruleId.keyword",
                                "size": LOGS_CONFIG['MAX_STATS_ITEMS']
                            }
                        },
                        "top_ips": {
                            "terms": {
                                "field": "transaction.client_ip.keyword",
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
