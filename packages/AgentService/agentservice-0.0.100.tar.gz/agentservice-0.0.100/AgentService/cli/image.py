
import click
import subprocess
import os
import AgentService


@click.group()
def group():
    pass


@group.command('image', help="Command that creates docker image")
def update_image():
    image_dir = os.path.join(AgentService.__path__[0], "templates", "agent-image")

    subprocess.run(
        "docker build -t agentservice-base .",
        shell=True,
        text=True,
        cwd=image_dir
    )
