#! /bin/sh

KIBANA_PREFIX="localhost:9200/.kibana"
INDEX_PATTERN="/index-pattern/network_*"
INDEX_PATTERN_SPEC="{\"title\": \"network_*\", \"timeFieldName\": \"@TimeUpdated\", \"customFormats\": {}}"
DEFAULT_INDEX="{\"defaultIndex\":\"network_*\"}"
VER="4.1.4"
CONFIG="/config/$VER"
PRETTY="?pretty"

NOT_FOUND="not found"
CREATE="/_create"
JSON_FLAG="-d"
XHEAD_PARAMS="-i"

KIBANA_LOG_FILE="/tmp/KibanaStartup.log"

if [ ! -e $KIBANA_LOG_FILE ]; then
   touch $KIBANA_LOG_FILE
fi


# Create the index pattern and specify TimeUpdated as the default time parameter
index_pattern_exists=$(curl "$XHEAD_PARAMS" -XHEAD "$KIBANA_PREFIX""$INDEX_PATTERN" | grep -i "$NOT_FOUND")
if [ $? == 0  ]; then
   echo `date +'%D %T'` "    Index pattern \"network_*\" DOES NOT exist. Creating it now..." >> $KIBANA_LOG_FILE
   echo `date +'%D %T'` "    POST returned:"                                                 >> $KIBANA_LOG_FILE
   curl -XPOST "$KIBANA_PREFIX""$INDEX_PATTERN""$CREATE""$PRETTY" -d "$INDEX_PATTERN_SPEC"   >> $KIBANA_LOG_FILE
   echo `date +'%D %T'` "    Result of -> curl -XGET $KIBANA_PREFIX$INDEX_PATTERN$PRETTY:"   >> $KIBANA_LOG_FILE
   curl -XGET "$KIBANA_PREFIX""$INDEX_PATTERN""$PRETTY"                                      >> $KIBANA_LOG_FILE
else
   echo `date +'%D %T'` "    Index pattern \"network_*\" ALREADY EXISTS."                    >> $KIBANA_LOG_FILE
fi

# Specify for our $VER config that the default index should be the newly created "network_*" index pattern
config_exists=$(curl "$XHEAD_PARAMS" -XHEAD "$KIBANA_PREFIX""$CONFIG" | grep -i "$NOT_FOUND")
if [ $? == 0  ]; then
   echo `date +'%D %T'` "    Config record for $VER DOES NOT exist. Creating it now..."      >> $KIBANA_LOG_FILE
   echo `date +'%D %T'` "    POST returned:"                                                 >> $KIBANA_LOG_FILE
   curl -XPOST "$KIBANA_PREFIX""$CONFIG""$CREATE""$PRETTY" "$JSON_FLAG" "$DEFAULT_INDEX"     >> $KIBANA_LOG_FILE
   echo `date +'%D %T'` "    Result of -> curl -XGET $KIBANA_PREFIX$CONFIG$PRETTY:"          >> $KIBANA_LOG_FILE
   curl -XGET "$KIBANA_PREFIX""$CONFIG""$PRETTY"                                             >> $KIBANA_LOG_FILE
else
   echo `date +'%D %T'` "    Config record for $VER ALREADY EXISTS."                         >> $KIBANA_LOG_FILE
fi
