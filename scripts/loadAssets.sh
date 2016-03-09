#! /bin/sh

KIBANA_LOG_FILE="/var/log/probe/KibanaStartup.log"
KIBANA_PREFIX="localhost:9200/.kibana"
VER="4.1.4"

TOP_LEVEL_DIR="/usr/local/kibana-$VER-linux-x64"
DASHBOARDS="dashboards"
VISUALIZATIONS="visualizations"
SEARCHES="searches"
PRETTY="?pretty"

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
    echo `date +'%D %T'` "Creating $FILENAME dashboard record at $KIBANA_PREFIX/dashboard/$KIBANA_ID"         >> $KIBANA_LOG_FILE 
    curl -XPOST ${KIBANA_PREFIX}/dashboard/${KIBANA_ID} \
         -d @${file} || exit 1                                                                >> $KIBANA_LOG_FILE
done

# VISUALIZATIONS
for file in $TOP_LEVEL_DIR/$VISUALIZATIONS/*.json
do
    FILENAME=${file##*/}
    KIBANA_ID=${FILENAME%.*}
    echo `date +'%D %T'` "Creating $FILENAME visualization record at $KIBANA_PREFIX/visualization/$KIBANA_ID" >> $KIBANA_LOG_FILE
    curl -XPOST ${KIBANA_PREFIX}/visualization/${KIBANA_ID} \
         -d @${file} || exit 1                                                                >> $KIBANA_LOG_FILE
done

# SEARCHES
for file in $TOP_LEVEL_DIR/$SEARCHES/*.json
do
    FILENAME=${file##*/}
    KIBANA_ID=${FILENAME%.*}
    echo `date +'%D %T'` "Creating $FILENAME search record at $KIBANA_PREFIX/search/$KIBANA_ID"               >> $KIBANA_LOG_FILE
    curl -XPOST ${KIBANA_PREFIX}/${KIBANA_INDEX}/search/${KIBANA_ID} \
        -d @${file} || exit 1                                                                 >> $KIBANA_LOG_FILE
done
