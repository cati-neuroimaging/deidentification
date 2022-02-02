import pytest
import os
import glob


ARCHIVES_OPENING_DIR = 'tests/data/archives/opening_archives'
ARCHIVES_NOT_OPENING_DIR = 'tests/data/archives/not_opening_archives'
FILES_DIR = 'tests/data/files'


@pytest.fixture(params=glob.glob(ARCHIVES_OPENING_DIR+'/*'))
def opening_archive_path(request):
    return request.param


@pytest.fixture(params=glob.glob(ARCHIVES_NOT_OPENING_DIR+'/*'))
def not_opening_archive_path(request):
    return request.param


@pytest.fixture(params=glob.glob(FILES_DIR+'/*'))
def non_archive_path(request):
    return request.param


def test_get_archive_ext():
    from deidentification.archive import get_archive_extensions
    extensions = ['.zip', '.gz', '.tar', '.bz2', '.tgz']
    for ext in extensions:
        assert ext in get_archive_extensions()


def test_is_archive_in_for_opening_archive(opening_archive_path):
    # Test if the function is_archive_in returns True for an archive that is a TAR or a ZIP
    from deidentification.archive import is_archive_in
    assert is_archive_in(opening_archive_path)


def test_is_archive_in_for_not_opening_archive(not_opening_archive_path):
    # Test if the is_archive_in raise an error for file that are not TAR or ZIP.
    # IRL files could have good extensions but tarlib or ziplib could not openened it
    from deidentification.archive import is_archive_in
    from deidentification.anonymizer import DeidentificationError
    with pytest.raises(DeidentificationError):
        is_archive_in(not_opening_archive_path)


def test_is_archive_in_for_files(non_archive_path):
    # Test if is_archive_in return False when an non archive file is on input
    from deidentification.archive import is_archive_in
    assert not is_archive_in(non_archive_path)


def test_is_archive_out_for_archives_paths(opening_archive_path):
    # Test if is_archive_out returns True if the path has an archive extension
    # Note : is_archive_out check only the file extension (not opening the file)
    from deidentification.archive import is_archive_out
    assert is_archive_out(opening_archive_path)


def test_is_archive_out_for_files_paths(non_archive_path):
    # Test if is_archive_out returns False if the path has no archive extension
    # Note : is_archive_out check only the file extension (not opening the file)

    from deidentification.archive import is_archive_out
    assert not is_archive_out(non_archive_path)
