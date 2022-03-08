#!/bin/sh

# This shell script install the ConTeXt typesetting tools

echo "----------------------------------------------------------------------"
echo $0
echo "----------------------------------------------------------------------"
echo ""

set -eux

cd

mkdir ConTeXt

cd ConTeXt

wget http://lmtx.pragma-ade.nl/install-lmtx/context-linux-64.zip

unzip context-linux-64.zip

sh install.sh

cd /

ls /tmp/artifacts

tar xvf /tmp/artifacts/chef-context-plugins.tar

pip install pdm

pdm --pep582 >> /root/.bashrc

#. `pdm --pep582`
#
#cd /root/cpChef
#
#pdm install
#
#./scripts/installEditableCpchefCommand
