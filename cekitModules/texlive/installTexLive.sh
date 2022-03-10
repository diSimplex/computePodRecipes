#!/bin/sh

# This shell script installs the TeXLive typesetting tools

echo "----------------------------------------------------------------------"
echo $0
echo "----------------------------------------------------------------------"
echo ""

set -eux

cd

mkdir TeXLive

cd TeXLive

wget https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz

tar zxvf install-tl-unx.tar.gz --strip-components=1

./install-tl --profile /tmp/artifacts/texlive.profile

cd /

ls /tmp/artifacts

tar xvf /tmp/artifacts/chef-texlive-plugins.tar

