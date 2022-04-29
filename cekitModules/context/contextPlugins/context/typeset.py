# This is a ConTeXt ComputePods Chef plugin

# It provides the Chef with recipes on how to typeset ConTeXt
# documents....

import asyncio
import datetime
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


######################################################################
# Defaults
#texmfhomeDir   = os.path.join(os.sep, 'root', 'texmf')
#contextCmdPath = '/root/ConTeXt/tex/texmf-linux-64/bin/context'
rsyncCmdPath    = '/usr/bin/rsync'
localLogFileDir = '/tmp/chefLogs'
#privateKeyPath = "/config/playGround-rsync-rsa"
######################################################################

def registerPlugin(config, managers, natsClient) :
  print("Registering ConTeXt typeset plugin via registerPlugin")
  chefUtils()
  rsyncManager = managers['rsync']

  async def reportError(msg) :
    await natsClient.sendMessage(
      "build.result",
      {
        'result' : 'failed to build',
        'details' : [ msg ]
      }
    )
    return None

  async def reportDone(msg) :
    await natsClient.sendMessage(
      "done.build.getExternalDependencies.context",
      {
        'retCode' : 0,
        'message' : msg
      }
    )

  async def reportInfo(msg) :
    await natsClient.sendMessage(
      "logger.getExternalDependencies.context",
      msg
    )

  async def reportDebug(msg) :
    await natsClient.sendMessage(
      "logger.getExternalDependencies.context",
      msg
    )

  async def checkForValue(aKey, data, default, msg) :
    if aKey in data and data[aKey] : return data[aKey]
    if default : return default
    await reportError(msg)
    return None

  @natsClient.subscribe("build.from.context.>")
  async def dealWithBuildRequest(subject, data) :
    scriptsDir = os.path.abspath(os.path.dirname(__file__))
    workingDir = os.path.join(os.getcwd(), 'tmpContextDir')
    if 'workingDir' in config : workingDir = config['workingDir']
    if not (projectName := await checkForValue('projectName', data, None, "no projectName specified")) : return
    if not (targetName := await checkForValue('targetName', data, None, "no targetName specified")) : return
    workingDir = os.path.join(workingDir, projectName, targetName)
    await aioMakedirs(workingDir, exist_ok=True)

    if not (projectDir := await checkForValue('projectDir', data, None, "no projectDir specified")) : return
    if not (srcDir := await checkForValue('srcDir', data, None, "no srcDir specified")) : return
    if not (outputDir := await checkForValue('outputDir', data, None, "no outputDir specified")) : return
    if not (documentName := await checkForValue('mainFile', data, None, "no mainFile specified")) : return
    if not (rsyncHostName := await checkForValue('rsyncHostName', data, None, "rsyncHostName not specified")) : return
    if not (rsyncUserName := await checkForValue('rsyncUserName', data, None, "rsyncUserName not specified")) : return
    if not (clean := await checkForValue('clean', data, str(False), "clean not specified")) : return
    if not (live := await checkForValue('live', data, str(False), "live logging not specified")) : return
    if not (logFileDir := await checkForValue('logFileDir', data, str(False), "logFileDir not specified")) : return

    verbosity = 0
    if 'verbosity' in data : verbosity = data['verbosity']

    rsyncProjectDir   = os.path.join(projectDir, srcDir)
    rsyncProjectDir   = f"{rsyncUserName}@{rsyncHostName}:{rsyncProjectDir}"
    hostPublicKeyPath = rsyncManager.getHostPublicKeyPath(rsyncHostName)
    privateKeyPath    = "/config/playGround-rsync-rsa"

    if not (externals := await checkForValue('externals', data, None, "no externals supplied")) : return

    texmfContentsPath = os.path.join(os.sep, 'tmp', 'context-chef', projectName, targetName, 'texmfContents')
    await aioMakedirs(os.path.dirname(texmfContentsPath), exist_ok=True)
    with open(texmfContentsPath, 'w') as texmfFile :
      externals = sorted(externals)
      for anExternal in externals :
        texmfFile.write(f"{anExternal}\n")

    await natsClient.sendMessage('test', [
      "Hello form dealWithBuildRequest",
      projectName,
      targetName,
      projectDir,
      srcDir,
      outputDir,
      documentName,
      texmfContentsPath,
      rsyncProjectDir,
      hostPublicKeyPath,
      privateKeyPath,
      verbosity,
      clean,
      live
    ])
    taskName = "aTask"
    if 'help' in data : taskName = data['help']

    # check if hostPublicKey exists....
    if not os.path.exists(hostPublicKeyPath) :
      return await reportError('rsync host has no public key')

    taskDetails = {
      'cmd' : [
        '/bin/bash',
        os.path.join(scriptsDir, 'typeset.sh'),
        #documentName,
        #projectDir,
        #rsyncProjectDir
      ],
      'projectDir' : workingDir,
      'env'  : {
        #'RSYNC_RSH' : f"ssh -v -i {privateKeyPath} -o UserKnownHostsFile={hostPublicKeyPath}"
        #'RSYNC_RSH' : f"ssh -i {privateKeyPath} -o UserKnownHostsFile={hostPublicKeyPath}",
        'CHEF_workingDir'        : workingDir,
        'CHEF_projectDir'        : projectDir,
        'CHEF_srcDir'            : srcDir,
        'CHEF_outputDir'         : outputDir,
        'CHEF_documentName'      : documentName,
        'CHEF_texmfContentsPath' : texmfContentsPath,
        'TEXMFHOME'              : os.path.join(os.sep, 'root', 'texmf'),
        'CHEF_rsyncHostName'     : rsyncHostName,
        'CHEF_rsyncUserName'     : rsyncUserName,
        'CHEF_hostPublicKeyPath' : hostPublicKeyPath,
        'CHEF_privateKeyPath'    : privateKeyPath,
        'CHEF_verbosity'         : str(verbosity),
        'CHEF_clean'             : str(clean)
      }
    }
    timeNow = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
    logFilePath = f"{localLogFileDir}/{projectName}/{targetName}/{timeNow}.log"
    if live == str(True) :
      taskLog = MultiLogger([
        FileLogger("stdout", 5),
        FileLogger(logFilePath, 5),
        NatsLogger(natsClient, f"logger.{projectName}.{targetName}", 5),
      ])
    else :
      taskLog = FileLogger(logFilePath, 5)

    await taskLog.open()

    if 0 < verbosity :
      await taskLog.write([
        "\n",
        "=========================================================\n",
        "Running ConTeXt on:\n",
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
    returnCode  = theTask.getReturnCode()
    elapsedTime = theTask.getElapsedTime()
    await taskLog.write(f"\nreturn code: {returnCode}\nelapsed time: {str(elapsedTime)}")
    await taskLog.close()

    if logFileDir != str(False) :
      if logFileDir.startswith('~') :
        logFileDir = logFileDir.lstrip('~/')
      rsyncCmd = [
        rsyncCmdPath,
        '-av',
        localLogFileDir+os.sep,
        f"{rsyncUserName}@{rsyncHostName}:{logFileDir}{os.sep}"
      ]
      await reportDebug(" ".join(rsyncCmd))
      rsyncEnv = {
        'RSYNC_RSH' : f"ssh -i {privateKeyPath} -o UserKnownHostsFile={hostPublicKeyPath}"
      }
      rsyncProc = await asyncio.create_subprocess_exec(
        *rsyncCmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=rsyncEnv
      )
      projTaskName = f"{projectName}:{taskName}"
      stdout, stderr = await rsyncProc.communicate()
      await reportInfo(f'rsync logs for{projTaskName} exited with {rsyncProc.returncode}')
      if stdout:
        await reportDebug("\n".join([
          projTaskName,
          "----------------rsync stdout------------------------",
          stdout.decode(),
          "----------------rsync stdout------------------------",
        ]))
      if stderr:
        await reportDebug("\n".join([
          projTaskName,
          "----------------rsync stderr------------------------",
          stderr.decode(),
          "----------------rsync stderr------------------------",
        ]))
      if rsyncProc.returncode != 0 :
        await reportError(f"Could not rsync log files for {projTaskName}\n  from {localLogFileDir}\n  to {logFileDir}")

    await natsClient.sendMessage('done.'+subject[0], {
      'retCode'     : returnCode,
      'elapsedTime' : str(elapsedTime)
    })
    print("ALL DONE!")

  print("Finished registering Context Plugin")

async def registerArtefacts(config, natsClient) :
  await natsClient.sendMessage("artefact.register.type.pdfFile",{
    "name" : "pdfFile",
    "extensions" : [
      "*.pdf"
    ]
  })
