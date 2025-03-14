import glob
import os
import os.path as osp
import shutil
import subprocess
import tarfile
import tempfile

import pydicom
import pytest

from deidentification import anonymizer
from deidentification.anonymizer import Anonymizer, AnonymizerError, anonymize
from deidentification.config import load_config_profile

from . import create_fake_config

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


@pytest.fixture(params=[DICOM_DATA_DIR])
def dicom_with_other(request):
    # DICOM folder with DICOM and non-DICOM in it
    folder_path = osp.abspath(request.param)
    tmp_folder = tempfile.mkdtemp()
    if osp.isdir(folder_path):
        yield (folder_path, tmp_folder)
    # clean tmp_folder
    if osp.exists(tmp_folder):
        shutil.rmtree(tmp_folder)


@pytest.fixture(params=glob.glob(DICOM_DATA_DIR + '/non_imaging/*.tar.gz'))
def dicom_non_imaging_archives_path(request):
    file_path = request.param
    if osp.isfile(file_path):
        yield file_path
    clean_outputs(file_path)


# Anonymizer class tests

def test_anonymizer_basic(dicom_path):
    a = anonymizer.Anonymizer(dicom_path, path_ano(dicom_path))
    a.run_ano()
    assert True


def test_anonymizer_public_tags(dicom_path):
    a = anonymizer.Anonymizer(dicom_path, path_ano(dicom_path))
    a.run_ano()
    ds = pydicom.read_file(path_ano(dicom_path))
    assert ds.get((0x0008, 0x0008))
    assert not ds.get((0x0008, 0x0032))


def test_anonymizer_input_tags(dicom_path):
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
    a = anonymizer.Anonymizer(dicom_path, path_ano(dicom_path))
    a.run_ano()
    ds = pydicom.read_file(path_ano(dicom_path))
    assert not ds.get((0x2005, 0x1445), None)
    assert ds.get((0x2001, 0x1003), None)


def test_anonymizer_private_creator(dicom_path):
    tags_config = {
        (0x2005, 0x101d): {'action': 'K', 'private_creator': 'Philips MR Imaging DD 001'},
        (0x2005, 0x1013): {'action': 'K', 'private_creator': 'TOTO'},
    }
    a = anonymizer.Anonymizer(dicom_path, path_ano(dicom_path),
                              tags_config=tags_config)
    a.run_ano()
    ds = pydicom.read_file(path_ano(dicom_path))
    assert ds.get((0x2005, 0x101d), None)
    assert not ds.get((0x2005, 0x1013), None)


def test_anonymizer_data_sharing_profile(dicom_path):
    tags_config = load_config_profile('data_sharing')
    a = anonymizer.Anonymizer(dicom_path, path_ano(dicom_path),
                              tags_config=tags_config)
    a.run_ano()
    _ds = pydicom.read_file(dicom_path)
    assert _ds.get((0x2005, 0x101D))
    ds = pydicom.read_file(path_ano(dicom_path))
    assert ds.get((0x2005, 0x101D))


def test_anonymizer_not_file(dicom_archives_path):
    with pytest.raises(anonymizer.AnonymizerError, match=r".*not a DICOM file.*{}".format(dicom_archives_path)):
        _ = anonymizer.Anonymizer(dicom_archives_path, path_ano(dicom_archives_path))


def test_anonymizer_anonymous(dicom_archives_path):
    with pytest.raises(anonymizer.AnonymizerError, match=r"({})".format(dicom_archives_path)):
        _ = anonymizer.Anonymizer(dicom_archives_path, path_ano(dicom_archives_path))
    with pytest.raises(anonymizer.AnonymizerError, match=r"^((?!{}).)*$".format(dicom_archives_path)):
        _ = anonymizer.Anonymizer(dicom_archives_path, path_ano(dicom_archives_path),
                                  anonymous=True)


# anonymize function tests

def test_anonymize_basic(dicom_path):
    anonymize(dicom_path, OUTPUT_DIR)
    assert osp.basename(dicom_path) in os.listdir(OUTPUT_DIR)


def test_anonymize_data_sharing_profile(dicom_path):
    anonymize(dicom_path, OUTPUT_DIR, config_profile='data_sharing')
    assert osp.basename(dicom_path) in os.listdir(OUTPUT_DIR)


def test_anonymize_archive_basic(dicom_archives_path):
    anonymize(dicom_archives_path, path_ano(dicom_archives_path))
    assert osp.exists(path_ano(dicom_archives_path))


def test_anonymize_bad_archive_basic(dicom_bad_archives_path):
    with pytest.raises(AnonymizerError):
        anonymize(dicom_bad_archives_path, path_ano(dicom_bad_archives_path))


def test_anonymize_archive_data_sharing_progile(dicom_archives_path):
    anonymize(dicom_archives_path, path_ano(dicom_archives_path))
    assert osp.exists(path_ano(dicom_archives_path))


def test_anonymize_anonymous(file_path):
    with pytest.raises(AnonymizerError, match=r"({})".format(file_path)):
        anonymize(file_path, path_ano(file_path))
    with pytest.raises(AnonymizerError, match=r"^((?!{}).)*$".format(file_path)):
        anonymize(file_path, path_ano(file_path), anonymous=True)


