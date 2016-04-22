#!/usr/bin/python
import os
import sys
import argparse
from util import ElasticsearchUtil
from util import Logger

EXPORT_LOG = "/tmp/ExportAssets.log"

esUtil = ElasticsearchUtil(EXPORT_LOG)
logger = Logger(EXPORT_LOG)
logging, rotating_handler = logger.configure_and_return_logging()

OUTPUT_DIR = os.path.dirname(os.path.realpath(__file__)) 

# ----------------- MAIN -----------------
def main(argv):

   argParser = argparse.ArgumentParser(description="Export dashboards, visualizations, or searches from Elasticsearch")
   argParser.add_argument("-d", "--dashboard", dest="dash_name", metavar="DASHBOARD_NAME", help="Export dashboard and all of its assets")
   argParser.add_argument("-v", "--visualization", dest="viz_name", metavar="VIZUALIZATION_NAME", help="Export a single visualization")
   argParser.add_argument("-s", "--search", dest="search_name", metavar="SEARCH_NAME", help="Export a single search")
   argParser.add_argument("-o", "--outputdir", dest="directory", metavar="DIR_NAME", help="Specify an output directory for the exported file")

   if len(sys.argv) == 1:
      print "Error: No arguments supplied \n"
      print argParser.print_help()
      sys.exit(2)

   print "path = " + OUTPUT_DIR

   args = vars(argParser.parse_args())

   for arg in args:
      print "arg: " + str(arg) + "    val: " + str(args[arg])

   do_something()


if __name__ == '__main__':
    main(sys.argv[1:])