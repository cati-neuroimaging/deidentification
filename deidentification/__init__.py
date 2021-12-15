__version__ = '1.0.0'

from pathlib import Path
CONFIG_FOLDER = Path(__file__).parent.joinpath('config')


class DeidentificationError(Exception):
    pass
