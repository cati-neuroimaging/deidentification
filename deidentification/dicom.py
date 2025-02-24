from pathlib import Path

# List of DICOM Tag value modality (0008, 0060) that is considered as imaging data
MODALITIES_SUPPORTED = ['CT', 'MR', 'NM', 'PT', 'ST']

# List of DICOM Tag value SOP Class UID that is considered as raw data not kept
# More informations about SOP Class UID : https://dicom.nema.org/dicom/2013/output/chtml/part04/sect_B.5.html
# This list came from qualiCATI project. It has been created in order to filter
# MRI data received by the CATI, to avoid keeping non-imaging data.
SOP_CLASS_UID_NOT_SUPPORTED = [
    "1.2.840.10008.5.1.4.1.1.11.1",  # Grayscale Softcopy Presentation State IOD
    "1.2.840.10008.5.1.4.1.1.66",  # Raw Data IOD
    "1.2.840.10008.5.1.4.1.1.7",  # Secondary Capture Image IOD
]


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
    sop_class_ok = sop_class_uid not in SOP_CLASS_UID_NOT_SUPPORTED
    return modality_ok and sop_class_ok


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

