# This shell script typesets a context document located at projectPath

#if test $# -ne 3 ; then
#  echo "usage: context.sh <documentName> <projectPath>"
#  exit 1
#fi

#documentName=$1
#projectPath=$2
#rsyncProjectPath=$3

export RSYNC_RSH="ssh -i $CHEF_privateKeyPath -o UserKnownHostsFile=$CHEF_hostPublicKeyPath"
rsyncProjectPath=$CHEF_rsyncUserName@$CHEF_rsyncHostName:$CHEF_projectDir

echo "-------------------------------------------------------------------"
echo "             RSYNC_RSH $RSYNC_RSH"
echo "       CHEF_workingDir $CHEF_workingDir"
echo "       CHEF_projectDir $CHEF_projectDir"
echo "           CHEF_srcDir $CHEF_srcDir"
echo "     CHEF_documentName $CHEF_documentName"
echo "CHEF_texmfContentsPath $CHEF_texmfContentsPath"
echo "             TEXMFHOME $TEXMFHOME"
echo "    CHEF_rsyncHostName $CHEF_rsyncHostName"
echo "    CHEF_rsyncUserName $CHEF_rsyncUserName"
echo "CHEF_hostPublicKeyPath $CHEF_hostPublicKeyPath"
echo "   CHEF_privateKeyPath $CHEF_privateKeyPath"
echo "-------------------------------------------------------------------"


echo mkdir -p $TEXMFHOME
mkdir -p $TEXMFHOME

echo cd $TEXMFHOME
cd $TEXMFHOME

echo rsync -av --files-from=$CHEF_texmfContentsPath $CHEF_rsyncUserName@$CHEF_rsyncHostName:/ .
rsync -av --files-from=$CHEF_texmfContentsPath $CHEF_rsyncUserName@$CHEF_rsyncHostName:/ .

echo cd $CHEF_workingDir
cd $CHEF_workingDir

echo rsync -av $rsyncProjectPath/ .
rsync -av $rsyncProjectPath/ .
echo "-------------------------------------------------------------------"

pwd

tree

echo "-------------------------------------------------------------------"

echo cd $CHEF_srcDir
cd $CHEF_srcDir

pwd

echo context $CHEF_documentName
/root/ConTeXt/tex/texmf-linux-64/bin/context $CHEF_documentName
echo "-------------------------------------------------------------------"

echo cd $CHEF_workingDir
cd $CHEF_workingDir

pwd

tree

echo "-------------------------------------------------------------------"
echo rsync -av . $rsyncProjectPath
rsync -av . $rsyncProjectPath
echo "-------------------------------------------------------------------"
