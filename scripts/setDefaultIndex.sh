#! /bin/sh

XHEAD_PARAMS="-i"
KIBANA_PREFIX="localhost:9200/.kibana"
NOT_FOUND="not found"
INDEX_PATTERN="{\"title\": \"network_*\", \"timeFieldName\": \"@TimeUpdated\", \"customFormats\": {}}"
DEFAULT_INDEX="{\"doc\":{\"doc\":{\"defaultIndex\":\"network_*\"},\"defaultIndex\":\"network_*\"}}"
JSON_FLAG="-d"

# Create the index pattern and specify TimeUpdated as the default time parameter
curl -XPOST "$KIBANA_PREFIX"/index-pattern/network_*/?op_type=create -d "$INDEX_PATTERN"

# Check to see if the kibana/config index exists already
#   If it does not, create it before updating it
config_exists=$(curl "$XHEAD_PARAMS" -XHEAD "$KIBANA_PREFIX"/config | grep -i "$NOT_FOUND")
if [ $? == 0  ]; then
   echo "Config record DOES NOT exist"
   curl -XPUT "$KIBANA_PREFIX"/config/4.1.4/_create "$JSON_FLAG" "$DEFAULT_INDEX"
else
   echo "Config record DOES exist"
fi

# Update the config so that the network_* index pattern is set as the default index
curl -XPOST "$KIBANA_PREFIX"/config/4.1.4/_update "$JSON_FLAG" "$DEFAULT_INDEX"
