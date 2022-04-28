# This shell script typesets a context document located at projectPath

#if test $# -ne 3 ; then
#  echo "usage: context.sh <documentName> <projectPath>"
#  exit 1
#fi

#documentName=$1
#projectPath=$2
#rsyncProjectPath=$3

function verboseDo {
	if [ $CHEF_verbosity -gt "0" ]; then
	  $*
	fi
}

export RSYNC_RSH="ssh -i $CHEF_privateKeyPath -o UserKnownHostsFile=$CHEF_hostPublicKeyPath"
rsyncProjectPath=$CHEF_rsyncUserName@$CHEF_rsyncHostName:$CHEF_projectDir

if [ $CHEF_verbosity -gt "0" ]; then
  echo "-------------------------------------------------------------------"
  echo "             RSYNC_RSH $RSYNC_RSH"
  echo "       CHEF_workingDir $CHEF_workingDir"
  echo "       CHEF_projectDir $CHEF_projectDir"
  echo "           CHEF_srcDir $CHEF_srcDir"
  echo "        CHEF_outputDir $CHEF_outputDir"
  echo "     CHEF_documentName $CHEF_documentName"
  echo "CHEF_texmfContentsPath $CHEF_texmfContentsPath"
  echo "             TEXMFHOME $TEXMFHOME"
  echo "    CHEF_rsyncHostName $CHEF_rsyncHostName"
  echo "    CHEF_rsyncUserName $CHEF_rsyncUserName"
  echo "CHEF_hostPublicKeyPath $CHEF_hostPublicKeyPath"
  echo "   CHEF_privateKeyPath $CHEF_privateKeyPath"
  echo "        CHEF_verbosity $CHEF_verbosity"
  echo "            CHEF_clean $CHEF_clean"
  echo "-------------------------------------------------------------------"
fi

verboseDo echo mkdir -p $TEXMFHOME
mkdir -p $TEXMFHOME

if [ "$CHEF_clean" == "True" ]; then
  verboseDo echo Cleaning up working directory
  verboseDo echo rm -rf $CHEF_workingDir
  rm -rf $CHEF_workingDir
fi

verboseDo echo mkdir -p $CHEF_workingDir
mkdir -p $CHEF_workingDir

verboseDo echo cd $CHEF_workingDir
cd $CHEF_workingDir

echo rsync -Cav --delete $rsyncProjectPath/ .
rsync -Cav --delete $rsyncProjectPath/ .

verboseDo echo "-------------------------------------------------------------------"

verboseDo pwd

verboseDo tree

echo "-------------------------------------------------------------------"

baseDir=$PWD
documentPath=$baseDir/$CHEF_srcDir/$CHEF_documentName

verboseDo echo mkdir -p $CHEF_outputDir
mkdir -p $CHEF_outputDir

verboseDo echo cd $CHEF_outputDir
cd $CHEF_outputDir

verboseDo pwd

echo context $documentPath
/root/ConTeXt/tex/texmf-linux-64/bin/context $documentPath

echo "-------------------------------------------------------------------"

verboseDo echo cd $CHEF_workingDir
cd $CHEF_workingDir

verboseDo pwd

verboseDo tree

verboseDo echo "-------------------------------------------------------------------"

echo rsync -Cav ./$CHEF_outputDir $rsyncProjectPath
rsync -Cav ./$CHEF_output $rsyncProjectPath
