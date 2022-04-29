# This file contains the context (typeset) commands.

import asyncio
import click
import os
import platform
import yaml

from cpcli.utils import runCommandWithNatsServer, \
     getDataFromMajorDomo, postDataToMajorDomo

@click.group(
  short_help="Typeset documents using ConTeXt",
  help="Typeset documents using ConTeXt"
)
def context() :
  """Click group command use to collect all of the ConTeXt commands."""

  pass

def registerCommands(theCli) :
  """Register the ConTeXt command with the main cli click group command."""

  theCli.add_command(context)

async def sendBuildConTeXtCmd(buildData, config, natsServer) :
  print("Building a ConTeXt document")
  projectName = buildData['projectName']
  targetName  = buildData['targetName']

  waitTillDone = asyncio.Event()

  async def echoNatsMessages(aSubject, theSubject, theMsg) :
    if isinstance(theMsg, str) and theMsg[1] != 'D' :
      print(theMsg.strip("\""))
    elif isinstance(theMsg, dict) :
      if 'retCode' in theMsg :
        print(f"completed with code: {theMsg['retCode']}")
      if 'elapsedTime' in theMsg :
        print(f"completed in {str(theMsg['elapsedTime'])}")
      if 'message' in theMsg :
        print(f"Message: {theMsg['message']}")
      if 'exception' in theMsg :
        print(f"Exception: {theMsg['exception']}")
      if 'traceback' in theMsg :
        print(f"Traceback: \n{theMsg['traceback']}")

    if theSubject.startswith("done") or theSubject.startswith('failed') :
        print("\n--------------------------------------------------------------------------------\n")
        waitTillDone.set()

  await natsServer.listenToSubject(
    f"logger.{projectName}.{targetName}", echoNatsMessages
  )
  await natsServer.listenToSubject(
    f"*.build.from.context.{projectName}.{targetName}", echoNatsMessages
  )

  await natsServer.sendMessage(
    f"build.from.context.{projectName}.{targetName}",
    #f"build.from.context.{projectName}",
    buildData
  )

  await waitTillDone.wait()

@context.command(
  short_help="build a ConTeXt document.",
  help="build a ConTeXt document."
)
@click.option('--clean', is_flag=True, default=False,
  help="Clean up working directory before starting [default: False]"
)
@click.option('--live',  is_flag=True, default=False,
  help="Provide live logging of build [default: False]"
)
@click.argument("projectName")
@click.argument("target")
@click.pass_context
def build(ctx, clean, live, projectname, target) :
  print(f"Building {projectname}:{target}")
  data = getDataFromMajorDomo(f'/project/buildTarget/{projectname}/{target}')
  if data is None : return
  data['projectName']   = projectname
  data['targetName']    = target
  data['clean']         = str(clean)
  data['live']          = str(live)
  data['rsyncHostName'] = platform.node()
  data['rsyncUserName'] = os.getlogin()
  data['verbosity']     = ctx.obj['config']['verbosity']

  runCommandWithNatsServer(data, sendBuildConTeXtCmd)

async def sendRebuildCmd(buildData, config, natsServer) :
  print("Rebuilding the ConTeXt module dependencies")

  waitTillDone = asyncio.Event()

  async def echoNatsMessages(aSubject, theSubject, theMsg) :
    if isinstance(theMsg, str) and theMsg[1] != 'D' :
      print(theMsg.strip("\""))
    elif isinstance(theMsg, dict) :
      if 'retCode' in theMsg :
        print(f"completed with code: {theMsg['retCode']}")
      if 'elapsedTime' in theMsg :
        print(f"completed in {str(theMsg['elapsedTime'])}")
      if 'message' in theMsg :
        print(f"Message: {theMsg['message']}")
      if 'exception' in theMsg :
        print(f"Exception: {theMsg['exception']}")
      if 'traceback' in theMsg :
        for aLine in theMsg['traceback'] : print(aLine)

    if theSubject.startswith("done") or theSubject.startswith('failed') :
        print("\n--------------------------------------------------------------------------------\n")
        waitTillDone.set()

  await natsServer.listenToSubject(
    f"logger.getExternalDependencies.context", echoNatsMessages
  )
  await natsServer.listenToSubject(
    f"*.build.getExternalDependencies.context", echoNatsMessages
  )

  await natsServer.sendMessage(
    "build.getExternalDependencies.context",
    buildData
  )

  await waitTillDone.wait()

@context.command(
  short_help="rebuild the local texmf modules",
  help="rebuild the local texmf modules"
)
@click.option('--clean', is_flag=True, default=False,
  help="Clean up working directory before starting [default: False]"
)
@click.pass_context
def rebuildModules(ctx, clean) :
  print("Rebuilding local ConTeXt texmf modules")
  data = {
    'clean' : str(clean)
  }
  runCommandWithNatsServer(data, sendRebuildCmd)
