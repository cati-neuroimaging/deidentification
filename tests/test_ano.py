import glob
import os
import os.path as osp
import pytest
import shutil
import subprocess

import pydicom

DATA_DIR = 'tests/data/'
DICOM_DATA_DIR = osp.join(DATA_DIR, 'dicoms')
FILES_DATA_DIR = osp.join(DATA_DIR, 'files')
OUTPUT_DIR = osp.join(DICOM_DATA_DIR, 'output_dir')
BIN_DIR = 'bin'


def path_ano(filepath):
    filename = os.path.basename(filepath)
    filename_wo_ext = filename.split('.')[0]
    return filepath.replace(filename_wo_ext, filename_wo_ext + '_ano')


def clean_outputs(filepath):
    filepath_ano = path_ano(filepath)
    if osp.exists(filepath_ano):
        if osp.isfile(filepath_ano):
            os.remove(filepath_ano)
        else:
            shutil.rmtree(filepath_ano)
    if osp.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)


@pytest.fixture(params=glob.glob(DICOM_DATA_DIR + '/*[!.tar.gz]'))
def dicom_path(request):
    file_path = request.param
    if osp.isfile(file_path):
        yield file_path
    clean_outputs(file_path)


@pytest.fixture(params=glob.glob(DICOM_DATA_DIR + '/*.tar.gz'))
def dicom_archives_path(request):
    file_path = request.param
    if osp.isfile(file_path):
        yield file_path
    clean_outputs(file_path)
    

@pytest.fixture(params=glob.glob(DICOM_DATA_DIR + '/bad_format/*.tar.gz'))
def dicom_bad_archives_path(request):
    file_path = request.param
    if osp.isfile(file_path):
        yield file_path
    clean_outputs(file_path)


@pytest.fixture(params=glob.glob(FILES_DATA_DIR + '/*'))
def file_path(request):
    file_path = request.param
    if osp.exists(file_path):
        yield file_path
    clean_outputs(file_path)


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


def test_anonymizer_input_tags(dicom_path):
    from deidentification import anonymizer
    tags_config = {
        (0x0008, 0x0032): {'action': 'K'},  # Usually deleted
        (0x0008, 0x0008): {'action': 'X'}  # Usually kept
    }
    a = anonymizer.Anonymizer(dicom_path, path_ano(dicom_path),
                              tags_config=tags_config)  # Usually kept
    a.run_ano()
    ds = pydicom.read_file(path_ano(dicom_path))
    assert not ds.get((0x0008, 0x0008))
    assert ds.get((0x0008, 0x0032))


def test_anonymizer_private_tags(dicom_path):
    from deidentification import anonymizer
    a = anonymizer.Anonymizer(dicom_path, path_ano(dicom_path))
    a.run_ano()
    ds = pydicom.read_file(path_ano(dicom_path))
    assert not ds.get((0x2005, 0x1445), None)
    assert ds.get((0x2001, 0x1003), None)


def test_anonymizer_private_creator(dicom_path):
    from deidentification import anonymizer
    tags_config = {
        (0x2005, 0x100d): {'action': 'K', 'private_creator': 'Philips MR Imaging DD 001'},
        (0x2005, 0x100e): {'action': 'K', 'private_creator': 'TOTO'},
    }
    a = anonymizer.Anonymizer(dicom_path, path_ano(dicom_path),
                              tags_config=tags_config)
    a.run_ano()
    ds = pydicom.read_file(path_ano(dicom_path))
    assert ds.get((0x2005, 0x100d), None)
    assert not ds.get((0x2005, 0x100e), None)


def test_anonymizer_data_sharing_profile(dicom_path):
    from deidentification import anonymizer
    from deidentification.config import load_config_profile
    tags_config = load_config_profile('data_sharing')
    a = anonymizer.Anonymizer(dicom_path, path_ano(dicom_path),
                              tags_config=tags_config)
    a.run_ano()
    _ds = pydicom.read_file(dicom_path)
    assert _ds.get((0x2005, 0x101D))
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
        

def test_anonymize_config_safe_private(dicom_path):
    from deidentification.anonymizer import Anonymizer
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    ds = pydicom.read_file(dicom_path)
    tags_config = {
        # Private Creator tag to be kept
        (0x2005, 0x0011): {
            'name': ds.get((0x2005, 0x0011)).value,
            'action': 'K'
        },
        # Private Creator tag with wrong name
        (0x2005, 0x0012): {
            'name': 'XX',
            'action': 'K'
        }
    }
    output_dicom_path = os.path.join(OUTPUT_DIR, os.path.basename(dicom_path))
    anon = Anonymizer(os.path.abspath(dicom_path),
                      os.path.abspath(output_dicom_path),
                      tags_config)
    anon.run_ano()
    
    ds = pydicom.read_file(output_dicom_path)
    
    assert ds.get((0x2005, 0x0011))
    assert ds.get((0x2005, 0x1199)) and ds.get((0x2005, 0x1134))
    assert ds.get((0x2005, 0x0012))
    assert not ds.get((0x2005, 0x1213))
        

# Anonymize bin

def test_deidentification_bin(dicom_path):
    cmd = [osp.join(BIN_DIR, 'deidentification'),
           '-in', dicom_path,
           '-out', OUTPUT_DIR,
           '-c', 'cati_collector']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    assert not stderr
    assert os.listdir(OUTPUT_DIR)
