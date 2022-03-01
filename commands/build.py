# This file contains the build commands.

import click
import yaml

from cpcli.utils import runCommandWithNatsServer

async def sillyCmd(config, natsServer) :
  print("Hello from sillyCmd!")
  await natsServer.sendMessage("SillySubject", "aMessage")

@click.command(short_help="build a ConTeXt document.")
def build() :
  print("Hello from builder")
  runCommandWithNatsServer(sillyCmd)
  print("Bye from builder")

