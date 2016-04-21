# File: setDefaultIndex.py
#
# Author: Craig Cogdill

import time
import json
from scripts import util
logging, rotating_handler = util.configure_and_return_logging()

ES_QUERY_TIMEOUT = 20

LOCALHOST="localhost:9200"
nm_index_pattern='[network_]YYYY_MM_DD'
default_index='"defaultIndex": \"%s\"' % nm_index_pattern
kibana_index = ".kibana"
index_pattern_type = "index-pattern"
config_type = "config"
kibana_version = "4.1.4"
CREATED=True
VERIFIED = 1

index_pattern_content = {
    "title": "[network_]YYYY_MM_DD",
    "timeInverval": "days",
    "defaultTimeField": "TimeUpdated"
}

version_config_content = {
    "defaultIndex": "[network_]YYYY_MM_DD"
}

def all_keys_verified(dict):
  #logging.info("  Verifying keys...")
  all_verified = True
  for key in dict:
    #logging.info("  Verifying key: " + key + "   --> " + str(dict[key]))
    all_verified = all_verified and dict[key]
  #logging.info("  all_verified is ...." + str(all_verified))
  return all_verified


def add_missing_elements_to_dict(to_verify, original_content):
    missing_elements = {}
    for key in to_verify:
        if to_verify[key] != VERIFIED:
            logging.debug("No hits for \"" + 
                          key +
                          "\":\"" +
                          original_content[key] +
                          "\". Adding to list of missing fields...")
            missing_elements[key] = original_content[key]
    return missing_elements


def verify_document_for_content(es_index, es_type, content):
    logging.info("Verifying content exists in Elasticsearch correctly. This could take several Elasticsearch requests.")
    start_time = time.time()
    content_json = json.loads(json.dumps(content))
    to_verify = util.copy_dict_keys(content_json)
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
    while not all_keys_verified(to_verify) and not util.time_has_run_out(start_time, time.time(), ES_QUERY_TIMEOUT):
        for key in content_json.keys():
            if to_verify[key] != VERIFIED:
                query = key + ':' + '"'+ content_json[key] + '"'
                hits = util.search_index_and_type(es_index, es_type, query)
                if hits > 0:    
                    to_verify[key] = VERIFIED
                    logging.info(str(hits) + " hit(s) for " + str(query) + ".")
        time.sleep(0.2) # 200ms
    return add_missing_elements_to_dict(to_verify, content_json)


def create_document_if_it_doesnt_exist(es_index, es_type, es_id, es_body):
    document_created = False
    ignored, doc_existence = util.function_with_timeout(10,
                                                        util.document_exists,
                                                            es_index,
                                                            es_type,
                                                            es_id)
    if not doc_existence:
        logging.info('Document %s/%s/%s/%s does not exist. Creating it now...', LOCALHOST, es_index, es_type, es_id)
        document_created, created_ret = util.function_with_timeout(util.STARTUP_TIMEOUT,
                                                                   util.create_document,
                                                                       es_index,
                                                                       es_type,
                                                                       es_id,
                                                                       es_body)
        logging.info("Create document returns: \n %s", created_ret)
        return document_created
    else:
        logging.info("Document %s/%s/%s/%s already exists.", LOCALHOST, es_index, es_type, es_id)
        return document_created


# ----------------- MAIN -----------------
def main():
    logging.info("================================== INDEX PATTERN ==================================")
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
        updated, update_ret = util.function_with_timeout(10,
                                                         util.update_document,
                                                            kibana_index,
                                                            index_pattern_type,
                                                            nm_index_pattern,
                                                            util.format_for_update(index_pattern_missing_fields))
        if not updated:
            logging.error("Unable to add missing index-pattern fields:")
            logging.error(update_ret)
    else:
        logging.info("No missing index-pattern fields.")

    logging.info("================================== " + kibana_version + " CONFIG ==================================")
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
        updated, update_ret = util.function_with_timeout(10,
                                                         util.update_document,
                                                            kibana_index,
                                                            index_pattern_type,
                                                            nm_index_pattern,
                                                            util.format_for_update(config_missing_fields))
        if not updated:
            logging.error("Unable to add missing index-pattern fields:")
            logging.error(update_ret)
    else:
        logging.info("No missing " + kibana_version + " config fields.")


if __name__ == '__main__':
    main()