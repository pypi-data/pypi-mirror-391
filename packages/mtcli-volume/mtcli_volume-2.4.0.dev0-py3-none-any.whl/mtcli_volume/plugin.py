from mtcli_volume.volume import volume


def register(cli):
    cli.add_command(volume, name="vp")
