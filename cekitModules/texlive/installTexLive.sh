#!/bin/sh

# This shell script installs the TeXLive typesetting tools

echo "----------------------------------------------------------------------"
echo $0
echo "----------------------------------------------------------------------"
echo ""

set -eux

ls /tmp/artifacts

cd

tar xvf /tmp/artifacts/texLive.tar.gz

cd /

tar xvf /tmp/artifacts/chef-texlive-plugins.tar
