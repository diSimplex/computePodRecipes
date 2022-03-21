#!/bin/sh

# This shell script installs the TeXLive typesetting tools

echo "----------------------------------------------------------------------"
echo $0
echo "----------------------------------------------------------------------"
echo ""

set -eux

cd

mkdir TeXLive

ls /tmp/artifacts

tar xvf /tmp/artifacts/texLive.tar.gz

tar xvf /tmp/artifacts/chef-texlive-plugins.tar

ls
