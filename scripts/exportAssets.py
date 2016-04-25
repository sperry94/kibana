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

def print_to_file(content, filename=OUTPUT_FILE):
   with open(filename, 'w') as outputfile:
      json.dump(content, outputfile, indent=esUtil.INDENT_LEVEL)

def strip_metadata(json_str):
   ob = json.loads(json.dumps(json_str))
   print "---- \n " + pretty_format(esUtil.safe_list_read(ob, '_source'))
   return esUtil.safe_list_read(ob, '_source')


# ----------------- MAIN -----------------
def main(argv):

   argParser = argparse.ArgumentParser(description="Export dashboards, visualizations, or searches from Elasticsearch")
   argParser.add_argument("-d", "--dashboard", dest="dash_name", metavar="DASHBOARD_NAME", help="Export dashboard and all of its assets")
   argParser.add_argument("-v", "--visualization", dest="viz_name", metavar="VIZUALIZATION_NAME", help="Export a single visualization")
   argParser.add_argument("-s", "--search", dest="search_name", metavar="SEARCH_NAME", help="Export a single search")
   argParser.add_argument("-o", "--outputdir", dest="directory", metavar="DIR_NAME", help="Specify an output directory for the exported file")

   
   args = argParser.parse_args()


   santize_input_args(argParser, args)

   if args.dash_name:
      print "dashboard name = " + args.dash_name
      TYPE = "dashboard"
      ID = args.dash_name
   elif args.viz_name:
      print "visualization name = " + args.viz_name
      TYPE = "visualization"
      ID = args.viz_name
   elif args.search_name:
      print "search name = " + args.search_name
      TYPE = "search"
      ID = args.search_name

   if args.directory:
      OUTPUT_DIR = args.directory

   print "path = " + OUTPUT_DIR


   success, ret = get_asset(INDEX, TYPE, ID)
   if success:
      print "SUCCESS\n"
      print pretty_format(ret)
      to_file = strip_metadata(ret)
      print_to_file(to_file)
   else:
      print "ERROR:   Did not find any " + TYPE + " named " + ID + " in Elasticsearch."
      sys.exit(2)

   # for arg in vars(args):
   #    print "arg: " + str(arg) + "    val: " + str(getattr(args, arg))



if __name__ == '__main__':
    main(sys.argv[1:])