#!/usr/bin/env bash

set -e
set -x

# This script will build kibana and update the .tar.gz file in the target directory
# please add this with your kibana pull request. The buildRpm and kibana.spec files
# will NOT build kibana from scratch, instead it will use that .tar.gz file to create
# the rpm

rm -rf ../kibana-build-target
mkdir -p ../kibana-build-target
cp -r . ../kibana-build-target/.
LOCATION=$PWD
cd ../kibana-build-target


sed -i s/\'shasum/\'sha1sum/g tasks/create_shasums.js
sed -i s/0.10.x/0.10.42/g .node-version
NVM_DIR="$PWD/nvm" bash scripts/kibanaSpecHelper_install_nvm.sh
source $PWD/nvm/nvm.sh
nvm install "$(cat .node-version)"
npm install
source nvm/nvm.sh
nvm/v0.10.42/bin/node node_modules/grunt-cli/bin/grunt build
cd $LOCATION
rm -f target/*
cp -r ../kibana-build-target/target/* target/.

echo "***** SUCCESS ****"
ls -alh target/

