#!/usr/bin/python


# Elasticsearch global params
INDENT_LEVEL = 3
ES_REQUEST_TIMEOUT = 20
ES_QUERY_TIMEOUT = 20
STARTUP_TIMEOUT = 300 # 5 minutes
LOCALHOST="localhost:9200"
KIBANA_INDEX = ".kibana"
INDEX_PATTERN_TYPE = "index-pattern"
CONFIG_TYPE = "config"
KIBANA_VERSION = "4.1.4"


import json
import time
import elasticsearch
es = elasticsearch.Elasticsearch(max_retries=1, timeout=ES_REQUEST_TIMEOUT)


class Logger:
  # Python Logging Info
  MAIN_LOG_FORMAT_STR='%(asctime)s.%(msecs)03d %(levelname)s:  %(message)s'
  MAIN_LOG_DATEFMT_STR='%Y/%m/%d %H:%M:%S'
  MAIN_LOG_PATH_DEFAULT='/var/log/probe/KibanaStartup.log'
  DEFAULT_LOGGING_LEVEL=10 # logging.DEBUG
  DEFAULT_LOG_ROTATE_BYTES=10485760
  DEFAULT_LOG_ROTATE_COUNT=5

  def __init__(self, log_file=MAIN_LOG_PATH_DEFAULT):
    self.MAIN_LOG_PATH_DEFAULT = log_file

  def configure_and_return_logging(self, datefmt_str=MAIN_LOG_DATEFMT_STR, format_str=MAIN_LOG_FORMAT_STR):
    import logging
    import logging.handlers
    logging.basicConfig(
        filename=self.MAIN_LOG_PATH_DEFAULT,
        level=self.DEFAULT_LOGGING_LEVEL,
        format=format_str,
        datefmt=datefmt_str)

    rotating_handler = logging.handlers.RotatingFileHandler(self.MAIN_LOG_PATH_DEFAULT, 
                                                            maxBytes=self.DEFAULT_LOG_ROTATE_BYTES,
                                                            backupCount=self.DEFAULT_LOG_ROTATE_COUNT)

    return logging, rotating_handler












class ElasticsearchUtil():

  LOG_FILE="/var/log/probe/KibanaStartup.log"
  ES_LOGGER = None
  logging = None
  rotating_handler = None

  def __init__(self, log_file=LOG_FILE):
    self.LOG_FILE = log_file
    self.ES_LOGGER = Logger(self.LOG_FILE) 
    self.logging, self.rotating_handler = self.ES_LOGGER.configure_and_return_logging()

  def safe_list_read(l, idx):
    try:
      value = l[idx]
      return value
    except:
      self.logging.warning("No element in list for index: " + idx)
      return "" 

      def time_has_run_out(start, curr, max):
        return curr - start > max

        def format_for_update(content):
          return "{ \"doc\": " + str(json.dumps(content)) + " }"

          def update_document(es_index, es_type, es_id, content):
            update_ret_raw = json.dumps(es.update(index=es_index,
              doc_type=es_type,
              id=es_id,
              body=content))
    # There is no true/false return value for an ES update
    return True, update_ret_raw

  def copy_dict_keys(dict):
    return dict.fromkeys(dict.keys(), 0)

  def search_index_and_type(es_index, es_type, query):
    search_response_raw = json.dumps(es.search(index=es_index,
     doc_type=es_type,
     q=query),
    indent=INDENT_LEVEL)
    search_response_json = json.loads(search_response_raw)
    hits_json = safe_list_read(search_response_json, 'hits')
    search_number_of_hits = safe_list_read(hits_json, 'total')
    return search_number_of_hits
  
  # Elasticsearch communication functions
  def create_document(es_index, es_type, es_id, es_body):
    es_create_ret = json.dumps(es.create(index=es_index,
      doc_type=es_type,
      id=es_id,
      body=es_body),
    indent=INDENT_LEVEL)
    es_create_ret_json = json.loads(es_create_ret)
    created = safe_list_read(es_create_ret_json, 'created')
    return created, es_create_ret

  def document_exists(es_index, es_type, es_id):
    exists_ret = es.exists(index=es_index, doc_type=es_type, id=es_id)
    # es.exists returns a true or false. 
    #   Always report that the function was successful,
    #   and leave the result in the second return value
    return True, exists_ret
   
  def delete_document(es_index, es_type, es_id):
    es_del_raw = es.delete(index=es_index, doc_type=es_type, id=es_id)
    es_del_json = json.loads(json.dumps(es_del_raw))
    if safe_list_read(es_del_json, 'found'):
      return True, es_del_raw
    else:
      return False, es_del_raw

  def get_document(es_index, es_type, es_id):
    es_get_raw = es.get(index=es_index, doc_type=es_type, id=es_id)
    es_get_json = json.loads(json.dumps(es_get_raw))
    if safe_list_read(es_get_json, 'found'):
      return True, es_get_raw
    else:
      return False, es_get_raw

  def read_json_from_file(filename):
    with open(filename) as file_raw:    
      return json.load(file_raw)

  def function_with_timeout(timeout, function, *args):
    keep_running = True
    start_time = time.time()
    itr = 1
    func_status = False
    func_ret = "Not yet run"
    while not time_has_run_out(start_time, time.time(), timeout) and keep_running:
      self.logging.info("try_with_timeout: Attempting run number " + str(itr) + " of function")
      try:
        func_status, func_ret = function(*args)
      except elasticsearch.TransportError as es1:
        self.logging.info("Caught elasticsearch TransportError exception: Status Code: " + str(es1.status_code) + ". Retrying...")
        if es1.status_code == 409:
          # 409 - DocumentAlreadyExistsException
          func_status = True
        else:
          func_status = False
      except:
        self.logging.info("Caught generic elasticsearch exception. Retrying...")
        func_status = False
      if func_status:
        keep_running = False
        return func_status, func_ret
      itr += 1
    return False, "Function timed out if it got this far"


  def get_request_as_json(es_index, es_type, es_id):
    found, raw = function_with_timeout(ES_REQUEST_TIMEOUT,
                                     get_document,
                                         es_index,
                                         es_type,
                                         es_id)
    return json.loads(json.dumps(raw))


