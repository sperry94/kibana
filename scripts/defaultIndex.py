# File: defaultIndex.py
#
# Author: Craig Cogdill

import logging
import json
import time
from elasticsearch import Elasticsearch
logging.basicConfig(filename="/var/log/probe/pythonKibanaStartup.log",
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s:  %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')
es = Elasticsearch()
localhost="localhost:9200"
nm_index_pattern='"[network_]YYYY_MM_DD"'
default_index='"defaultIndex": %s' % nm_index_pattern
indent_level = 3
kibana_index = ".kibana"
index_pattern_type = "index-pattern"
config_type = "config"
kibana_version = "4.1.4"

index_pattern_content = {
    "title": "[network_]YYYY_MM_DD",
    "timeInverval": "days",
    "defaultTimeField": "TimeUpdated"
}

version_config_content = {
    "defaultIndex": "[network_]YYYY_MM_DD"
}

def formatForUpdate(content):
    return "{ \"doc\": " + str(json.dumps(content)) + " }"

def updateDocument(es_index, es_type, es_id, content):
    return json.dumps(es.update(index=es_index, doc_type=es_type, id=es_id, body=content))

def searchIndexAndType(es_index, es_type, query):
    search_response_raw = json.dumps(es.search(index=es_index,
                                               doc_type=es_type,
                                               q=query),
                                     indent=indent_level)
    search_response_json = json.loads(search_response_raw)
    search_number_of_hits = search_response_json['hits']['total']
    return search_number_of_hits

def verifyDocumentForContent(es_index, es_type, content):
    content_json = json.loads(json.dumps(content))
    for key in content_json.keys():
        query = key + ':' + '"'+ content_json[key] + '"'
        hits = searchIndexAndType(es_index, es_type, query)
        if (hits > 0):
            logging.info(str(hits) + " hit(s) for " + str(query) + ".")
        else:
            logging.info("No hits for " + str(query) + ". Attempting to update index...")

def createDocument(es_index, es_type, es_id, es_body):
    return json.dumps(es.create(index=es_index,
                                doc_type=es_type,
                                id=es_id,
                                body=es_body),
                      indent=indent_level)

def createDocumentIfItDoesntExist(es_index, es_type, es_id, es_body):
    document_exists = es.exists(index=es_index, doc_type=es_type, id=es_id)
    if (not document_exists):
        logging.info('Document %s/%s/%s/%s does not exist. Creating it now...', localhost, es_index, es_type, es_id)
        create_document = createDocument(es_index, es_type, es_id, es_body)
        logging.info("Create document returns: \n %s", create_document)
    else:
        logging.info("Document %s/%s/%s/%s already exists.", localhost, es_index, es_type, es_id)




# ----------------- MAIN -----------------

updateDocument(kibana_index, config_type, kibana_version, formatForUpdate(version_config_content))

# createDocumentIfItDoesntExist(kibana_index, index_pattern_type, nm_index_pattern, index_pattern_content)
# time.sleep(1.0)
# verifyDocumentForContent(kibana_index, index_pattern_type, index_pattern_content)

# createDocumentIfItDoesntExist(kibana_index, config_type, kibana_version, version_config_content)
# time.sleep(1.0)
# verifyDocumentForContent(kibana_index, config_type, version_config_content)


