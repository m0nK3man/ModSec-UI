import os

# config.py
LOCAL_CONF_PATH = "local-conf/"
MODSECURITY_CONF_PATH = 'local-conf/modsecurity.conf'
CRS_CONF_PATH = 'local-conf/crs/crs-setup.conf'
MODSECURITY_RULES_DIR = 'local-conf/crs/rules'

# GIT
GIT_REPO_PATH = '/root/modsec-ui'  # Parent directory of rules
GIT_AUTHOR_NAME = "ModSecurity UI"
GIT_AUTHOR_EMAIL = "modsec-ui@bravo.com"

# Elasticsearch Configuration
ELASTICSEARCH_CONFIG = {
    'HOST': os.getenv('ELASTICSEARCH_HOST', 'https://172.16.20.31:9200'),
    'USER': os.getenv('ELASTICSEARCH_USER', 'elastic'),
    'PASSWORD': os.getenv('ELASTICSEARCH_PASSWORD', 'BravoSOC@2024'),
    'INDEX_PATTERN': os.getenv('ELASTICSEARCH_INDEX', 'modsec-*'),
    'MAX_RESULTS': int(os.getenv('ELASTICSEARCH_MAX_RESULTS', 100)),
}

# Time range options for logs
TIME_RANGES = {
    '15m': '15 minutes',
    '30m': '30 minutes',
    '1h': '1 hour',
    '3h': '3 hours',
    '6h': '6 hours',
    '12h': '12 hours',
    '1d': '1 day',
    '7d': '7 days'
}

# Severity levels and their corresponding colors
SEVERITY_LEVELS = {
    'CRITICAL': '#ff4444',
    'ERROR': '#ff8800',
    'WARNING': '#ffbb33',
    'NOTICE': '#00C851',
    'INFO': '#33b5e5'
}

# Logs configuration
LOGS_CONFIG = {
    'REFRESH_INTERVAL': int(os.getenv('LOGS_REFRESH_INTERVAL', 30)),  # in seconds
    'DEFAULT_TIME_RANGE': '15m',
    'STATS_REFRESH_INTERVAL': int(os.getenv('STATS_REFRESH_INTERVAL', 60)),  # in seconds
    'MAX_STATS_ITEMS': int(os.getenv('MAX_STATS_ITEMS', 5))
}
