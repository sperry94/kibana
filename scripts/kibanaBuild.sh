#!/usr/bin/env bash

set -e
set -x

# This script is called by kibana.spec to build kibana using 
# using the pre-packaged files below, and update the .tar.gz 
# in the target directory

# Extract node_modules
rm -rf node_modules
tar xvzf node_modules.tgz

# Extract kibana bower_components
rm -rf src/kibana/bower_components
tar xvzf bower_components.tgz

# Extract nvm and node
rm -rf nvm
tar xvzf nvm.tgz
export NVM_DIR=$PWD/nvm

# Execute the nvm.sh script that was just unpackaged. 
# It switches the installed version of node to v0.10.42 
# to build kibana.
source nvm/nvm.sh

# Run the grunt build
rm -f target/*
nvm/v0.10.42/bin/node node_modules/grunt-cli/bin/grunt build

echo "***** SUCCESS ****"
ls -alh target/
