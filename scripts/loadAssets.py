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

kibana_version = "4.1.4"

resources = "/usr/local/kibana-" + kibana_version + "-linux-x64/resources"
dashboards_path = resources + "/dashboards" 
visualizations_path = resources + "/visualizations" 
searches_path = resources + "/searches" 

dashboard_type = "dashboard"
visualization_type = "visualization"
search_type = "search"

kibana_index = ".kibana"
indent_level = 3

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

def get_request_as_json(es_index, es_type, es_id):
    return json.loads(json.dumps(es.get(index=es_index, doc_type=es_type, id=es_id)))


def load_assets(es_index, es_type, path_to_files, files):
    for file in files:
        logging.debug("--------- " + file + " ---------")
        full_file_path = path_to_files + "/" + file
        es_id = get_es_id(file)
        if (es.exists(index=es_index, doc_type=es_type, id=es_id)):
            get_response_json = get_request_as_json(es_index, es_type, es_id)
            version_of_disk_file = get_version_of_file(full_file_path)
            version_of_es_file = get_response_json['_source']['version']
            if (version_of_disk_file > version_of_es_file):
                logging.info("File \"" + str(file) + "\" is outdated and requires update from version " + str(version_of_es_file) +
                             " to version " + str(version_of_disk_file) + ". Updating it now...")
                update_existing_document(es_index, es_type, es_id, full_file_path)
            else:
                logging.info("Current version of file \"" + str(file) + "\" in Elasticsearch is up-to-date. Version: " + str(version_of_es_file))
        else:
            logging.info("File \"" + str(file) + "\" doesn't exist in Elasticsearch. Creating it now...")
            create_document_from_file(es_index, es_type, es_id, full_file_path)




# ----------------- MAIN -----------------

# Create arrays of the filenames in each of the resource dirs
dashboards = [file for file in listdir(dashboards_path) if isfile(join(dashboards_path, file))]
visualizations = [file for file in listdir(visualizations_path) if isfile(join(visualizations_path, file))]
searches = [file for file in listdir(searches_path) if isfile(join(searches_path, file))]

# Load all the artifacts appropriately
logging.debug("================================== DASHBOARDS ==================================")
load_assets(kibana_index, dashboard_type, dashboards_path, dashboards)
# logging.debug("================================== VISUALIZATIONS ==================================")
# load_assets(kibana_index, visualization_type, visualizations_path, visualizations)
# logging.debug("================================== SEARCHES ==================================")
# load_assets(kibana_index, search_type, searches_path, searches)
