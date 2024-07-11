import csv
import json
import os

import pydicom


def get_dicom_header_str(filepath: str) -> str:
    return str(pydicom.read_file(filepath))


def get_tag_value(filepath: str, tag: tuple) -> str:
    ds = pydicom.read_file(filepath)
    return str(ds[tag].value)


def save_header(filepath: str, output_path: str) -> None:
    with open(output_path, 'w') as outfile:
        outfile.write(get_dicom_header_str(filepath))
