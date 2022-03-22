#!/bin/bash

# This bash shell script install the ConTeXt typesetting tools

# (We require BASH to be able to use pdm --pep582 below)

echo "----------------------------------------------------------------------"
echo $0
echo "----------------------------------------------------------------------"
echo ""

set -eux

ls /tmp/artifacts

cd

tar xvf /tmp/artifacts/context.tar.gz

cd /

tar xvf /tmp/artifacts/chef-context-plugins.tar
