#!/usr/bin/python
import os
import sys
import argparse
import json
from util import ElasticsearchUtil
from util import Logger

EXPORT_LOG = "/tmp/ExportAssets.log"

esUtil = ElasticsearchUtil(EXPORT_LOG)
logger = Logger(EXPORT_LOG)
logging, rotating_handler = logger.configure_and_return_logging()

OUTPUT_DIR = os.path.dirname(os.path.realpath(__file__)) 
OUTPUT_FILE = "export.json"

INDEX = esUtil.KIBANA_INDEX
TYPE = None
ID = None

DASHBOARD = "dashboard"
VISUALIZATION = "visualization"
SEARCH = "search"

TO_FILE = {}

def make_json(content):
   return json.loads(json.dumps(content))

def pretty_format(raw_json_content):
   json_obj = json.loads(json.dumps(raw_json_content))
   return json.dumps(json_obj, indent = esUtil.INDENT_LEVEL)


def get_asset(es_index, es_type, es_id):
   ignored, doc_exists = esUtil.function_with_timeout(esUtil.ES_QUERY_TIMEOUT,
                                           esUtil.document_exists,
                                             es_index,
                                             es_type,
                                             es_id)
   if doc_exists:
      success, ret = esUtil.get_document(es_index, es_type, es_id)
      logging.info("GET RETURNS: " + "\n" + pretty_format(ret))
      return True, ret
   else:
      logging.info("No such thing as " + es_id + " in /" + es_index + "/" + es_type + "/")
      return False, "Not found"

def print_error_and_usage(argParser, error):
   print "Error:  " + error + "\n"
   print argParser.print_help()
   sys.exit(2)

def santize_input_args(argParser, args):
   if len(sys.argv) == 1:
      print_error_and_usage(argParser, "No arguments supplied.")
   if (args.dash_name is None
      and args.viz_name is None
      and args.search_name is None):
      print_error_and_usage(argParser, "Must have one of the following flags: -d -v -s")

def get_filename(id):
   return id + ".json"

def get_full_path(asset_id):
   global OUTPUT_DIR
   return OUTPUT_DIR + "/" + get_filename(asset_id)

def print_to_file(content, filename=OUTPUT_FILE):
   with open(filename, 'w') as outputfile:
      json.dump(content, outputfile, indent=esUtil.INDENT_LEVEL)

def strip_metadata(json_str):
   ob = json.loads(json.dumps(json_str))
   return esUtil.safe_list_read(ob, '_source')

def remove_all_char(str, char):
   return str.replace(char, "")

def get_dashboard_panels(panels_str):
   panels_with_type = {}
   db_panels_json = json.loads(remove_all_char(panels_str, "\\"))
   for index, panel in enumerate(db_panels_json):
      
      panel_id = esUtil.safe_list_read(db_panels_json[index], 'id')
      print panel_id
      panel_type = esUtil.safe_list_read(db_panels_json[index], 'type')
      print "  " + panel_type
      panels_with_type[panel_id] = panel_type
   return panels_with_type

def export_all_files():
   global OUTPUT_DIR
   global TO_FILE
   for asset_name, asset_content in TO_FILE.iteritems():
      print_to_file(asset_content, asset_name)

def get_all_dashboard_content_from_ES(db_raw):
   global TO_FILE
   global INDEX
   db_json = make_json(db_raw)
   db_panels_raw = esUtil.safe_list_read(db_json, 'panelsJSON')
   print "DB_PANELS_RAW:"
   print db_panels_raw
   panels_with_type = get_dashboard_panels(db_panels_raw)
   for panel_id, panel_type in panels_with_type.iteritems():
      success, ret = get_asset(INDEX, panel_type, panel_id)
      if success:
         TO_FILE[get_full_path(panel_id)] = strip_metadata(ret)
      else:
         print "ERROR: Failed to get asset " + panel_id + " needed by dashboard."


# ----------------- MAIN -----------------
def main(argv):

   argParser = argparse.ArgumentParser(description="Export dashboards, visualizations, or searches from Elasticsearch")
   argParser.add_argument("-d", "--dashboard", dest="dash_name", metavar="DASHBOARD_NAME", help="Export dashboard and all of its assets")
   argParser.add_argument("-v", "--visualization", dest="viz_name", metavar="VIZUALIZATION_NAME", help="Export a single visualization")
   argParser.add_argument("-s", "--search", dest="search_name", metavar="SEARCH_NAME", help="Export a single search")
   argParser.add_argument("-o", "--outputdir", dest="directory", metavar="DIR_NAME", help="Specify an output directory for the exported file")
   
   args = argParser.parse_args()

   santize_input_args(argParser, args)
   
   global OUTPUT_DIR
   global TO_FILE
   global TYPE
   global ID

   if args.dash_name:
      TYPE = DASHBOARD
      ID = args.dash_name
   elif args.viz_name:
      TYPE = VISUALIZATION
      ID = args.viz_name
   elif args.search_name:
      TYPE = SEARCH
      ID = args.search_name

   if args.directory:
      OUTPUT_DIR = args.directory



   success, ret = get_asset(INDEX, TYPE, ID)



   if success:
      asset_raw = strip_metadata(ret)
      full_file_path = OUTPUT_DIR + "/" + get_filename(ID)
      TO_FILE[full_file_path] = asset_raw
      if TYPE == DASHBOARD:
         get_all_dashboard_content_from_ES(asset_raw)
      export_all_files()
   else:
      print "ERROR:   Did not find any " + TYPE + " named " + ID + " in Elasticsearch."
      sys.exit(2)


if __name__ == '__main__':
    main(sys.argv[1:])