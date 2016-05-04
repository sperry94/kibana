# File: setDefaultIndex.py
#
# Author: Craig Cogdill

import time
import json
from util import ElasticsearchUtil
from util import Utility
from util import Logger
esUtil = ElasticsearchUtil()
logger = Logger()
logging, rotating_handler = logger.configure_and_return_logging()
UTIL = Utility()

NM_INDEX_PATTERN='[network_]YYYY_MM_DD'
DEFAULT_INDEX='"defaultIndex": \"%s\"' % NM_INDEX_PATTERN
VERIFIED = 1

FIELD_FORMAT_MAPPINGS_FILE = "usr/local/kibana-" + esUtil.KIBANA_VERSION + "-linux-x64/resources/mappings.json"

index_pattern_content = {
    "title": "[network_]YYYY_MM_DD",
    "intervalName": "days",
    "timeFieldName": "TimeUpdated"
}

version_config_content = {
    "defaultIndex": "[network_]YYYY_MM_DD"
}

def all_keys_verified(dict):
  all_verified = True
  for key in dict:
    all_verified = all_verified and dict[key]
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

def flatten_dict(d):
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    yield key + "." + subkey, subvalue
            else:
                yield key, value

    return dict(items())

def verify_document_for_content(es_index, es_type, content):
    logging.info("Verifying content exists in Elasticsearch correctly. This could take several Elasticsearch requests.")
    start_time = time.time()
    flattened_content = flatten_dict(content)
    content_json = json.loads(json.dumps(flattened_content))
    to_verify = UTIL.copy_dict_keys(content_json)
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
    while not all_keys_verified(to_verify) and not UTIL.time_has_run_out(start_time, time.time(), esUtil.ES_QUERY_TIMEOUT):
        for key in content_json.keys():
            if to_verify[key] != VERIFIED:
                query = key + ':' + '"'+ str(content_json[key]) + '"'
                success, hits = esUtil.search_index_and_type(es_index, es_type, query)
                if hits > 0:    
                    to_verify[key] = VERIFIED
                    logging.info(str(hits) + " hit(s) for " + str(query) + ".")
        time.sleep(0.2) # 200ms
    return add_missing_elements_to_dict(to_verify, content_json)


def create_document_if_it_doesnt_exist(es_index, es_type, es_id, es_body):
    document_created = False
    ignored, doc_existence = esUtil.function_with_timeout(esUtil.ES_QUERY_TIMEOUT,
                                                          esUtil.document_exists,
                                                            es_index,
                                                            es_type,
                                                            es_id)
    if not doc_existence:
        logging.info('Document %s/%s/%s/%s does not exist. Creating it now...', esUtil.LOCALHOST, es_index, es_type, es_id)
        document_created, created_ret = esUtil.function_with_timeout(esUtil.STARTUP_TIMEOUT,
                                                                   esUtil.create_document,
                                                                       es_index,
                                                                       es_type,
                                                                       es_id,
                                                                       es_body)
        logging.info("Create document returns: \n %s", created_ret)
        return document_created
    else:
        logging.info("Document %s/%s/%s/%s already exists.", esUtil.LOCALHOST, es_index, es_type, es_id)
        return document_created

def get_field_mappings(filename):
    global index_pattern_content
    mappings_json = UTIL.read_json_from_file(filename)
    index_pattern_content.update(mappings_json)


# ----------------- MAIN -----------------
def main():

    # Add fieldFormatMap to index-pattern content
    get_field_mappings(filename=FIELD_FORMAT_MAPPINGS_FILE)

    logging.info("================================== INDEX PATTERN ==================================")
    index_pattern_doc_created = create_document_if_it_doesnt_exist(esUtil.KIBANA_INDEX,
                                                                   esUtil.INDEX_PATTERN_TYPE,
                                                                   NM_INDEX_PATTERN,
                                                                   index_pattern_content)
    index_pattern_missing_fields = verify_document_for_content(esUtil.KIBANA_INDEX,
                                                               esUtil.INDEX_PATTERN_TYPE,
                                                               index_pattern_content)
    if len(index_pattern_missing_fields) > 0:
        logging.info("Updating Network Monitor index-pattern with missing fields: ")
        for key in index_pattern_missing_fields:
            logging.info("      " + key + ":    " + index_pattern_missing_fields[key])
        updated, update_ret = esUtil.function_with_timeout(esUtil.ES_QUERY_TIMEOUT,
                                                         esUtil.update_document,
                                                            esUtil.KIBANA_INDEX,
                                                            esUtil.INDEX_PATTERN_TYPE,
                                                            NM_INDEX_PATTERN,
                                                            esUtil.format_for_update(index_pattern_missing_fields))
        if not updated:
            logging.error("Unable to add missing index-pattern fields:")
            logging.error(update_ret)
    else:
        logging.info("No missing index-pattern fields.")

    logging.info("================================== " + esUtil.KIBANA_VERSION + " CONFIG ==================================")
    config_doc_created = create_document_if_it_doesnt_exist(esUtil.KIBANA_INDEX,
                                                            esUtil.CONFIG_TYPE,
                                                            esUtil.KIBANA_VERSION,
                                                            version_config_content)
    config_missing_fields = verify_document_for_content(esUtil.KIBANA_INDEX,
                                                        esUtil.CONFIG_TYPE,
                                                        version_config_content)
    if len(config_missing_fields) > 0:
        logging.info("Updating " + esUtil.KIBANA_VERSION + " config with missing fields:   ")
        for key in config_missing_fields:
            logging.info("      " + key + ":    " + config_missing_fields[key])
        updated, update_ret = esUtil.function_with_timeout(esUtil.ES_QUERY_TIMEOUT,
                                                           esUtil.update_document,
                                                               esUtil.KIBANA_INDEX,
                                                               esUtil.CONFIG_TYPE,
                                                               esUtil.KIBANA_VERSION,
                                                               esUtil.format_for_update(config_missing_fields))
        if not updated:
            logging.error("Unable to add missing index-pattern fields:")
            logging.error(update_ret)
    else:
        logging.info("No missing " + esUtil.KIBANA_VERSION + " config fields.")


if __name__ == '__main__':
    main()