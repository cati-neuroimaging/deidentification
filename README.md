# deidentification

Tool to remove metadata allowing to identify a subject from DICOM images used in neuroimaging research. Can anonymize dicom files or archives of dicoms.

## Dependencies

- Python >= 2.7
- Pydicom >= 1.4.2

## Deidentification norm

[DICOM attribute confidentiality Profiles](http://dicom.nema.org/medical/dicom/current/output/html/part15.html#chapter_E)

- X means the attribute must be removed
- U means the attribute must be replaced with a cleaned but internally consistent UUID
- D means replace with a non-zero length dummy value
- Z means replace with a zero or non-zero length dummy value
- C means the attribute can be kept if it is cleaned

```python
annex_e = {
    (0x0008, 0x0050): ['N', 'Y', 'Z', '', '', '', '', '', '', '', '', ''],  # Accession Number
    (0x0018, 0x4000): ['Y', 'N', 'X', '', '', '', '', '', '', 'C', '', ''],  # Acquisition Comments
    (0x0040, 0x0555): ['N', 'Y', 'X', '', '', '', '', '', '', '', 'C', ''],  # Acquisition Context Sequence
    (0x0008, 0x0022): ['N', 'Y', 'X/Z', '', '', '', '', 'K', 'C', '', '', ''],  # Acquisition Date
    (0x0008, 0x002A): ['N', 'Y', 'X/D', '', '', '', '', 'K', 'C', '', '', ''],  # Acquisition DateTime
    (0x0018, 0x1400): ['N', 'Y', 'X/D', '', '', '', '', '', '', 'C', '', ''],  # Acquisition Device Processing Description
    (0x0018, 0x9424): ['N', 'Y', 'X', '', '', '', '', '', '', 'C', '', ''],  # Acquisition Protocol Description
    (0x0008, 0x0032): ['N', 'Y', 'X/Z', '', '', '', '', 'K', 'C', '', '', ''],  # Acquisition Time
    (0x0040, 0x4035): ['N', 'N', 'X', '', '', '', '', '', '', '', '', ''],  # Actual Human Performers Sequence
    (0x0010, 0x21B0): ['N', 'Y', 'X', '', '', '', '', '', '', 'C', '', ''],  # Additional Patient's History
    (0x0038, 0x0010): ['N', 'Y', 'X', '', '', '', '', '', '', '', '', ''],  # Admission ID
    (0x0038, 0x0020): ['N', 'N', 'X', '', '', '', '', 'K', 'C', '', '', ''],  # Admitting Date
    (0x0008, 0x1084): ['N', 'Y', 'X', '', '', '', '', '', '', 'C', '', ''],  # Admitting Diagnoses Code Sequence
    (0x0008, 0x1080): ['N', 'Y', 'X', '', '', '', '', '', '', 'C', '', ''],  # Admitting Diagnoses Description
    (0x0038, 0x0021): ['N', 'N', 'X', '', '', '', '', 'K', 'C', '', '', ''],  # Admitting Time

    [....]

}
```

## Config file

Tag to keep for CATI :

```python
tags_to_keep = [
    (0x0008, 0x0020), (0x0008, 0x0031), (0x0008, 0x0032), (0x0008, 0x0033),
    (0x0008, 0x103E), (0x0010, 0x0010), (0x0019, 0x100A), (0x0019, 0x100C),
    (0x0019, 0x101E), (0x0019, 0x105A), (0x0019, 0x107E), (0x0019, 0x109F),
    (0x0021, 0x105A), (0x0025, 0x1007), (0x0027, 0x1060), (0x0043, 0x102C),
    (0x0043, 0x102F), (0x0043, 0x1039), (0x0051, 0x100A), (0x0051, 0x100B),
    (0x0051, 0x100C), (0x0051, 0x100E), (0x0051, 0x100F), (0x0051, 0x1011),
    (0x0051, 0x1016), (0x2001, 0x1003), (0x2001, 0x100B), (0x2001, 0x1013),
    (0x2001, 0x1014), (0x2001, 0x1018), (0x2001, 0x101B), (0x2001, 0x1081),
    (0x2005, 0x101D), (0x2005, 0x1074), (0x2005, 0x1075), (0x2005, 0x1076),
    (0x2005, 0x10A1), (0x2005, 0x10A9)
]
```

## Improvements

- Take into account XA11 version
- What to do with CSA header ?

## How to use it?

### As a script

Launch anon_example.py function to anonymize a dicom file.

Whitout subject id (set as "Unknown" by default):

```sh
python anon_example.py -in myInputFolder -out myOutputFolder
```

With a subject id:

```sh
python anon_example.py -in myInputFolder -out myOutputFolder -ID 0001XXXX
```

### Using python module

```python
from deidentification import anonymizer
from deidentification.config import tag_to_keep

dicom_input_path = '/path/to/dicom_input_file'
dicom_output_path = '/path/to/dicom_output_file'

anonymizer.anonymize(
    dicom_input_path,
    dicom_output_path,
    tag_to_keep
)
```
