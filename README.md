# deidentification

[![Python tests](https://github.com/cati-neuroimaging/deidentification/actions/workflows/python-package.yml/badge.svg)](https://github.com/cati-neuroimaging/deidentification/actions/workflows/python-package.yml)

Tool to remove metadata allowing to directly identify a subject from DICOM images used in neuroimaging research. Can anonymize DICOM files or archives of DICOM files.
Deidentification is based on the last version of [Supplement 142](ftp://medical.nema.org/medical/dicom/final/sup142_ft.pdf) of the DICOM standard.

According to this standard:

- Public Tags are allowed except a list of identifying Tags
- Private Tags are removed except a list of safe Tags containing data about acquisition

This tool can be personnalized with deidentification profiles to force keeping some tags that could be removed by DICOM standard.

## Dependencies

- Python >= 3.6
- Pydicom >= 1.4.2

## Deidentification standard

According to DICOM standard, public tags can be kept, except a list of tags that may contain identifying data. Those tags are defined in
[Attribute Confidentiality Profiles](http://dicom.nema.org/medical/dicom/current/output/html/part15.html#chapter_E).

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

On the other hand, private tags must be deleted, except a list of safe private tags that may only contain data acquisition information without directly identifying data.

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

It is possible to personnalize the deidentification tool using deidentification profiles. A profile is defined by a `.tsv` file in folder `deidentification/config/profiles/`. This file references actions to be done on DICOM tags, teh same as the actions defined in the DICOM standard ([De-identification Action Codes](https://dicom.nema.org/medical/dicom/current/output/html/part15.html#table_E.1-1a), ex: 'X' -> remove, 'K' -> keep).

In case of private tag, it is **highly recommended** to add the corresponding private creator value, which will be checked during deidentification. (To learn more about private creator tags: [Private Data Elements](https://dicom.nema.org/dicom/2013/output/chtml/part05/sect_7.8.html))

If tag referenced in profile corresponds to a private creator tag (with its value in *private creator* column), deidentification will keep all the block of element corresponding.

Those rules override rules defined in the DICOM standard.

An example of deidentification profile:

| Tag | Name | Action | Private Creator |
| :---: | :---: | :---: | :---: |
| (0008,0104) | Code Meaning | X | |
| (0018,1060) | Trigger Time | K | |
| (0019,100C) | B Value | K | SIEMENS MR HEADER |
| (0019,100A) | Number of slices | K | SIEMENS MR HEADER |
| (0019,101E) | Display field of view | K | GEMS_ACQU_01 |
| ... | ... | ... | ... |

Two deidentification profiles are already defined in deidentification module.

- `cati_collector` keeps some private tags about acquisition parameters and tags to help to identify acquisition. This profile is used internally by the CATI to deidentify data incoming from hospitals. **It is not a profile recommended to use in other case of deidentification** as identifying data could stay.
- `data_sharing` keeps some private tags about acquisition parameters. Those tags came from the CATI experience about neuroimaging data, and are supposed to contains only non-identifying acquisition data.

## How to use it?

### As a script

Launch anon_example.py to anonymize a dicom file.

Without subject id (set as "Unknown" by default):

```sh
deidentification -in myInputFolder -out myOutputFolder
```

With a subject id and configuration profile:

```sh
deidentification -in myInputFolder -out myOutputFolder -id 0001XXXX -c data_sharing
```

### As a Python module

```python
from deidentification import anonymizer

dicom_input_path = '/path/to/dicom_input_file_or_folder'
dicom_output_path = '/path/to/dicom_output_file_or_folder'

# Basic usage
anonymizer.anonymize(
    dicom_input_path,
    dicom_output_path,
)

# With more parameters
anonymizer.anonymize(
    dicom_input_path,
    dicom_output_path,
    forced_value={(0x0010, 0x0010): '0001XXXX'},
    config_profile='data_sharing'
)
```

## Improvements

- Take into account XA11 version
- What to do with CSA header ?
