# This shell script typesets a context document located at projectPath

if test $# -ne 3 ; then
  echo "usage: context.sh <documentName> <projectPath>"
  exit 1
fi

documentName=$1
projectPath=$2
rsyncProjectPath=$3

echo "-------------------------------------------------------------------"
echo $RSYNC_RSH
echo "-------------------------------------------------------------------"
echo rsync -av $rsyncProjectPath/ .
rsync -av $rsyncProjectPath/ .
echo "-------------------------------------------------------------------"

pwd

tree

echo "-------------------------------------------------------------------"
echo context $documentName
/root/ConTeXt/tex/texmf-linux-64/bin/context $documentName
echo "-------------------------------------------------------------------"

tree

echo "-------------------------------------------------------------------"
echo rsync -av . $rsyncProjectPath
rsync -av . $rsyncProjectPath
echo "-------------------------------------------------------------------"
