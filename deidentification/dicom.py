from pathlib import Path
import puremagic
import pydicom
import shutil
from subprocess import DEVNULL, run
import tempfile

# List of DICOM Tag value modality (0008, 0060) that is considered as imaging data
MODALITIES_SUPPORTED = ['CT', 'MR', 'NM', 'PT', 'ST']

# List of DICOM Tag value SOP Class UID that is considered as raw data not kept
# More informations about SOP Class UID : https://dicom.nema.org/dicom/2013/output/chtml/part04/sect_B.5.html
# This list came from qualiCATI project. It has been created in order to filter
# MRI data received by the CATI, to avoid keeping non-imaging data.
SOP_CLASS_UID_NO_IMAGING = [
    "1.2.840.10008.5.1.4.1.1.11.1",  # Grayscale Softcopy Presentation State IOD
    "1.2.840.10008.5.1.4.1.1.66",  # Raw Data IOD
    "1.2.840.10008.5.1.4.1.1.7",  # Secondary Capture Image IOD
]

CAPTURE_SOP_CLASS_UIDS = ["1.2.840.10008.5.1.4.1.1.7"]

def is_imaging_modality(dicom_ds):
    """ Check if modality tag (0008, 0060) in dicom correspond to a supported imaging modality.
    Supported modalities are:
    - CT: Computed Tomography
    - MR: Magnetic Resonance
    - NM: Nuclear Medicine
    - PT: Positron Emission Tomography (PET)
    - ST: Single-Photon Emission Computed Tomography (SPECT)
    """
    modality = dicom_ds.get((0x8, 0x60), None)
    if modality is None:
        return False
    sop_class_uid = dicom_ds.SOPClassUID
    
    modality_ok = modality.value in MODALITIES_SUPPORTED
    sop_class_ok = sop_class_uid not in SOP_CLASS_UID_NO_IMAGING
    return modality_ok and sop_class_ok


def is_dicom(filepath):
    magic = puremagic.magic_file(filepath)
    magic_mime_type = set(m.mime_type for m in magic)
    if "application/dicom" in magic_mime_type:
        return True
    return False


def is_capture(filepath):
    """
    Check if filepath is a capture file. Check if jpg, png, or DICOM with class UID of capture
    """
    # jpg : 'image/jpeg'
    # png : 'image/png'
    # DICOM : 'application/dicom'

    magic = puremagic.magic_file(filepath)
    magic_mime_type = set(m.mime_type for m in magic)
    if "image/jpeg" in magic_mime_type:
        return "image"
    elif "image/png" in magic_mime_type:
        return "image"
    elif "application/dicom" in magic_mime_type:
        try:
            # check tag
            ds = pydicom.read_file(filepath)
            if is_capture_dicom(ds):
                return "dicom"
        except Exception:
            return ""
    return ""


def is_capture_dicom(ds):
    """
    Check if an already loaded DICOM is a capture DICOM
    """
    # TODO Maybe add modality "SC" for Secondary Capture (modality found in DICOM conformance)
    class_uid = ds.get("SOPClassUID")
    if class_uid and class_uid in CAPTURE_SOP_CLASS_UIDS:
        return True
    return False


def is_spectro(filepath):
    # check if spec2nii peut faire la conversion en mode auto
    # si non, vérifier avec les extension des fichiers et tenter avec les options philips_dl ou philips_dicom
    
    temp_folder = tempfile.mkdtemp()
    cmd = ["spec2nii", "auto", "-o", temp_folder, filepath]
    cmd_ph = ["spec2nii", "philips_dcm", "-o", temp_folder, filepath]

    try:
        run(cmd, shell=False, check=True, stderr=DEVNULL, stdout=DEVNULL)
    except Exception:
        try:
            run(cmd_ph, shell=False, check=True, stderr=DEVNULL, stdout=DEVNULL)
        except Exception:
            return False
    finally:
        shutil.rmtree(temp_folder, ignore_errors=True)

    return True


def is_folder_empty_of_files(folder_path) -> bool:
    if isinstance(folder_path, str):
        folder_path = Path(folder_path)
    if not folder_path.is_dir():
        return False
    
    for item in folder_path.iterdir():
        if item.is_file():
            return False
        if item.is_dir() and not is_folder_empty_of_files(item):
            return False
    
    return True

