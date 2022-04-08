# This is a ConTeXt ComputePods Chef plugin

# It provides the Chef with recipes on how to update/rebuild the ConTeXt
# TEXMFHOME TDS directory of modules.

import asyncio
import logging
import os
import signal
import yaml
from aiofiles.os import wrap

aioMakedirs = wrap(os.makedirs)
aioSystem   = wrap(os.system)

from cputils.debouncingTaskRunner import \
  NatsLogger, FileLogger, MultiLogger, DebouncingTaskRunner
from cputils.rsyncFileTransporter import RsyncFileTransporter

from cpchef.utils import chefUtils
import cpchef.plugins

######################################################################
# Defaults
texmfhomeDir   = os.path.join(os.sep, 'root', 'texmf')
contextCmdPath = '/root/ConTeXt/tex/texmf-linux-64/bin/context'
rsyncCmdPath   = '/usr/bin/rsync'
privateKeyPath = "/config/playGround-rsync-rsa"
######################################################################

def registerPlugin(config, managers, natsClient) :
  print("Registering ConTeXt texmfhome plugin via registerPlugin")
  chefUtils()
  rsyncManager = managers['rsync']

  async def reportError(msg) :
    await natsClient.sendMessage(
      "build.result",
      {
        'result' : 'failed to update the TEXMFHOME',
        'details' : [ msg ]
      }
    )
    return None

  async def checkForValue(aKey, data, msg) :
    if aKey in data and data[aKey] : return data[aKey]
    await reportError(msg)
    return None

  @natsClient.subscribe("build.externalDependencies.>")
  async def dealWithBuildRequest(subject, data) :
    if subject[3] != 'context' : return

    logging.info("starting to update the ConTeXt modules in texmf")

    scriptsDir = os.path.abspath(os.path.dirname(__file__))

    for aPkgName, aPkgDef in data.items() :
      if not (projectDir   := await checkForValue('projectDir',   aPkgDef, "no projectDir specified")) : return
      if not (installDir   := await checkForValue('installDir',   aPkgDef, "no installDir specified")) : return
      if not (manualUpdate := await checkForValue('manualUpdate', aPkgDef, "no projectDir specified")) : return
      if manualUpdate :
        pkgDir = os.path.join(projectDir, installDir)
      else :
        if not (outputDir    := await checkForValue('outputDir',    aPkgDef, "no outputDir specified")) : return
        pkgDir = os.path.join(projectDir, outputDir)

      moduleDir = os.path.join(texmfhomeDir, installDir)
      await aioMakedirs(moduleDir, exist_ok=True)

      if not (rsyncUser    := await checkForValue('rsyncUser',    aPkgDef, "no rsyncUser specified")) : return
      if not (rsyncHost    := await checkForValue('rsyncHost',    aPkgDef, "no rsyncHost specified")) : return

      origPath = f"{rsyncUser}@{rsyncHost}:{pkgDir}{os.sep}"

      rsyncCmd = [
        rsyncCmdPath,
        '-av',
        origPath,
        moduleDir
      ]

      hostPublicKeyPath = rsyncManager.getHostPublicKeyPath(rsyncHost)
      rsyncEnv = {
        'RSYNC_RSH' : f"ssh -i {privateKeyPath} -o UserKnownHostsFile={hostPublicKeyPath}"
      }

      rsyncProc = await asyncio.create_subprocess_exec(
        *rsyncCmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=rsyncEnv
      )

      stdout, stderr = await rsyncProc.communicate()

      logging.info(f'rsync ({aPkgName}) exited with {rsyncProc.returncode}')
      if stdout:
        logging.debug("\n".join([
          aPkgName,
          "----------------rsync stdout------------------------",
          stdout.decode(),
          "----------------rsync stdout------------------------",
        ]))
      if stderr:
        logging.debug("\n".join([
          aPkgName,
          "----------------rsync stderr------------------------",
          stderr.decode(),
          "----------------rsync stderr------------------------",
        ]))
      if rsyncProc.returncode != 0 :
        logging.info(f"Could not rsync module files for {aPkgName}\n  from {origPath}\n  to {moduleDir}")

    updateCmd = [
      contextCmdPath,
      '-generate'
    ]

    updateProc = await asyncio.create_subprocess_exec(
      *updateCmd,
      stdout=asyncio.subprocess.PIPE,
      stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await updateProc.communicate()

    logging.info(f'context texmf update exited with {updateProc.returncode}')
    if stdout:
      logging.debug("\n".join([
        'update ConTeXt modules in texmf',
        "----------------update stdout------------------------",
        stdout.decode(),
        "----------------update stdout------------------------",
      ]))
    if stderr:
      logging.debug("\n".join([
        'update ConTeXt modules in texmf',
        "----------------update stderr------------------------",
        stderr.decode(),
        "----------------update stderr------------------------",
      ]))
    if updateProc.returncode != 0 :
      logging.info(f"Could not update the ConTeXt modules in texmf")

    logging.info("Finished updating ConTeXt modules in texmf")

    return

  print("Finished registering Context Plugin")

async def registerArtefacts(config, natsClient) :
  await natsClient.sendMessage("artefact.register.type.pdfFile",{
    "name" : "pdfFile",
    "extensions" : [
      "*.pdf"
    ]
  })