def test_anonymize_config_safe_private(dicom_path):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    ds = pydicom.read_file(dicom_path)
    tags_config = {
        # Private Creator tag to be kept
        (0x2005, 0x0011): {
            'private_creator': ds.get((0x2005, 0x0011)).value,
            'action': 'K'
        },
        # Private Creator tag with wrong name
        (0x2005, 0x0012): {
            'private_creator': 'XX',
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


def test_anonymize_private_creator_tree(dicom_path):
    # In case of private tag and private creator tag in a block inside tag
    # Check that Private Creator if found and tag kept
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Create :
    # (3030, 1001)     1 item(s) ----
    #    (3033, 0010) Private Creator                     LO: 'Test deidentification'
    #    (3033, 1011) Private tag data                    SH: 'Very Important Tag'
    #    (3035, 1011) Private tag data                    SH: 'Very Important Tag2'
    #    ---------
    # (3035, 0010) Private Creator                     SH: 'Test deidentification2'

    ds = pydicom.read_file(osp.abspath(dicom_path))
    sequence_block = pydicom.Dataset()
    block = sequence_block.private_block(0x3033, 'Test deidentification', create=True)
    block.add_new(0x11, 'SH', 'Very Important Tag')
    block2 = sequence_block.private_block(0x3035, 'Test deidentification2', create=True)
    block2.add_new(0X11, 'SH', 'Very Important Tag2')
    del sequence_block[(0x3035, 0x10)]
    ds.add_new((0x3030, 0x1001), 'SQ', [sequence_block])
    ds.add_new((0x3035, 0x0010), 'SH', 'Test deidentification2')

    tmp_file = tempfile.NamedTemporaryFile()
    tmp_file_path = tmp_file.name
    ds.save_as(tmp_file_path)

    tags_config = {
        (0x3033, 0x1011): {
            'private_creator': 'Test deidentification',
            'action': 'K'
        },
        (0x3035, 0x1011): {
            'private_creator': 'Test deidentification2',
            'action': 'K'
        }
    }

    output_dicom_path = os.path.join(OUTPUT_DIR, os.path.basename(dicom_path))
    anon = Anonymizer(tmp_file_path,
                      osp.abspath(output_dicom_path),
                      tags_config)
    anon.run_ano()

    ds = pydicom.read_file(osp.abspath(output_dicom_path))

    assert ds[(0x3030, 0x1001)][0][(0x3033, 0x1011)]
    assert ds.get((0x3035, 0X0010))
    assert not ds[(0x3030, 0x1001)][0].get((0x3035, 1011))


def test_ano_several_private_creator_name(dicom_path):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    tmp_config = create_fake_config([
        ['(3033,1011)', 'VIT', 'K', 'Name1'],
        ['(3033,1011)', 'VIT', 'K', 'Name2'],
    ])

    ds = pydicom.read_file(osp.abspath(dicom_path))
    sequence_block = pydicom.Dataset()
    block = sequence_block.private_block(0x3033, 'Name1', create=True)
    block.add_new(0x11, 'SH', 'Very Important Tag')
    sequence_block2 = pydicom.Dataset()
    block2 = sequence_block2.private_block(0x3033, 'Name2', create=True)
    block2.add_new(0x11, 'SH', 'Very Important Tag')
    ds.add_new((0x3030, 0x1001), 'SQ', [sequence_block])
    ds.add_new((0x3034, 0x1001), 'SQ', [sequence_block2])

    tmp_file = tempfile.NamedTemporaryFile()
    tmp_file_path = tmp_file.name
    ds.save_as(tmp_file_path)

    output_dicom_path = os.path.join(OUTPUT_DIR, os.path.basename(dicom_path))
    anon = Anonymizer(tmp_file_path,
                      osp.abspath(output_dicom_path),
                      load_config_profile(tmp_config))
    anon.run_ano()

    ds = pydicom.read_file(osp.abspath(output_dicom_path))

    assert ds[(0x3030, 0x1001)][0].get((0x3033, 0x1011))
    assert ds[(0x3034, 0x1001)][0].get((0x3033, 0x1011))


def test_anonymize_non_imaging_dicom(dicom_non_imaging_archives_path):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    anonymize(dicom_non_imaging_archives_path, path_ano(dicom_non_imaging_archives_path))

    # Get list of all files in the archive
    with tarfile.open(path_ano(dicom_non_imaging_archives_path), 'r:gz') as tar:
        files_in_tar = tar.getnames()
    
    assert len(files_in_tar) == 1 and files_in_tar[0] == 'deidentification_report.csv'

def test_anonymize_non_dicom_w_err(dicom_with_other):
    dicom_folder, tmp_folder = dicom_with_other
    with pytest.raises(anonymizer.AnonymizerError, match=f".*not a DICOM file.*{dicom_folder}.*"):
        anonymize(dicom_folder, tmp_folder, error_no_dicom=True)


def test_anonymize_non_dicom_w_err_wo_seriesdescription(dicom_path):
    """Check that the lack of SeriesDescription does not raise an error anymore
    """
    ds = pydicom.read_file(osp.abspath(dicom_path))
    if ds.get('SeriesDescription', None) is not None:
        del ds['SeriesDescription']
    ds.Modality = "ANN"
    tmp_file = tempfile.NamedTemporaryFile()
    tmp_file_path = tmp_file.name
    ds.save_as(tmp_file_path)
    output_dicom_path = os.path.join(OUTPUT_DIR, os.path.basename(dicom_path))
    anonymize(tmp_file_path, output_dicom_path)
       

def test_anonymize_non_dicom_wo_err(dicom_with_other):
    dicom_folder, tmp_folder = dicom_with_other
    anonymize(DICOM_DATA_DIR, tmp_folder, error_no_dicom=False)


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
