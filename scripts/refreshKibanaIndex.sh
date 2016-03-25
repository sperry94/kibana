#! /bin/sh

ES_HEAD="localhost:9200"
KIBANA_PREFIX="$ES_HEAD/.kibana/"

CURL="curl -g"
REFRESH="/_refresh"

KIBANA_LOG_FILE="/var/log/probe/KibanaStartup.log"

if [ ! -e $KIBANA_LOG_FILE ]; then
   touch $KIBANA_LOG_FILE
fi

echo `date +'%D %T'` "   Refreshing Kibana index..." >> $KIBANA_LOG_FILE
$CURL -XPOST "$KIBANA_PREFIX""$REFRESH""$PRETTY"     >> $KIBANA_LOG_FILE
