import pytest
import os


@pytest.fixture(params=os.listdir('tests/data/archives'))
def archive_path(request):
    return request.param


@pytest.fixture(params=os.listdir('tests/data/files'))
def non_archive_path(request):
    return request.param


def test_get_archive_ext():
    from deidentification.archive import get_archive_extensions
    extensions = ['.zip', '.gz', '.tar', '.bz2', '.tgz']
    for ext in extensions:
        assert ext in get_archive_extensions()


def test_is_archive(archive_path):
    from deidentification.archive import is_archive
    assert is_archive(archive_path)


def test_is_not_archive(non_archive_path):
    from deidentification.archive import is_archive
    assert not is_archive(non_archive_path)
    
