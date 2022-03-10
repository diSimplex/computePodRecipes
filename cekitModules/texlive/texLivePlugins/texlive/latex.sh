# This shell script typesets a latex2e document located at projectPath

if test $# -ne 3 ; then
  echo "usage: latex2e.sh <documentName> <projectPath>"
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
echo latex2e $documentName
/root/TexLive/tex/texmf-linux-64/bin/latex $documentName
echo "-------------------------------------------------------------------"

tree

echo "-------------------------------------------------------------------"
echo rsync -av . $rsyncProjectPath
rsync -av . $rsyncProjectPath
echo "-------------------------------------------------------------------"
