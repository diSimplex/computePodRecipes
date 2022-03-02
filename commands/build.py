# This file contains the build commands.

import click
import os
import platform
import yaml

from cpcli.utils import runCommandWithNatsServer

async def sendBuildConTeXtCmd(config, natsServer) :
  print("Building a ConTeXt document")
  buildData = {
    'projectDir'    : 'sillyDir',
    'taskName'      : 'a silly task',
    'doc'           : 'silliestDoc.tex',
    'rsyncHostName' : platform.node(),
    'rsyncUserName' : os.getlogin()
  }
  await natsServer.sendMessage("build.from.context", buildData)

@click.command(short_help="build a ConTeXt document.")
def build() :
  print("Hello from builder")
  runCommandWithNatsServer(sendBuildConTeXtCmd)
  print("Bye from builder")
