#! /bin/sh
KIBANA_LOG_FILE="/var/log/probe/KibanaStartup.log"

if [ ! -e $KIBANA_LOG_FILE ]; then
   touch $KIBANA_LOG_FILE
fi

echo `date +'%D %T'` "   Refreshing Kibana index..." >> $KIBANA_LOG_FILE
curl -g -XPOST localhost:9200/.kibana/_refresh?pretty     >> $KIBANA_LOG_FILE
