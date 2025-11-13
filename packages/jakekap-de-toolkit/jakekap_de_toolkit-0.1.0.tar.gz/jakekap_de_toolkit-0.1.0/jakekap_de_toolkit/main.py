import click
from jakekap_de_toolkit import vm

@click.group()
def cli():
    pass

cli.add_command(vm.start)
cli.add_command(vm.stop)
cli.add_command(vm.connect)

if __name__ == '__main__':
    cli()
