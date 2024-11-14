#!/bin/bash
if [ -e /tmp/modsec_rules.sql ]; then
    echo "File /tmp/modsec_rules.sql exists"
else
    sudo -u postgres psql -d modsec_ui -c "\! pg_dump -d modsec_ui -t modsec_rules -F p -f /tmp/modsec_rules.sql"
    echo "File backup successfully to /tmp/modsec_rules.sql"
fi

