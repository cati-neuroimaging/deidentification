import glob
import os
import os.path as osp
import pytest
import shutil

import pydicom

DATA_DIR = 'tests/data/'
DICOM_DATA_DIR = osp.join(DATA_DIR, 'dicoms')
FILES_DATA_DIR = osp.join(DATA_DIR, 'files')
OUTPUT_DIR = osp.join(DICOM_DATA_DIR, 'output_dir')


def path_ano(filepath):
    filename = os.path.basename(filepath)
    filename_wo_ext = filename.split('.')[0]
    return filepath.replace(filename_wo_ext, filename_wo_ext + '_ano')


@pytest.fixture(params=glob.glob(DICOM_DATA_DIR + '/*[!.tar.gz]'))
def dicom_path(request):
    file_path = request.param
    if osp.isfile(file_path):
        yield file_path
    if osp.exists(path_ano(file_path)):
        os.remove(path_ano(file_path))
    if osp.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)


@pytest.fixture(params=glob.glob(DICOM_DATA_DIR + '/*.tar.gz'))
def dicom_archives_path(request):
    file_path = request.param
    if osp.isfile(file_path):
        yield file_path
    if osp.exists(path_ano(file_path)):
        os.remove(path_ano(file_path))
    if osp.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    

@pytest.fixture(params=glob.glob(DICOM_DATA_DIR + '/bad_format/*.tar.gz'))
def dicom_bad_archives_path(request):
    file_path = request.param
    if osp.isfile(file_path):
        yield file_path
    if osp.exists(path_ano(file_path)):
        os.remove(path_ano(file_path))
    if osp.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)


@pytest.fixture(params=glob.glob(FILES_DATA_DIR + '/*'))
def file_path(request):
    file_path = request.param
    if osp.exists(file_path):
        yield file_path
    path_ano_ = path_ano(file_path)
    if osp.exists(path_ano_):
        if osp.isfile(path_ano_):
            os.remove(path_ano_)
        else:
            shutil.rmtree(path_ano_)


# Config

def test_tag_lists():
    from deidentification.tag_lists import conf_profile, conf_profile_range
    from deidentification.tag_lists import safe_private_attributes
    assert isinstance(conf_profile, dict)
    assert isinstance(conf_profile_range, dict)
    assert isinstance(safe_private_attributes, dict)


def test_anonymizer_profile_load():
    from deidentification.config import load_config_profile
    from deidentification import DeidentificationError
    tags_to_keep = load_config_profile('data_sharing')
    assert isinstance(tags_to_keep, list)
    with pytest.raises(DeidentificationError, match=r"Profile .* does not exists."):
        tags_to_keep = load_config_profile('wrong_profile')


def test_tag_to_tuple():
    from deidentification.config import tag_to_tuple
    tags = {
        '(0010, 005A)': (0x0010, 0x005A),
        'F010,1010': (0xF010, 0x1010),
        '(1,1)': (0x0001, 0x0001),
    }
    for tag_str, tag_value in tags.items():
        assert tag_to_tuple(tag_str) == tag_value

    wrong_tags = ['(0010)', '0250 0010', '(2005, 1050, 0001)', '(2005, 1015a)', '000h, 2005']
    for wrong_tag in wrong_tags:
        with pytest.raises(ValueError, match=r"Input tag .* must contains .*"):
            tag_to_tuple(wrong_tag)


# Anonymizer class tests

def test_anonymizer_basic(dicom_path):
    from deidentification import anonymizer
    a = anonymizer.Anonymizer(dicom_path, path_ano(dicom_path))
    a.run_ano()
    assert True


def test_anonymizer_public_tags(dicom_path):
    from deidentification import anonymizer
    a = anonymizer.Anonymizer(dicom_path, path_ano(dicom_path))
    a.run_ano()
    ds = pydicom.read_file(path_ano(dicom_path))
    assert ds.get((0x0008, 0x0008))
    assert not ds.get((0x0008, 0x0032))


def test_anonymizer_private_tags(dicom_path):
    from deidentification import anonymizer
    a = anonymizer.Anonymizer(dicom_path, path_ano(dicom_path))
    a.run_ano()
    ds = pydicom.read_file(path_ano(dicom_path))
    assert not ds.get((0x2005, 0x1445), None)
    assert ds.get((0x2001, 0x1003), None)


def test_anonymizer_data_sharing_profile(dicom_path):
    from deidentification import anonymizer
    from deidentification.config import load_config_profile
    tags_to_keep = load_config_profile('data_sharing')
    a = anonymizer.Anonymizer(dicom_path, path_ano(dicom_path),
                              tags_to_keep=tags_to_keep)
    a.run_ano()
    ds = pydicom.read_file(path_ano(dicom_path))
    assert ds.get((0x2005, 0x101D))


def test_anonymizer_not_file(dicom_archives_path):
    from deidentification import anonymizer
    with pytest.raises(anonymizer.AnonymizerError, match=r".*not a DICOM file.*{}".format(dicom_archives_path)):
        _ = anonymizer.Anonymizer(dicom_archives_path, path_ano(dicom_archives_path))


def test_anonymizer_anonymous(dicom_archives_path):
    from deidentification import anonymizer
    with pytest.raises(anonymizer.AnonymizerError, match=r"({})".format(dicom_archives_path)):
        _ = anonymizer.Anonymizer(dicom_archives_path, path_ano(dicom_archives_path))
    with pytest.raises(anonymizer.AnonymizerError, match=r"^((?!{}).)*$".format(dicom_archives_path)):
        _ = anonymizer.Anonymizer(dicom_archives_path, path_ano(dicom_archives_path),
                                  anonymous=True)


# anonymize function tests

def test_anonymize_basic(dicom_path):
    from deidentification.anonymizer import anonymize
    anonymize(dicom_path, OUTPUT_DIR)
    assert osp.basename(dicom_path) in os.listdir(OUTPUT_DIR)


def test_anonymize_data_sharing_profile(dicom_path):
    from deidentification.anonymizer import anonymize
    anonymize(dicom_path, OUTPUT_DIR, config_profile='data_sharing')
    assert osp.basename(dicom_path) in os.listdir(OUTPUT_DIR)


def test_anonymize_archive_basic(dicom_archives_path):
    from deidentification.anonymizer import anonymize
    anonymize(dicom_archives_path, path_ano(dicom_archives_path))
    assert osp.exists(path_ano(dicom_archives_path))


def test_anonymize_bad_archive_basic(dicom_bad_archives_path):
    from deidentification.anonymizer import anonymize, AnonymizerError
    with pytest.raises(AnonymizerError):
        anonymize(dicom_bad_archives_path, path_ano(dicom_bad_archives_path))


def test_anonymize_archive_data_sharing_progile(dicom_archives_path):
    from deidentification.anonymizer import anonymize
    anonymize(dicom_archives_path, path_ano(dicom_archives_path))
    assert(osp.exists(path_ano(dicom_archives_path)))


def test_anonymize_anonymous(file_path):
    from deidentification.anonymizer import anonymize, AnonymizerError
    with pytest.raises(AnonymizerError, match=r"({})".format(file_path)):
        anonymize(file_path, path_ano(file_path))
    with pytest.raises(AnonymizerError, match=r"^((?!{}).)*$".format(file_path)):
        anonymize(file_path, path_ano(file_path), anonymous=True)
        
