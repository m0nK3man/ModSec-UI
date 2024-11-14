#!/bin/bash
if [ -e /tmp/modsec_users.sql ]; then
    echo "File /tmp/modsec_users.sql exists"
else
    sudo -u postgres psql -d modsec_ui -c "\! pg_dump -d modsec_ui -t modsec_users -F p -f /tmp/modsec_users.sql"
    echo "File backup successfully to /tmp/modsec_users.sql"
fi

