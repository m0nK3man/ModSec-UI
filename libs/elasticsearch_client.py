# libs/elasticsearch_client.py
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
from libs.var import ELASTICSEARCH_CONFIG, LOGS_CONFIG
import pytz
from html import escape

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
        self.index_modsec = ELASTICSEARCH_CONFIG['INDEX_MODSEC']
        self.max_results = ELASTICSEARCH_CONFIG['MAX_RESULTS']

    def calculate_time_utc(self, base_time):
        # Set up timezones
        tz_utc = pytz.UTC
        tz_utc7 = pytz.timezone('Asia/Bangkok')  # UTC+7 timezone

        # Convert ISO format string to a timezone-aware datetime
        utc_time = datetime.fromisoformat(base_time)

        # If the input time is naive (no timezone info), assume it's in UTC+7
        if utc_time.tzinfo is None:
            utc_time = tz_utc7.localize(utc_time)

        # Convert the time to UTC for Elasticsearch query
        return utc_time.astimezone(tz_utc)

    def get_modsec_logs(self, size=500, search_query=None, start_time=None, end_time=None):
        try:
            # Use provided size or default from config
            size = size or self.max_results
            
            # Convert and validate times
            if not start_time or not end_time:
                return {"logs": [], "current_length": 0, "total_hits": 0}

            # Convert times to UTC for Elasticsearch query
            from_time_utc = self.calculate_time_utc(start_time)
            to_time_utc = self.calculate_time_utc(end_time)

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
            
            query_fields = [
                "@timestamp",
                "transaction.messages.message",
                "transaction.messages.details.ruleId",
                "transaction.messages.details.file",
                "transaction.messages.details.severity",
                "transaction.messages.details.data",
                "transaction.client_ip",
                "transaction.request.headers.Host",
                "transaction.request.headers.host",
                "transaction.request.uri",
                "transaction.response.http_code",
                "transaction.request.headers.User-Agent",
                "transaction.request.headers.user-agent"
            ]
            
            # Add search query if provided
            if search_query:
                query["bool"]["must"].append({
                    "query_string": {
                        "query": search_query,
                        "fields": query_fields
                    }
                })
    
            # Execute search (limit return source for quick query)
            response = self.es.search(
                index=self.index_modsec,
                body={
                    "query": query,
                    "sort": [{"@timestamp": {"order": "desc"}}],
                    "size": size,
                    "_source": query_fields
                }
            )

            # Get current length
            current_length = len(response['hits']['hits'])  # Số lượng kết quả trả về
            # Get total matched documents
            total_hits = response['hits']['total']['value']  # Tổng số kết quả phù hợp

            # Process and format results
            logs = []
            for hit in response['hits']['hits']:
                source = hit['_source']
                # Extracting details from the log structure
                messages = source.get('transaction', {}).get('messages', [])
                for msg in messages:

                    request_host = source.get('transaction', {}).get('request', {}).get('headers', {}).get('Host', source.get('transaction', {}).get('request', {}).get('headers', {}).get('host', 'N/A'))
                    client_info = source.get('transaction', {}).get('request', {}).get('headers', {}).get('Clientinfo', source.get('transaction', {}).get('request', {}).get('headers', {}).get('clientinfo', 'N/A'))
                    raw_user_agent = source.get('transaction', {}).get('request', {}).get('headers', {}).get('User-Agent', source.get('transaction', {}).get('request', {}).get('headers', {}).get('user-agent', 'N/A'))
                    user_agent = escape(raw_user_agent)

                    uri = escape(source.get('transaction', {}).get('request', {}).get('uri', 'N/A'))
                    rule_id = msg.get('details', {}).get('ruleId', 'N/A')
                    rule_file = msg.get('details', {}).get('file', 'N/A')
                    client_ip = source.get('transaction', {}).get('client_ip', 'N/A')
                    severity = msg.get('details', {}).get('severity', 'N/A')
                    http_code = source.get('transaction', {}).get('response', {}).get('http_code', 'N/A')
                    messages_message = msg.get('message', 'N/A')
                    messages_details = msg.get('details', {}).get('data', 'N/A')

                    log_entry = {
                        'timestamp': source.get('@timestamp'),
                        'rule_id': f"{rule_id}---{rule_file}",
                        'severity': severity,
                        'client_ip': f"{client_ip}---{client_info}",
                        'request_host': f"{request_host}---{uri}",
                        'http_code': http_code,
                        'user_agent': user_agent,
                        'message': f"{messages_message}---{messages_details}"
                    }
                    logs.append(log_entry)

            return {
                "logs": logs,
                "current_length": current_length,
                "total_hits": total_hits
            }
    
        except Exception as e:
            print(f"Elasticsearch query error: {e}")
            return {"logs": [], "current_length": 0, "total_hits": 0}

    def get_modsec_stats(self, size=500, search_query=None, start_time=None, end_time=None):
        try:
             # Use provided size or default from config
            size = size or self.max_results
            
            # Convert and validate times
            if not start_time or not end_time:
                return {}

            # Convert times to UTC for Elasticsearch query
            from_time_utc = self.calculate_time_utc(start_time)
            to_time_utc = self.calculate_time_utc(end_time)

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
            
            query_fields = [
                "@timestamp",
                "transaction.messages.message",
                "transaction.messages.details.ruleId",
                "transaction.messages.details.file",
                "transaction.messages.details.severity",
                "transaction.messages.details.data",
                "transaction.client_ip",
                "transaction.request.headers.Host",
                "transaction.request.headers.host",
                "transaction.request.uri",
                "transaction.response.http_code",
                "transaction.request.headers.User-Agent",
                "transaction.request.headers.user-agent"
            ]
            
            # Add search query if provided
            if search_query:
                query["bool"]["must"].append({
                    "query_string": {
                        "query": search_query,
                        "fields": query_fields
                    }
                })
            
            # Base arguments
            aggs = {
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
            }

            # Execute search
            response = self.es.search(
                index=self.index_modsec,
                body={
                    "query": query,
                    "aggs": aggs,
                    "size": size
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
