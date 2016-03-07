#! /bin/sh

XHEAD_PARAMS="-i"
KIBANA_PREFIX="localhost:9200/.kibana"
NOT_FOUND="not found"
INDEX_PATTERN="{\"title\": \"network_*\", \"timeFieldName\": \"@TimeUpdated\", \"customFormats\": {}}"
DEFAULT_INDEX="{\"doc\":{\"doc\":{\"defaultIndex\":\"network_*\"},\"defaultIndex\":\"network_*\"}}"
JSON_FLAG="-d"

echo "START"
curl -XPOST localhost:9200/.kibana/index-pattern/network_*/?op_type=create -d "$INDEX_PATTERN"
echo "CREATED"
config_exists=$(curl "$XHEAD_PARAMS" -XHEAD "$KIBANA_PREFIX"/config | grep -i "$NOT_FOUND")
if [ $? == 0  ]; then
   echo "Config record DOES NOT exist"
   curl -XPUT "$KIBANA_PREFIX"/config/4.1.4/_create "$JSON_FLAG" "$DEFAULT_INDEX"
else
   echo "Config record DOES exist"
fi

echo "Config should exist at this point"
curl -XPOST "$KIBANA_PREFIX"/config/4.1.4/_update "$JSON_FLAG" "$DEFAULT_INDEX"

echo "END"
