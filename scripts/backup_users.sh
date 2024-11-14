#!/bin/bash
DB=modsec_ui
TB=modsec_users
if [ -e /tmp/$TB.sql ]; then
    echo "File /tmp/$TB.sql exists"
else
    sudo -u postgres psql -d $DB -c "\! pg_dump -d $DB -t $TB -F p -f /tmp/$TB.sql"
    echo "File backup successfully to /tmp/$TB.sql"
    sudo mv /tmp/$TB.sql $(pwd)/database/$TB.sql
    echo "File moved to $(pwd)/database/$TB.sql"
fi

