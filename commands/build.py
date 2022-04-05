# This file contains the build commands.

import click
import os
import platform
import yaml

from cpcli.utils import runCommandWithNatsServer, \
     getDataFromMajorDomo, postDataToMajorDomo

async def sendBuildConTeXtCmd(buildData, config, natsServer) :
  print("Building a ConTeXt document")
  projectName = buildData['projectName']
  targetName  = buildData['targetName']
  await natsServer.sendMessage(
    f"build.from.context.{projectName}.{targetName}",
    #f"build.from.context.{projectName}",
    buildData
  )

@click.command(short_help="build a ConTeXt document.")
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

