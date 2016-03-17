#! /bin/sh

KIBANA_LOG_FILE="/var/log/probe/KibanaStartup.log"
KIBANA_PREFIX="localhost:9200/.kibana"
VER="4.1.4"

RESOURCES="resources"
TOP_LEVEL_DIR="/usr/local/kibana-$VER-linux-x64/$RESOURCES"
DASHBOARDS="dashboards"
VISUALIZATIONS="visualizations"
SEARCHES="searches"
PRETTY="?pretty"
NOT_FOUND="404"
SILENT="-q"
# Directories directly under the kibana/resources folder include:
#   dashboards
#   visualizations
#   searches

# DASHBOARDS
curl -i -XHEAD "$KIBANA_PREFIX"/dashboard | grep "$SILENT" "$NOT_FOUND"
dashboards_set=$?
if [ $dashboards_set == 0 ]; then
    echo `date +'%D %T'` "  INSERTING DASHBOARDS INTO ELASTICSEARCH"                                                >> $KIBANA_LOG_FILE
    for file in $TOP_LEVEL_DIR/$DASHBOARDS/*.json
    do
        FILENAME=${file##*/}
        KIBANA_ID=${FILENAME%.*}
        echo `date +'%D %T'` "  Creating $FILENAME dashboard record at $KIBANA_PREFIX/dashboard/$KIBANA_ID"         >> $KIBANA_LOG_FILE 
        curl -XPOST ${KIBANA_PREFIX}/dashboard/${KIBANA_ID} \
             -d @${file} || exit 1                                                                                  >> $KIBANA_LOG_FILE
    done
else
    echo `date +'%D %T'` "  Dashboards have already been inserted"                                                  >> $KIBANA_LOG_FILE
fi

# VISUALIZATIONS
curl -i -XHEAD "$KIBANA_PREFIX"/visualization | grep "$SILENT" "$NOT_FOUND"
visualizations_set=$?
if [ $visualizations_set == 0 ]; then
    echo `date +'%D %T'` "  INSERTING VISUALIZATIONS INTO ELASTICSEARCH"                                            >> $KIBANA_LOG_FILE
    for file in $TOP_LEVEL_DIR/$VISUALIZATIONS/*.json
    do
        FILENAME=${file##*/}
        KIBANA_ID=${FILENAME%.*}
        echo `date +'%D %T'` "  Creating $FILENAME visualization record at $KIBANA_PREFIX/visualization/$KIBANA_ID" >> $KIBANA_LOG_FILE
        curl -XPOST ${KIBANA_PREFIX}/visualization/${KIBANA_ID} \
             -d @${file} || exit 1                                                                                  >> $KIBANA_LOG_FILE
    done
else
    echo `date +'%D %T'` "  Visualizations have already been inserted"                                              >> $KIBANA_LOG_FILE
fi

# SEARCHES
curl -i -XHEAD "$KIBANA_PREFIX"/search | grep "$SILENT" "$NOT_FOUND"
searches_set=$?
if [ $searches_set == 0 ]; then
    echo `date +'%D %T'` "  INSERTING SEARCHES INTO ELASTICSEARCH"                                                  >> $KIBANA_LOG_FILE
    for file in $TOP_LEVEL_DIR/$SEARCHES/*.json
    do
        FILENAME=${file##*/}
        KIBANA_ID=${FILENAME%.*}
        echo `date +'%D %T'` "  Creating $FILENAME search record at $KIBANA_PREFIX/search/$KIBANA_ID"               >> $KIBANA_LOG_FILE
        curl -XPOST ${KIBANA_PREFIX}/${KIBANA_INDEX}/search/${KIBANA_ID} \
            -d @${file} || exit 1                                                                                   >> $KIBANA_LOG_FILE
    done
else
    echo `date +'%D %T'` "  Searches have already been inserted"                                                    >> $KIBANA_LOG_FILE
fi