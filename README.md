# deidentification

Tool to remove metadata allowing to identify a subject from DICOM images used in neuroimaging research. Can anonymize dicom files or archives of dicoms.
Deidentification is based on DICOM Standard deinfinition, based on Supplement 142. This Supplement has evolved among time, and this tool aims to use last version of this standard.

According to this standard :

- Public Tags are allowed except a list of identifying Tags
- Private Tags are removed except a list of safe Tags containing data about acquisition

This tool can be personnalized with deidentification profiles to force keeping some tags that could be removed by DICOM standard.

## Dependencies

- Python >= 3.6
- Pydicom >= 1.4.2

## Deidentification standard

According to DICOM standard public tags can be kept, except a list of tags that may contains indentifying data. Those tags are defined in _Confidentiality profile`

[DICOM attribute confidentiality Profiles](http://dicom.nema.org/medical/dicom/current/output/html/part15.html#chapter_E)

- X means the attribute must be removed
- U means the attribute must be replaced with a cleaned but internally consistent UUID
- D means replace with a non-zero length dummy value
- Z means replace with a zero or non-zero length dummy value
- C means the attribute can be kept if it is cleaned

| Tag | Action| Description |
| :---: | :---: | :---: |
| (0x0008,0x2111) | X | Derivation Description |
| (0x0008,0x2112) | X/Z/U* | Source Image Sequence |
| (0x0008,0x3010) | U | Irradiation Event UID |
| (0x0008,0x4000) | X | Identifying Comments |
| (0x0010,0x0010) | Z | Patient's Name |
| (0x0010,0x0020) | Z | Patient ID |
| (0x0010,0x0021) | X | Issuer of Patient ID |
| (0x0010,0x0030) | Z | Patient's Birth Date |
| (0x0010,0x0032) | X | Patient's Birth Time |
| ... | ... | ... |

In the other hand, private tags have to be deleted excepting a list of safe private tags that may only contains data acquisition information without identifying data.

| Data Element | Private Creator | Meaning |
| :---: | :---: | :--- |
| (0x2001,0x0003)| Philips Imaging DD 001 | MR Image Diffusion B-Factor |
| (0x2001,0x0004)| Philips Imaging DD 001 | MR Image Diffusion Direction |
| (0x2001,0x0005)| Philips Imaging DD 001 | Graphic Annotation Parent ID |
| (0x0019,0x000C)| SIEMENS MR HEADER | B Value |
| (0x0019,0x000D)| SIEMENS MR HEADER | Diffusion Directionality |
| (0x0019,0x000E)| SIEMENS MR HEADER | Diffusion Gradient Direction |
| (0x0019,0x0027)| SIEMENS MR HEADER | B Matrix |
| (0x0043,0x0039)| GEMS_PARM_01 | 1stvalue is B Value |
| ... | ... | ... |

## Deidentification profile

It is possible to personnalize deidentification tool using deidentification profiles. A profile is defined by a _.tsv_ file in the folder _deidentification/config/profiles/._ This file references all the DICOM tags to keep during deidentification, even if this tag have to be deleted/modified according to DICOM deidentification standard.

An exemple of deidentification profile :

| Tag | Name |
| :---: | :---: |
| (0018,1060) | Trigger Time |
| (0019,100C) | B Value |
| (0019,100A) | Number of slices |
| (0019,101E) | Display field of view |
| ... | ... |

Two deidentification profiles are already defined in deidentification module.

- `cati_collector` keeps some private tags about acquisition parameters and tags to help to identify acquisition. This profile is used internally by the CATI to deidentify data incoming from hospitals. **It is not a profile recommended to use in other case of deidentification** as identifying data could stay.
- `data_sharing` keeps some private tafs about acquisition parameters. Those tags came from the CATI experience about neuroimaging data, and are supposed to contains only non indentifying acquisition data.

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

dicom_input_path = '/path/to/dicom_input_file_or_foled'
dicom_output_path = '/path/to/dicom_output_file_or_folder'

anonymizer.anonymize(
    dicom_input_path,
    dicom_output_path,
)
```

## Improvements

- Take into account XA11 version
- What to do with CSA header ?
