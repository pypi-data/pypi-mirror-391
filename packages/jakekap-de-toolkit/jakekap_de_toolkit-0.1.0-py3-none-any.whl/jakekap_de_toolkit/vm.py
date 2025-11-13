import click
import subprocess

@click.command()
def start():
    """Start your VM"""
    subprocess.run([
        "gcloud", "compute", "instances", "start",
        "--zone=us-east1-c", "bootcamp-lewagon"
    ], check=True)

@click.command()
def stop():
    """Stop your VM"""
    subprocess.run([
        "gcloud", "compute", "instances", "stop",
        "--zone=us-east1-c", "bootcamp-lewagon"
    ], check=True)

@click.command()
def connect():
    """Connect to your VM in VSCode inside your ~/code/jakekap/folder"""
    subprocess.run([
        "code", "--folder-uri",
        "vscode-remote://ssh-remote+jakekap@34.26.16.168/home/ce.andrade.p/code/Jakekap"
    ], check=True)
