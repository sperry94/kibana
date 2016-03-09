#! /bin/sh

KIBANA_PREFIX="localhost:9200/.kibana"
VER="4.1.4"
DASHBOARDS="dashboards"
VISUALIZATIONS="visualizations"
SEARCHES="searches"

TOP_LEVEL_DIR="/usr/local/kibana-$VER-linux-x64"

# Directories directly under the kibana folder include:
#   dashboards
#   visualizations
#   searches

cd "$TOP_LEVEL_DIR"

# DASHBOARDS
for file in $TOP_LEVEL_DIR/$DASHBOARDS/*.json
do
    FILENAME=${file##*/}
    KIBANA_ID=${FILENAME%.*}
    echo "Filename is $FILENAME:"
    echo "  KIBANA_ID is  $KIBANA_ID:"
    curl -XPOST ${KIBANA_PREFIX}/dashboard/${KIBANA_ID} \
         -d @${file} || exit 1
    echo
done

# VISUALIZATIONS
for file in $TOP_LEVEL_DIR/$VISUALIZATIONS/*.json
do
    FILENAME=${file##*/}
    KIBANA_ID=${FILENAME%.*}
    echo "Loading visualization $FILENAME:"
    echo "  KIBANA_ID is  $KIBANA_ID:"
    curl -XPOST ${KIBANA_PREFIX}/visualization/${KIBANA_ID} \
         -d @${file} || exit 1
    echo
done

# SEARCHES
for file in $TOP_LEVEL_DIR/$SEARCHES/*.json
do
    FILENAME=${file##*/}
    KIBANA_ID=${FILENAME%.*}
    echo "Loading search $FILENAME:"
    echo "  KIBANA_ID is  $KIBANA_ID:"
    curl -XPOST ${KIBANA_PREFIX}/${KIBANA_INDEX}/search/${KIBANA_ID} \
        -d @${file} || exit 1
    echo
done