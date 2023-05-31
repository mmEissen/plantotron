import os
import subprocess
import click
import sys
import getpass

from plantotron import _plantotron

ROOT_DIR_NAME = os.path.dirname(os.path.dirname(__file__))


@click.group()
def cli() -> None:
    pass


@cli.command()
def run() -> None:
    _plantotron.main()


SERVICE_TEMPLATE = """
[Unit]
Description=Water my plants
After=network-online.target

[Service]
ExecStart={python} {command}
WorkingDirectory={working_directory}
StandardOutput=inherit
StandardError=inherit
Restart=always
User={user}

[Install]
WantedBy=multi-user.target
"""


@cli.command()
def install() -> None:
    with open("/lib/systemd/system/plantotron.service", "w") as service_file:
        service_file.write(
            SERVICE_TEMPLATE.format(
                python=sys.executable,
                command="-m plantotron run",
                working_directory=ROOT_DIR_NAME,
                user=getpass.getuser(),
            )
        )
    subprocess.run(["systemctl", "enable", "plantotron.service"], check=True)
    subprocess.run(["systemctl", "start", "plantotron.service"], check=True)


cli()
