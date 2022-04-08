# This file contains the context (typeset) commands.

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
  await natsServer.sendMessage(
    f"build.from.context.{projectName}.{targetName}",
    #f"build.from.context.{projectName}",
    buildData
  )

@context.command(
  short_help="build a ConTeXt document.",
  help="build a ConTeXt document."
)
@click.argument("projectName")
@click.argument("target")
@click.pass_context
def build(ctx, projectname, target) :
  print(f"Building {projectname}:{target}")
  data = getDataFromMajorDomo(f'/project/buildTarget/{projectname}/{target}')
  data['projectName']   = projectname
  data['targetName']    = target
  data['rsyncHostName'] = platform.node()
  data['rsyncUserName'] = os.getlogin()
  runCommandWithNatsServer(data, sendBuildConTeXtCmd)

async def sendRebuildCmd(buildData, config, natsServer) :
  await natsServer.sendMessage(
    "build.getExternalDependencies.context",
    buildData
  )

@context.command(
  short_help="rebuild the local texmf modules",
  help="rebuild the local texmf modules"
)
@click.pass_context
def rebuildModules(ctx) :
  print("Rebuilding local ConTeXt texmf modules")
  runCommandWithNatsServer(None, sendRebuildCmd)
