from deidentification.info import __version__

from pathlib import Path
CONFIG_FOLDER = Path(__file__).parent.joinpath('config')


class DeidentificationError(Exception):
    pass
