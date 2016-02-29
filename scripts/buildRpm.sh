#!/bin/bash
set -e
PACKAGE=kibana
GIT_VERSION=`git rev-list --branches HEAD | wc -l`
GIT_BRANCH=`git rev-parse --abbrev-ref HEAD`
VERSION="$GIT_BRANCH.$GIT_VERSION"

PWD=`pwd`

rm -rf ~/rpmbuild
rpmdev-setuptree
cp packaging/$PACKAGE.spec ~/rpmbuild/SPECS
rm -f $PACKAGE-$VERSION.tar.gz
tar cvzf ~/rpmbuild/SOURCES/$PACKAGE-$VERSION.tar.gz -C $PWD .
rpmbuild -v -bb --define="version ${VERSION}" --define="kibana_version ${GIT_BRANCH}" --target=x86_64 ~/rpmbuild/SPECS/$PACKAGE.spec
