# File: setDefaultIndex.py
#
# Author: Craig Cogdill

import logging
import json
import time
from elasticsearch import Elasticsearch
from os import listdir
from os.path import isfile, join, splitext
logging.basicConfig(filename="/var/log/probe/pythonKibanaStartup.log",
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s:  %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')
es = Elasticsearch()

resources = "/usr/local/kibana-4.1.4-linux-x64/resources"
dashboards_path = resources + "/dashboards" 
visualizations_path = resources + "/visualizations" 
searches_path = resources + "/searches" 
dashboards = [file for file in listdir(dashboards_path) if isfile(join(dashboards_path, file))]
visualizations = [file for file in listdir(visualizations_path) if isfile(join(visualizations_path, file))]
searches = [file for file in listdir(searches_path) if isfile(join(searches_path, file))]

dashboard_type = "dashboard"
visualization_type = "visualization"
search_type = "search"

def format_for_update(content):
    return "{ \"doc\": " + str(json.dumps(content)) + " }"

def update_document(es_index, es_type, es_id, content):
    return json.dumps(es.update(index=es_index, doc_type=es_type, id=es_id, body=content))

def create_document(es_index, es_type, es_id, es_body):
    return json.dumps(es.create(index=es_index,
                                doc_type=es_type,
                                id=es_id,
                                body=es_body),
                      indent=indent_level)

def create_document_from_file(es_index, es_type, es_id, path_to_updated_json):
    content = read_json_from_file(path_to_updated_json)
    create_document(es_index, es_type, es_id, content)

def get_es_id(filename):
    return splitext(filename)[0]

def delete_document(es_index, es_type, es_id):
    es.delete(es_index, es_type, es_id)

def read_json_from_file(file):
    with open(file) as file_raw:    
        return json.load(file_raw)

def get_version_of_file(file):
    return read_json_from_file(file)['version']

def update_existing_document(es_index, es_type, es_id, path_to_updated_json):
    delete_document(es_index, es_type, es_id)
    create_document_from_file(es_index, es_type, es_id, path_to_updated_json)

def load_assets(es_index, es_type, path_to_files, files):
    for file in files:
        full_file_path = path_to_files + "/" + file
        es_id = get_es_id(file)
        document_exists = es.exists(index=es_index, doc_type=es_type, id=es_id)
        if (document_exists):
            get_response_json = json.loads(json.dumps(es.get(index=es_index, doc_type=es_type, id=es_id)))
            if ( get_version_of_file(path_to_files + "/" + file) > get_response_json['_source']['version']):
                logging.info("Current version for file: " + file + " is higher than existing. Updating it...")
                update_existing_document(es_index, es_type, es_id, full_file_path)
            else:
                logging.info("Current version for file: " + file + " is NOT higher than existing")
        else:
            logging.info("Document doesn't exist in ES currently. Adding it now")
            create_document_from_file(es_index, es_type, es_id, full_file_path)




# ----------------- MAIN -----------------

logging.debug("================================== DASHBOARDS ==================================")
load_assets(kibana_index, dashboard_type, dashboards_path, dashboards)
logging.debug("================================== VISUALIZATIONS ==================================")
load_assets(kibana_index, dashboard_type, dashboards_path, dashboards)
logging.debug("================================== SEARCHES ==================================")
load_assets(kibana_index, dashboard_type, dashboards_path, dashboards)


