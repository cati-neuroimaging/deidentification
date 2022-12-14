from pathlib import Path

from deidentification.info import __version__

CONFIG_FOLDER = Path(__file__).parent.joinpath('config')


class DeidentificationError(Exception):
    pass
