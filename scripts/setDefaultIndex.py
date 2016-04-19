# File: setDefaultIndex.py
#
# Author: Craig Cogdill

import logging
import logging.handlers
import json
import time
from elasticsearch import Elasticsearch
log_filename = "/var/log/probe/KibanaStartup.log"
es_request_timeout = 30
es_query_timeout = 10
logging.basicConfig(filename=log_filename,
                    level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d %(levelname)s:  %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')
rotating_handler = logging.handlers.RotatingFileHandler(log_filename, 
                                                        maxBytes=10485760,
                                                        backupCount=5)
es = Elasticsearch(max_retries=50, retry_on_timeout=True)
localhost="localhost:9200"
nm_index_pattern='[network_]YYYY_MM_DD'
default_index='"defaultIndex": \"%s\"' % nm_index_pattern
indent_level = 3
kibana_index = ".kibana"
index_pattern_type = "index-pattern"
config_type = "config"
kibana_version = "4.1.4"
created=True
verified = 1

index_pattern_content = {
    "title": "[network_]YYYY_MM_DD",
    "timeInverval": "days",
    "defaultTimeField": "TimeUpdated"
}

version_config_content = {
    "defaultIndex": "[network_]YYYY_MM_DD"
}

def safe_list_read(l, idx):
    try:
        value = l[idx]
        return value
    except:
        logging.warning("No element in list for index: " + idx)
        return "" 

def format_for_update(content):
    return "{ \"doc\": " + str(json.dumps(content)) + " }"

def update_document(es_index, es_type, es_id, content):
    return json.dumps(es.update(index=es_index, doc_type=es_type, id=es_id, body=content, request_timeout=es_request_timeout))

def copy_dict_keys(dict):
  return dict.fromkeys(dict.keys(), 0)

def time_has_run_out(start, curr, max):
  logging.warning("START TIME = " + str(start))
  logging.warning("CURR TIME = " + str(curr))
  logging.warning(str(curr) + " - " + str(start) + " > " + str(max) + " == " + str(curr-start>max))
  return curr - start > max

def all_keys_verified(dict):
  logging.info("  Verifying keys...")
  all_verified = True
  for key in dict:
    logging.info("  Verifying key: " + key + "   --> " + str(dict[key]))
    all_verified = all_verified and dict[key]
  logging.info("  all_verified is ...." + str(all_verified))
  return all_verified

def search_index_and_type(es_index, es_type, query):
    search_response_raw = json.dumps(es.search(index=es_index,
                                               doc_type=es_type,
                                               q=query,
                                               request_timeout=es_request_timeout),
                                     indent=indent_level)
    search_response_json = json.loads(search_response_raw)
    hits_json = safe_list_read(search_response_json, 'hits')
    search_number_of_hits = safe_list_read(hits_json, 'total')
    return search_number_of_hits

def add_missing_elements_to_dict(to_verify, original_content):
    missing_elements = {}
    for key in to_verify:
        if to_verify[key] != verified:
            logging.debug("No hits for \"" + 
                          key +
                          "\":\"" +
                          original_content[key] +
                          "\". Adding to list of missing fields...")
            missing_elements[key] = original_content[key]
    return missing_elements


def verify_document_for_content(es_index, es_type, content):
    start_time = time.time()
    content_json = json.loads(json.dumps(content))
    to_verify = copy_dict_keys(content_json)
    # There is approximately a one second delay between
    #   when a document is inserted and when it can be
    #   retrieved. Rather than sleeping for a set amount
    #   of time and then checking for the document only
    #   once, we set a timeout period and query elasticsearch
    #   continuously until the document is retrieved.
    #
    #   If the timeout passes and no document has been
    #   retrieved, we will report that it is missing and
    #   try to reinsert it.
    while not all_keys_verified(to_verify) and not time_has_run_out(start_time, time.time(), es_query_timeout):
        for key in content_json.keys():
            if to_verify[key] != verified:
                query = key + ':' + '"'+ content_json[key] + '"'
                hits = search_index_and_type(es_index, es_type, query)
                if hits > 0:    
                    to_verify[key] = verified
                    logging.debug(str(hits) + " hit(s) for " + str(query) + ".")
        time.sleep(0.2) # 200ms
    return add_missing_elements_to_dict(to_verify, content_json)

def create_document(es_index, es_type, es_id, es_body):
    return json.dumps(es.create(index=es_index,
                                doc_type=es_type,
                                id=es_id,
                                body=es_body,
                                request_timeout=es_request_timeout),
                      indent=indent_level)

def create_document_if_it_doesnt_exist(es_index, es_type, es_id, es_body):
    document_exists = es.exists(index=es_index, doc_type=es_type, id=es_id, request_timeout=es_request_timeout)
    if not document_exists:
        logging.info('Document %s/%s/%s/%s does not exist. Creating it now...', localhost, es_index, es_type, es_id)
        document_created = create_document(es_index, es_type, es_id, es_body)
        logging.info("Create document returns: \n %s", document_created)
        return created
    else:
        logging.info("Document %s/%s/%s/%s already exists.", localhost, es_index, es_type, es_id)
        return not created


def sleep_if_necessary(need_to_sleep):
    if need_to_sleep:
        time.sleep(1)

# ----------------- MAIN -----------------
def main():
    logging.debug("================================== INDEX PATTERN ==================================")
    index_pattern_doc_created = create_document_if_it_doesnt_exist(kibana_index,
                                                                   index_pattern_type,
                                                                   nm_index_pattern,
                                                                   index_pattern_content)
    index_pattern_missing_fields = verify_document_for_content(kibana_index,
                                                               index_pattern_type,
                                                               index_pattern_content)
    if len(index_pattern_missing_fields) > 0:
        logging.info("Updating Network Monitor index-pattern with missing fields: ")
        for key in index_pattern_missing_fields:
            logging.info("      " + key + ":    " + config_missing_fields[key])
        update_document(kibana_index,
                        index_pattern_type,
                        nm_index_pattern,
                        format_for_update(index_pattern_missing_fields))
    else:
        logging.info("No missing index-pattern fields.")

    logging.debug("================================== " + kibana_version + " CONFIG ==================================")
    config_doc_created = create_document_if_it_doesnt_exist(kibana_index,
                                                            config_type,
                                                            kibana_version,
                                                            version_config_content)
    config_missing_fields = verify_document_for_content(kibana_index,
                                                        config_type,
                                                        version_config_content)
    if len(config_missing_fields) > 0:
        logging.info("Updating " + kibana_version + " config with missing fields:   ")
        for key in config_missing_fields:
            logging.info("      " + key + ":    " + config_missing_fields[key])
        update_document(kibana_index,
                        index_pattern_type,
                        nm_index_pattern,
                        format_for_update(config_missing_fields))
    else:
        logging.info("No missing " + kibana_version + " config fields.")


if __name__ == '__main__':
    main()