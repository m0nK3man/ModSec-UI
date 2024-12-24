# libs/elasticsearch_client.py
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import pytz
from html import escape
from controller.settings_func import load_config
config = load_config()

class ElasticsearchClient:
    def __init__(self):
        self.es = Elasticsearch(
            [config['ELASTICSEARCH_CONFIG']['HOST']],
            basic_auth=(
                config['ELASTICSEARCH_CONFIG']['USER'],
                config['ELASTICSEARCH_CONFIG']['PASSWORD']
            ),
            verify_certs=False,
            ssl_show_warn=False
        )
        self.index_modsec = config['ELASTICSEARCH_CONFIG']['INDEX_MODSEC']
        self.index_access = config['ELASTICSEARCH_CONFIG']['INDEX_ACCESS']
        self.max_results = config['ELASTICSEARCH_CONFIG']['MAX_RESULTS']

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
#                "transaction.messages.message.keyword",
                "transaction.messages.details.match",
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
                   # "_source": query_fields
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
                    rule_file_truncated = rule_file[rule_file.rfind("/") + 1:]
                    rule_file_name = rule_file_truncated.replace(".conf", "")
                    rule_file_name = rule_file_name.replace("-", " ").title()

                    client_ip = source.get('transaction', {}).get('client_ip', 'N/A')
                    severity = msg.get('details', {}).get('severity', 'N/A')
                    http_code = source.get('transaction', {}).get('response', {}).get('http_code', 'N/A')
                    messages_message = msg.get('message') or msg.get('details', {}).get('match', 'N/A')
                    messages_details = msg.get('details', {}).get('data', 'N/A')

                    log_entry = {
                        'timestamp': source.get('@timestamp'),
                        'rule_id': f"{rule_file_name}---{rule_id}",
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
                "transaction.messages.message.keyword",
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
                "host_severity_breakdown": {
                    "terms": {
                        "field": "transaction.request.headers.host.keyword",
                        "size": 10
                    },
                    "aggs": {
                        "severity_breakdown": {
                            "terms": {
                                "field": "transaction.messages.details.severity.keyword",
                                "size": 5
                            }
                        }
                    }
                },
                "top_rules": {
                    "terms": {
                        "field": "transaction.messages.details.ruleId.keyword",
                        "size": 5
                    }
                },
                "top_ips": {
                    "terms": {
                        "field": "transaction.client_ip.keyword",
                        "size": 5
                    }
                },
                "top_status_code": {
                    "terms": {
                        "field": "transaction.response.http_code",
                        "size": 10
                    }
                },
                "top_attack": {
                    "terms": {
                        "field": "transaction.messages.message.keyword",
                        "size": 100
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


            # Parse results for host-severity breakdown
            host_severity = {}
            for host_bucket in response['aggregations']['host_severity_breakdown']['buckets']:
                host = host_bucket['key']
                severity_buckets = host_bucket['severity_breakdown']['buckets']
                host_severity[host] = {
                    severity['key']: severity['doc_count'] for severity in severity_buckets
                }

            top_attack = [
                bucket for bucket in response['aggregations']['top_attack']['buckets']
                if bucket['key'] != "" and "Anomaly Score Exceeded" not in bucket['key']
            ]

            return {
                'severity_breakdown': host_severity,
                'top_rules': response['aggregations']['top_rules']['buckets'][:5],
                'top_ips': response['aggregations']['top_ips']['buckets'][:5],
                'top_status_code': response['aggregations']['top_status_code']['buckets'][:10],
                'top_attack': top_attack[:10]
            }

        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}

    def get_access_logs(self, size=500, search_query=None, start_time=None, end_time=None):
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
                "http_host",
                "http_referrer",
                "http_user_agent",
                "remote_addr",
                "request",
                "status",
                "upstream_response_time"
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
                index=self.index_access,
                body={
                    "query": query,
                    "sort": [{"@timestamp": {"order": "desc"}}],
                    "size": size,
                    "_source": query_fields
                }
            )

            # Get current length
            current_length = len(response['hits']['hits'])  # Number of results returned
            # Get total matched documents
            total_hits = response['hits']['total']['value']  # Total matched documents

            # Process and format results
            logs = []
            for hit in response['hits']['hits']:
                source = hit['_source']
                log_entry = {
                    'timestamp': source.get('@timestamp', 'N/A'),
                    'http_host': source.get('http_host', 'N/A'),
                    'http_user_agent': source.get('http_user_agent', 'N/A'),
                    'client_ip': f"{source.get('remote_addr', 'N/A')}---{source.get('http_referrer', 'N/A')}",
                    'remote_addr': source.get('remote_addr', 'N/A'),
                    'request': source.get('request', 'N/A'),
                    'status': source.get('status', 'N/A'),
                    'upstream_response_time': source.get('upstream_response_time', 'N/A')
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

