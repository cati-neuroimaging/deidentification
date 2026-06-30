import glob
import os
import os.path as osp
import shutil

import pytest

from deidentification import anonymizer

DATA_DIR = 'tests/data/'
CAPTURE_DATA_DIR = osp.join(DATA_DIR, 'captures')
OUTPUT_DIR = osp.join(CAPTURE_DATA_DIR, 'output_dir')


def path_ano(filepath):
    filename = osp.basename(filepath)
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


@pytest.fixture(params=glob.glob(CAPTURE_DATA_DIR + '/*'))
def capture_path(request):
    file_path = request.param
    if osp.isfile(file_path):
        yield file_path
    clean_outputs(file_path)


def test_ano_keep_capture(capture_path):
    capture_folder = osp.join(OUTPUT_DIR, "captures")
    os.makedirs(capture_folder)
    anonymizer.anonymize_file(capture_path, OUTPUT_DIR, capture_folder=capture_folder)
    assert len(glob.glob(capture_folder + "/*")) == 1


def test_ano_no_keep_capture(capture_path):
    capture_folder = osp.join(OUTPUT_DIR, "captures")
    os.makedirs(capture_folder)
    if "dicom" in osp.basename(capture_path):
        anonymizer.anonymize_file(capture_path, OUTPUT_DIR)
        assert not osp.exists(OUTPUT_DIR)
    else:
        with pytest.raises(anonymizer.AnonymizerError, match=r".*not a DICOM file.*{}".format(capture_path)):
            anonymizer.anonymize_file(capture_path, OUTPUT_DIR)


def test_ano_file_keep_capture(capture_path):
    anonymizer.anonymize(capture_path, OUTPUT_DIR, keep_capture=True)
    assert "captures" in os.listdir(OUTPUT_DIR)
    assert len(glob.glob(osp.join(OUTPUT_DIR, "captures") + "/*")) == 1


def test_ano_file_no_keep_capture(capture_path):
    if "dicom" in osp.basename(capture_path):
        anonymizer.anonymize(capture_path, OUTPUT_DIR, keep_capture=False)
        assert "captures" not in os.listdir(OUTPUT_DIR)
    else:
        with pytest.raises(anonymizer.AnonymizerError, match=r".*not a DICOM file.*{}".format(capture_path)):
            anonymizer.anonymize(capture_path, OUTPUT_DIR, keep_capture=False)