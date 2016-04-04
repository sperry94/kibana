# File: defaultIndex.py
#
# Author: Craig Cogdill
#
# Description: Uploads and applies an upgrade to the NetMon Application.
#              The API Key is used to provide access to the external API calls
#              which can be found at:
#                   _api/application/uploadFile.php
#                   _api/application/doUpgrade.php
#              The functionality is provided via a RESTful API, which is
#              reached via curl POST requests in the script here. The .lrp
#              file is first download from Jenkins, using curl calls to get
#              the file's details (Build Number / Version Number).
#              The upgrade is then applied to the system through doUpgrade.php
#              This script takes a long time for a number of reasons:
#                   1) The download of the .lrp
#                   2) The upload of the .lrp
#                   3) Restarting the system
#               Please be patient while these processes take place, and do
#               not cancel the process, although it may appear to be hung at
#               times.
#
# Note: All of the comments littered throughout the code is to be used when CentOS 7
#       is released. cURL is not supported in the current version of CentOS, so we
#       were forced to use wget to get the necessary functionality.
#

import logging
from elasticsearch import Elasticsearch
logging.basicConfig(filename="/var/log/probe/pythonKibanaStartup.log",
                    level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s:  %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S')
es = Elasticsearch()


def createDocumentIfItDoesntExist(es_index, es_type, es_id, es_body):
    document_exists = es.exists(index=es_index, doc_type=es_type, id=es_id)
    if (not document_exists):
        logging.info('Document %s/%s/%s does not exist. Creating it now...', es_index, es_type, es_id)
        create_document = es.create(index=es_index, doc_type=es_type, id=es_id, body=es_body)
    else:
        logging.info("Document %s/%s/%s already exists.", es_index, es_type, es_id)



index_pattern_content = {
    "title": "[network_]YYYY_MM_DD",
    "timeInverval": "days",
    "defaultTimeField": "TimeUpdated"
}

version_config_content = {
    "defaultIndex": "[network_]YYYY_MM_DD"
}


logging.info("TEST MESSAGE")


createDocumentIfItDoesntExist(".kibana", "index-pattern", "[network_]YYYY_MM_DD", index_pattern_content)
createDocumentIfItDoesntExist(".kibana", "config", "4.1.4", version_config_content)




# index_pattern_exists = es.exists(index=".kibana", doc_type="index-pattern", id="[network_]YYYY_MM_DD")
# if (not index_pattern_exists):
#     logging.info("The index-pattern doesn't exist!")
#     index_pattern_create = es.create(index=".kibana", doc_type="index-pattern", id="[network_]YYYY_MM_DD", body=index_pattern_content)

# else:
#     logging.info("The index-pattern does exist!")




# version_config_exists = es.exists(index=".kibana", doc_type="config", id="4.1.4")
# if (not version_config_exists):
#     logging.info("Config for 4.1.4 doesn't exist!")
#     version_config_content= {
#             "defaultIndex": "[network_]YYYY_MM_DD",
#         }
#     version_config_create = es.create(index=".kibana", doc_type="config", id="4.1.4", body=version_config_content)

# else:
#     logging.info("Previous config for version 4.1.4 exists.")


# import re
# import sys
# import json
# import shutil
# import getopt
# import datetime
# import subprocess
# sys.path.append(
#    os.path.abspath(os.path.join(os.path.dirname(__file__),os.path.pardir)))
# from util import check_if_wget_is_installed
# from util import rpm_remove
# from util import yum_install

# ### Globals ###
# _apiKey = None
# _logData = None
# _outputFile = None
# _outputDirectory = None
# _loginInfo = None
# _domain = None
# _upgradeFile = None
# _minimumUpgradeSize = 100000000

# def printUsage():
#     print "USAGE: In order to use this function, supply your API key and domain,"
#     print "in a config file. The upgrade file will be taken care of for you."
#     print "Format the config file with Key/Value pairs, as follows:"
#     print "\tAPI_Key: <apiKey>"
#     print "\tDomain: <domain>"
#     print "Your domain should be in the form of an IP address, or a localhost"
#     print "Also, you can:"
#     print "\tProvide an output directory for the logs to be placed (optional)"
#     print "\tProvide an upgrade file if you don't want the most recent (optional)"
#     print " -- Example -- "
#     print "python applyUpgrade.py -c <configFilePath> -o <outputDirectory> -u <upgradeFilePath>"
#     print " -------------"

# def parseArgumentsForOptions(argv):
#     options, args = getopt.getopt(argv, "hc:o:u:")
#     checkOptions(options)
#     return options

# def checkOptions(options):
#     if not bool(options):
#         exitCleanly()

# def displayError(error):
#     print "----------------------------------------------"
#     print str(error)
#     print "----------------------------------------------"
#     exitWithError()

# def parseOptions(options):
#     global _upgradeFile
#     outputDirectoryName = None
#     for opt, arg in options:
#         if opt == "-h":
#             exitCleanly()
#         elif opt == "-c":
#             setVariablesFromConfig(str(arg))
#         elif opt == "-u":
#             _upgradeFile = str(arg)
#         elif opt == "-o":
#             outputDirectoryName = str(arg)
#     initializeLog(outputDirectoryName)

# def setVariablesFromConfig(config):
#     verifyConfigFieldsExist(config)
#     populateConfigVariables(config)

# def verifyConfigFieldsExist(config):
#     configFile = open(config, "r").read()
#     fieldArray = ["API_Key:", "Domain:"]
#     for field in fieldArray:
#         if not re.search(field, configFile):
#             errorString = "ERROR: Config missing fields!"
#             errorString += "\n\tIn function: 'verifyConfigFieldsExist'"
#             raise ValueError(errorString)

# def populateConfigVariables(config):
#     global _loginInfo, _domain, _apiKey
#     configFile = open(config, "r")
#     apiRegex     = "API_Key: (\S+)"
#     domainRegex  = "Domain: (\S+)"

#     for line in configFile:
#         if re.search(apiRegex, line):
#             _apiKey = re.search(apiRegex, line).group(1)
#             _loginInfo = formatLoginInfo(str(_apiKey))
#         elif re.search(domainRegex, line):
#             _domain = re.search(domainRegex, line).group(1)

# def downloadLatestUpgrade():
#     versionNumber = getVersionNumber()
#     buildNumber = getBuildNumber()
#     getUpgradeFile(versionNumber, buildNumber)

# def getVersionNumber():
#     getVersionNumberArray = generateGetVersionNumberArray()
#     process = subprocess.Popen(getVersionNumberArray)
#     exitcode = process.wait()
#     if (exitcode == 0):
#         result = open("getVersionNumberOutput.json", "r+").read()
#         matchObject = re.search("upgrade-(\d\.\d\.\d|master)", result)
#         if (matchObject):
#             return matchObject.group(1)
#     errorString = "The version number from the last build could not be read"
#     errorString += "\n\tIn function: 'getVersionNumber'"
#     raise ValueError(errorString)

# def getBuildNumber():
#     getBuildNumberArray = generateGetBuildNumberArray()
#     process = subprocess.Popen(getBuildNumberArray)
#     exitcode = process.wait()
#     if (exitcode == 0):
#         result = open("getBuildNumberOutput.json", "r+").read()
#         return result
#     errorString = "Could not fetch build number!"
#     errorString += "\n\tIn function: 'getBuildNumber'"
#     raise ValueError(errorString)

# def getUpgradeFile(versionNumber, buildNumber):
#     getUpgradeFileArray = generateGetUpgradeFileArray(versionNumber, buildNumber)
#     process = subprocess.Popen(getUpgradeFileArray)
#     exitcode = process.wait()
#     if (exitcode == 0):
#         resultSize = os.path.getsize(_upgradeFile)
#         if (resultSize < _minimumUpgradeSize):
#             errorString = "Upgrade file was not downloaded, but process ran without error"
#             errorString += "\n\tIn function: 'getUpgradeFile'"
#             raise ValueError(errorString)
#     else:
#         errorString = "Upgrade file was not downloaded with bad exitcode"
#         errorString += "\n\tIn function: 'getUpgradeFile'"
#         raise ValueError(errorString)
#     #### TODO: CentOS 7 Code ####
#         # if re.search(...):
#             # return fileName
#     #return None
#     # getUpgradeFileArray = generateGetUpgradeFileArray(versionNumber, buildNumber)
#     # process = subprocess.Popen(getUpgradeFileArray, stdout=subprocess.PIPE)
#     # result = process.stdout.read()

# def generateGetBuildNumberArray():
#     url = "http://jenkins2:8080/view/NM-REV1/job/NM_REV1_MasterBuild/lastSuccessfulBuild/buildNumber"
#     return ["wget", url, "-O", "getBuildNumberOutput.json"]
#     #TODO: return ['curl', '-X', 'GET', url]

# def generateGetVersionNumberArray():
#     url = "http://jenkins2:8080/view/NM-REV1/job/NM_REV1_Package/lastSuccessfulBuild/artifact/rpms/"
#     return ["wget", url, "-O", "getVersionNumberOutput.json"]
#     #TODO: return ['curl', '-X', 'GET', url]

# def generateGetUpgradeFileArray(versionNumber, buildNumber):
#     global _upgradeFile
#     _upgradeFile = "upgrade-{0}.{1}.lrp".format(versionNumber, buildNumber)
#     url = "http://jenkins2:8080/view/NM-REV1/job/NM_REV1_Package/ws/rpms/{0}".format(_upgradeFile)
#     return ["wget", url]
#     #TODO: return ['curl', '-O', url]

# def applyUpgrade():
#     if argumentsAreSet(_domain, _loginInfo, _upgradeFile):
#         moveUpgradeFile(_upgradeFile)
#         return executeCurlDoUpgrade()
#         #### TODO: CentOS 7 Code ####
#         # uploadResult = executeCurlUploadUpgrade(domain, loginInfo, upgrade)
#         # if (uploadWasSuccessful(uploadResult, upgrade)):
#         #    upgradeResult = executeCurlDoUpgrade(domain, loginInfo, upgrade)
#     errorString = "ERROR: API Key, Domain, or Upgrade file is incorrect/missing!"
#     errorString += "\n\tIn function: 'applyUpgrade'"
#     raise ValueError(errorString)

# def moveUpgradeFile(upgrade):
#     source = upgrade
#     dest = "/home/probe/upgrade/" + upgrade
#     shutil.move(source, dest)

# def argumentsAreSet(domain, loginInfo, upgrade):
#     return (verifyDomain(domain) and verifyLoginInfo(loginInfo) and verifyUpgrade(upgrade))

# def verifyLoginInfo(loginInfo):
#     return re.search("\S+:.+", loginInfo)

# def verifyDomain(domain):
#     return domain != ""

# def verifyUpgrade(upgrade):
#     return re.search(".+\.lrp", upgrade)

# def formatLoginInfo(apiKey):
#     return "admin:" + apiKey

# def executeCurlDoUpgrade():
#     doUpgradeArray = generateUpgradeArray()
#     process = subprocess.Popen(doUpgradeArray)
#     process.wait()
#     result = open("applyUpgradeOutput.json", "r+").read()
#     return result

# def generateUpgradeArray():
#     url = "https://{0}/_api/application/doUpgrade.php?fileName={1}".format(_domain, _upgradeFile)
#     password = "--password={0}".format(_apiKey)
#     return ["wget", "--no-check-certificate", "--user=admin", password, url, "-O", "applyUpgradeOutput.json"]
#     # TODO: return ['curl', '-X', 'GET', '--insecure', '-L', '-u', loginInfo, url]


# #### TODO: CentOS 7 Code ####
# # def uploadWasSuccessful(uploadResult, upgrade):
# #     expectedResult = "'name':'{0}'".format(upgrade)
# #     result = re.search(expectedResult, uploadResult)
# #     return bool(result)

# # def generateUploadUpgradeArray(domain, loginInfo, upgrade):
# #     url = "https://{0}/_api/application/uploadFile.php".format(domain)
# #     upgradePath = formatUpgradePath(upgrade)
# #     return ['curl', '-X', 'POST', '--insecure', '-L', '-u', loginInfo, '-F', upgradePath, url]

# # def executeCurlUploadUpgrade(domain, loginInfo, upgrade):
# #     uploadUpgradeArray = generateUploadUpgradeArray(domain, loginInfo, upgrade)
# #     process = subprocess.check_output(uploadUpgradeArray)
# #     return process

# # def formatUpgradePath(upgradeFile):
# #     return "files=@{0}".format(upgrade)

# def initializeLog(outputDirectory):
#     global _logData, _outputFile, _outputDirectory
#     if not (outputDirectory):
#         outputDirectory = "applyUpgradeOutput"
#     currentDirectory = os.getcwd()
#     _outputDirectory = os.path.join(os.getcwd(), outputDirectory)
#     _outputFile = determineLogName()

#     if not os.path.exists(_outputDirectory):
#         os.makedirs(_outputDirectory)
#     os.chdir(_outputDirectory)
#     _logData = open(_outputFile, "w+")
#     os.chdir(currentDirectory)

# def determineLogName():
#     baseName = "applyUpgrade"
#     date = datetime.datetime.now()
#     dateString = "-{0}_{1}_{2}-{3}_{4}_{5}".format(
#         str(date.month),
#         str(date.day),
#         str(date.year),
#         str(date.hour),
#         str(date.minute),
#         str(date.second))
#     logName = baseName + dateString + ".log"
#     return logName

# def logResult(upgradeResult):
#     status = ""
#     if re.search("PASS", upgradeResult):
#         status = "PASS: Upgrade successfully uploaded and installed!"
#     else:
#         status = "FAIL: Could not perform upgrade with API!"
#     _logData.write(status)
#     return status

# # def wgetIsNotInstalled():
# #     proc = subprocess.Popen(["rpm", "-q", "wget"], stdout=subprocess.PIPE)
# #     exitcode = proc.wait()
# #     output = proc.stdout.read().strip().rstrip()
# #     if ("not installed" in output):
# #         return True

# #     if exitcode != 0:
# #         errorString = "ERROR: in checking to see if wget is installed."
# #         errorString += "\n\tIn function: 'wgetIsNotInstalled'"
# #         raise TypeError(errorString)
# #         sys.exit(exitcode)

# #     return False

# def printSummary(status):
#     print "----------------------------------------------"
#     print "Overall Run: " + status
#     print "----------------------------------------------"

# def exitWithError():
#     printUsage()
#     sys.exit(1)

# def exitCleanly():
#     printUsage()
#     sys.exit(0)

# # def raiseWgetError():
# #     errorString = "ERROR: wget must be installed to run this script."
# #     errorString += "\n\tInstall using 'sudo yum install wget'"
# #     raise ValueError(errorString)

# if __name__ == '__main__':
#     try:
#         # TODO: Remove wget check when CentOS 7 is available
#         wget_installed = check_if_wget_is_installed()
#         if not wget_installed:
#             yum_install('wget')
#         options = parseArgumentsForOptions(sys.argv[1:])
#         parseOptions(options)
#         if _upgradeFile == None:
#             downloadLatestUpgrade()
#         result = applyUpgrade()
#         status = logResult(result)
#         printSummary(status)
#     except (getopt.GetoptError, ValueError, TypeError, IOError) as error:
#         displayError(error)
#     finally:
#         if not wget_installed:
#             rpm_remove('wget')