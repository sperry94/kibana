#! /bin/sh

ES_HEAD="localhost:9200"
KIBANA_PREFIX="$ES_HEAD/.kibana"
INDEX_PATTERN="/index-pattern/network_*"
INDEX_PATTERN_SPEC="{\"title\": \"network_*\", \"timeFieldName\": \"TimeUpdated\"}"
DEFAULT_INDEX="{\"defaultIndex\":\"network_*\"}"
VER="4.1.4"
CONFIG="/config/$VER"
PRETTY="?pretty"
TOP_LEVEL_DIR="/usr/local/kibana-$VER-linux-x64"
MAPPINGS="$TOP_LEVEL_DIR/resources/mappings.json"

NOT_FOUND="404"
CREATE="/_create"
UPDATE="/_update"
JSON_FLAG="-d"
XHEAD_PARAMS="-i"
SILENT="-q"
CASE_INSENS="-i"

KIBANA_LOG_FILE="/var/log/probe/KibanaStartup.log"

if [ ! -e $KIBANA_LOG_FILE ]; then
   touch $KIBANA_LOG_FILE
fi

# Create the index pattern and specify TimeUpdated as the default time parameter
curl "$XHEAD_PARAMS" -XHEAD "$KIBANA_PREFIX""$INDEX_PATTERN" | grep "$SILENT" "$NOT_FOUND"
index_pattern_exists=$?
if [ "$index_pattern_exists" -eq "0"  ]; then
   echo `date +'%D %T'` "  Index pattern \"network_*\" DOES NOT exist. Creating it now..." >> $KIBANA_LOG_FILE
   echo `date +'%D %T'` "  POST returned:"                                                 >> $KIBANA_LOG_FILE
   curl -XPOST "$KIBANA_PREFIX""$INDEX_PATTERN""$CREATE""$PRETTY" -d "$INDEX_PATTERN_SPEC" >> $KIBANA_LOG_FILE
   echo `date +'%D %T'` "  Result of -> curl -XGET $KIBANA_PREFIX$INDEX_PATTERN$PRETTY:"   >> $KIBANA_LOG_FILE
   curl -XGET "$KIBANA_PREFIX""$INDEX_PATTERN""$PRETTY"                                    >> $KIBANA_LOG_FILE
else
   echo `date +'%D %T'` "  Index pattern \"network_*\" ALREADY EXISTS."                    >> $KIBANA_LOG_FILE
fi

# Check for our custom field mappings
#
# BUG NOTICE: When the Kibana service starts, the first thing it does is check its default
#             index-pattern and re-pull all of that metadata from elasticsearch. In our case,
#             that means it goes to all the network_* indeces and re-caches the field names
#             and updates the index-pattern/network_* record to reflect the fields it found.
#
#             There is a bug in Kibana 4.1 where when a record gets updated, specifically the
#             key-value pair of "fieldFormatMap" gets overwritten. The bug report for it can
#             be found here: https://github.com/elastic/kibana/issues/4309
#
#             This means that everytime Kibana restarts, we will lose our custom mappings.
#             Fortunately this script checks for the "fieldFormatMap" on every Kibana startup,
#             so we are always reloading our mappings succesfully. You will see this
#             reflected in the Kibana startup log.
curl -XGET localhost:9200/.kibana/index-pattern/network_* | grep -q "fieldFormatMap"
field_format_map_exists=$?
if [ "$field_format_map_exists" -ne "0" ]; then
   echo `date +'%D %T'` "  Custom fieldFormatMap doesn't exist. Creating it..."            >> $KIBANA_LOG_FILE
   echo `date +'%D %T'` "  POST returned:"                                                 >> $KIBANA_LOG_FILE
   curl -XPOST "$KIBANA_PREFIX""$INDEX_PATTERN""$UPDATE" "$JSON_FLAG" @$MAPPINGS           >> $KIBANA_LOG_FILE
   echo `date +'%D %T'` "  Result of -> curl -XGET $KIBANA_PREFIX$INDEX_PATTERN$PRETTY:"   >> $KIBANA_LOG_FILE
   curl -XGET "$KIBANA_PREFIX""$INDEX_PATTERN""$PRETTY"                                    >> $KIBANA_LOG_FILE
else
   echo `date +'%D %T'` "  Custom fieldFormatMap already exists."                          >> $KIBANA_LOG_FILE
fi

# Specify for our $VER config that the default index should be the newly created "network_*" index pattern
curl "$XHEAD_PARAMS" -XHEAD "$KIBANA_PREFIX""$CONFIG" | grep "$SILENT" "$NOT_FOUND"
config_exists=$?
if [ "$config_exists" -eq "0"  ]; then
   echo `date +'%D %T'` "  Config record for $VER DOES NOT exist. Creating it now..."      >> $KIBANA_LOG_FILE
   echo `date +'%D %T'` "  POST returned:"                                                 >> $KIBANA_LOG_FILE
   curl -XPOST "$KIBANA_PREFIX""$CONFIG""$CREATE""$PRETTY" "$JSON_FLAG" "$DEFAULT_INDEX"   >> $KIBANA_LOG_FILE
   echo `date +'%D %T'` "  Result of -> curl -XGET $KIBANA_PREFIX$CONFIG$PRETTY:"          >> $KIBANA_LOG_FILE
   curl -XGET "$KIBANA_PREFIX""$CONFIG""$PRETTY"                                           >> $KIBANA_LOG_FILE
else
   echo `date +'%D %T'` "  Config record for $VER ALREADY EXISTS."                         >> $KIBANA_LOG_FILE
fi

# If you stop XDELETE the kibana index while kibana is still running, it can rebuild the
#  config type with ID 4.1.4 on its own. We need to check for this and update the record
#  to include "defaultIndex": "network_*"

curl -XGET "$KIBANA_PREFIX""$CONFIG" | grep "$SILENT" '\"defaultIndex\":\"network_\*\"'
config_has_default_index=$?
if [ "$config_has_default_index" -ne "0" ]; then
   echo `date +'%D %T'` "  Config for $VER exists, but no default index is specified"      >> $KIBANA_LOG_FILE
   echo `date +'%D %T'` "  Updating config/$VER record with default index \"network_*\""   >> $KIBANA_LOG_FILE
   curl -XPOST "$KIBANA_PREFIX""$CONFIG""$UPDATE" "$JSON_FLAG" "{\"doc\": $DEFAULT_INDEX}" >> $KIBANA_LOG_FILE
   echo `date +'%D %T'` "  Result of -> curl -XGET $KIBANA_PREFIX$CONFIG$PRETTY:"          >> $KIBANA_LOG_FILE
   curl -XGET "$KIBANA_PREFIX""$CONFIG""$PRETTY"                                           >> $KIBANA_LOG_FILE
else
   echo `date +'%D %T'` "  defaultIndex parameter for index pattern \"network_*\" is set"  >> $KIBANA_LOG_FILE
fi




