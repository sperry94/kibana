#!/bin/bash
set -e
set -x

if [[ $# -ne 1 ]] ; then
    echo 'Usage:  sh buildRpm <BRANCH> '
    exit 0
fi

PACKAGE=kibana
GIT_VERSION=`git rev-list --branches HEAD | wc -l`
GIT_BRANCH="$1"
VERSION="$GIT_BRANCH.$GIT_VERSION"

PWD=`pwd`

rm -rf ~/rpmbuild
rpmdev-setuptree
cp packaging/$PACKAGE.spec ~/rpmbuild/SPECS
rm -f $PACKAGE-$VERSION.tar.gz
tar cvzf ~/rpmbuild/SOURCES/$PACKAGE-$VERSION.tar.gz -C $PWD .
rpmbuild -v -bb --define="version ${VERSION}" --define="kibana_version ${GIT_BRANCH}" --target=x86_64 ~/rpmbuild/SPECS/$PACKAGE.spec
