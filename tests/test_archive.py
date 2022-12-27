import pytest
import glob


ARCHIVES_OPENING_DIR = 'tests/data/archives/opening_archives'
ARCHIVES_NOT_OPENING_DIR = 'tests/data/archives/not_opening_archives'
FILES_DIR = 'tests/data/files'


@pytest.fixture(params=glob.glob(ARCHIVES_OPENING_DIR + '/*'))
def opening_archive_path(request):
    return request.param


@pytest.fixture(params=glob.glob(ARCHIVES_NOT_OPENING_DIR + '/*'))
def not_opening_archive_path(request):
    return request.param


@pytest.fixture(params=glob.glob(FILES_DIR + '/*'))
def non_archive_path(request):
    return request.param


def test_get_archive_ext():
    from deidentification.archive import get_archive_extensions
    extensions = ['.zip', '.gz', '.tar', '.bz2', '.tgz']
    for ext in extensions:
        assert ext in get_archive_extensions()


def test_is_archive_file_for_opening_archive(opening_archive_path):
    # Test if is_archive_file returns True for TAR or ZIP archives
    from deidentification.archive import is_archive_file
    assert is_archive_file(opening_archive_path)


def test_is_archive_file_for_not_opening_archive(not_opening_archive_path):
    # Test if is_archive_file raises an error for files that are not TAR or ZIP.
    # Files may have such extensions, but tarlib or ziplib could not open them
    from deidentification.archive import is_archive_file
    from deidentification.anonymizer import DeidentificationError
    with pytest.raises(DeidentificationError):
        is_archive_file(not_opening_archive_path)


def test_is_archive_file_for_files(non_archive_path):
    # Test if is_archive_file return False for an non archive file
    from deidentification.archive import is_archive_file
    assert not is_archive_file(non_archive_path)


def test_is_archive_ext_for_archives_paths(opening_archive_path):
    # Test if is_archive_ext returns True if the path has an archive extension
    from deidentification.archive import is_archive_ext
    assert is_archive_ext(opening_archive_path)


def test_is_archive_ext_for_files_paths(non_archive_path):
    # Test if is_archive_ext returns False if the path has no archive extension
    from deidentification.archive import is_archive_ext
    assert not is_archive_ext(non_archive_path)
