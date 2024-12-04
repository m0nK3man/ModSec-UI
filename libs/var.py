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
    'INDEX_MODSEC': os.getenv('ELASTICSEARCH_INDEX', 'modsec-*'),
    'INDEX_ACCESS': os.getenv('ELASTICSEARCH_INDEX', 'nginx-access-logs-*'),
    'INDEX_ERROR': os.getenv('ELASTICSEARCH_INDEX', 'nginx-error-logs-*'),
    'MAX_RESULTS': int(os.getenv('ELASTICSEARCH_MAX_RESULTS', 100)),
}

# Logs configuration
LOGS_CONFIG = {
    'REFRESH_INTERVAL': int(os.getenv('LOGS_REFRESH_INTERVAL', 30)),  # in seconds
    'DEFAULT_TIME_RANGE': '15m',
    'STATS_REFRESH_INTERVAL': int(os.getenv('STATS_REFRESH_INTERVAL', 60)),  # in seconds
#    'MAX_STATS_ITEMS': int(os.getenv('MAX_STATS_ITEMS', 5))
}
