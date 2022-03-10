# This is LaTeX ComputePods Chef plugin

# It provides the Chef with recipes on how to typeset LaTeX2e documents....

import asyncio
import os
import signal
import yaml
from aiofiles.os import wrap

aioMakedirs = wrap(os.makedirs)
aioSystem   = wrap(os.system)

from cputils.debouncingTaskRunner import \
  NatsLogger, FileLogger, MultiLogger, DebouncingTaskRunner
from cpchef.utils import chefUtils
import cpchef.plugins

def registerPlugin(config, managers, natsClient) :
  print("Registering LaTeX plugin via registerPlugin")
  chefUtils()
  rsyncManager = managers['rsync']

  @natsClient.subscribe("build.from.latex.>")
  async def dealWithBuildRequest(subject, data) :
    scriptsDir = os.path.abspath(os.path.dirname(__file__))
    workingDir = os.path.join(os.getcwd(), 'tmpLaTeXDir')
    if 'workingDir' in config :
      workingDir = config['workingDir']
    #await aioSystem(f"rm -rf {workingDir}")
    await aioMakedirs(workingDir, exist_ok=True)
    projectDir = workingDir
    if 'projectDir' in data : projectDir = data['projectDir']
    #projectDir = os.path.abspath(os.path.expanduser(projectDir))
    taskName = "aTask"
    if 'taskName' in data : taskName = data['taskName']
    documentName = taskName
    if 'doc' in data : documentName = data['doc']
    rsyncHostName = None
    if 'rsyncHostName' in data : rsyncHostName = data['rsyncHostName']
    rsyncUserName = None
    if 'rsyncUserName' in data : rsyncUserName = data['rsyncUserName']
    rsyncProjectDir = projectDir
    if rsyncUserName is not None and rsyncHostName is not None :
      rsyncProjectDir = f"{rsyncUserName}@{rsyncHostName}:{projectDir}"
    hostPublicKeyPath = rsyncManager.getHostPublicKeyPath(rsyncHostName)
    privateKeyPath    = "/config/playGround-rsync-rsa"
    # check if hostPublicKey exists....
    if not os.path.exists(hostPublicKeyPath) :
      await natsClient.sendMessage(
        "build.result",
        {
          'result' : 'failed to build',
          'details' : [
            'rsync host has no public key'
          ]
        }
      )
      return

    taskDetails = {
      'cmd' : [
        '/bin/bash',
        os.path.join(scriptsDir, 'latex.sh'),
        documentName,
        projectDir,
        rsyncProjectDir
      ],
      'projectDir' : workingDir,
      'env'  : {
        #'RSYNC_RSH' : f"ssh -v -i {privateKeyPath} -o UserKnownHostsFile={hostPublicKeyPath}"
        'RSYNC_RSH' : f"ssh -i {privateKeyPath} -o UserKnownHostsFile={hostPublicKeyPath}"
      }
    }
    taskLog = FileLogger("stdout", 5)
    #taskLog = MultiLogger([
    #  FileLogger("stdout", 5),
    #  FileLogger("/tmp/test.log", 5),
    #  NatsLogger(natsClient, "logger", 5),
    #])
    await taskLog.open()

    await taskLog.write([
      "\n",
      "=========================================================\n",
      "Running LaTeX2e on:\n",
    ])
    await taskLog.write(yaml.dump(data))
    await taskLog.write("\n")

    workDone = asyncio.Event()

    def doneCallback() :
      print("DONE callback!")
      workDone.set()

    theTask = DebouncingTaskRunner(
      1, taskName, taskDetails, taskLog, signal.SIGHUP,
      doneCallback=doneCallback,
    )
    await theTask.reStart()
    await workDone.wait()
    await natsClient.sendMessage('done.'+subject[0], {
      'retCode' : theTask.getReturnCode()
    })
    print("ALL DONE!")

  print("Finished registering LaTeX Plugin")

async def registerArtefacts(config, natsClient) :
  await natsClient.sendMessage("artefact.register.type.pdfFile",{
    "name" : "pdfFile",
    "extensions" : [
      "*.pdf"
    ]
  })
