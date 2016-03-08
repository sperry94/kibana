#! /bin/sh

KIBANA_PREFIX="localhost:9200/.kibana"
INDEX_PATTERN="/index-pattern/network_*"
INDEX_PATTERN_SPEC="{\"title\": \"network_*\", \"timeFieldName\": \"@TimeUpdated\", \"customFormats\": {}}"
DEFAULT_INDEX="{\"defaultIndex\":\"network_*\"}"
CONFIG="/config/4.1.4"

NOT_FOUND="not found"
CREATE="/_create"
JSON_FLAG="-d"
XHEAD_PARAMS="-i"

# Create the index pattern and specify TimeUpdated as the default time parameter
index_pattern_exists=$(curl "$XHEAD_PARAMS" -XHEAD "$KIBANA_PREFIX""$INDEX_PATTERN" | grep -i "$NOT_FOUND")
if [ $? == 0  ]; then
   echo "Index pattern \"network_*\" DOES NOT exist"
   curl -XPOST "$KIBANA_PREFIX""$INDEX_PATTERN""$CREATE" -d "$INDEX_PATTERN_SPEC"
else
   echo "Index pattern \"network_*\" DOES exist"
fi

# Check to see if the kibana/config index exists already
#   If it does not, create it before updating it
config_exists=$(curl "$XHEAD_PARAMS" -XHEAD "$KIBANA_PREFIX""$CONFIG" | grep -i "$NOT_FOUND")
if [ $? == 0  ]; then
   echo "Config record DOES NOT exist"
   curl -XPUT "$KIBANA_PREFIX""$CONFIG""$CREATE" "$JSON_FLAG" "$DEFAULT_INDEX"
else
   echo "Config record DOES exist"
fi

# Update the config so that the network_* index pattern is set as the default index
#curl -XPOST "$KIBANA_PREFIX"/config/4.1.4/_update "$JSON_FLAG" "$DEFAULT_INDEX"
