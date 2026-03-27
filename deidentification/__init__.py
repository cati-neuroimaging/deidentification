from pathlib import Path
import importlib.metadata

__version__ = importlib.metadata.version("deidentification")

CONFIG_FOLDER = Path(__file__).parent.joinpath('config')


class DeidentificationError(Exception):
    pass
