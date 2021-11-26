import csv
import os

from deidentification import CONFIG_FOLDER


def tag_to_tuple(tag_str: str) -> tuple:
    tag = tag_str
    for char in '() ':
        tag = tag.replace(char, '')

    tag_tuple = tag.split(',')
    if len(tag_tuple) != 2:
        raise AttributeError("Input tag '{}' must contains 2 elements".format(tag_str))
    
    tag_tuple = tuple(eval('0x' + t) for t in tag_tuple)
    return tag_tuple


def load_config_profile(profile: str):
    profile_path = os.path.join(CONFIG_FOLDER, 'profiles', profile + '.tsv')
    if not os.path.exists(profile_path):
        raise AttributeError('Profile {} does not exists.'.format(profile))
    
    with open(profile_path, 'r') as tsv_file:
        tsv_reader = csv.reader(tsv_file, delimiter='\t')
        _ = next(tsv_reader)  # header
        data = [tag_to_tuple(d[0]) for d in tsv_reader]

    return data
    
    
# Dicom tag to keep
tags_to_keep = [
    (0x0008, 0x0020),  # Study Date
    (0x0008, 0x0031),  # Series Time
    (0x0008, 0x0032),  # Acquisition Time
    (0x0008, 0x0033),  # Content Time
    (0x0008, 0x103E),  # Series Description
    (0x0010, 0x0010),  # Patient's Name
    (0x0018, 0x1060),  # Trigger Time
    (0x0019, 0x100A),  #
    (0x0019, 0x100C),  #
    (0x0019, 0x101E),  #
    (0x0019, 0x105A),  #
    (0x0019, 0x107E),  #
    (0x0019, 0x109F),  #
    (0x0019, 0x10bb),  #
    (0x0019, 0x10bc),  #
    (0x0019, 0x10bd),  #
    (0x0021, 0x105A),  #
    (0x0021, 0x105E),  #
    (0x0025, 0x1007),  #
    (0x0025, 0x101B),  #
    (0x0027, 0x1060),  #
    (0x0043, 0x102A),  #
    (0x0043, 0x102C),  #
    (0x0043, 0x102F),  #
    (0x0043, 0x1039),  #
    (0x0051, 0x100A),  #
    (0x0051, 0x100B),  #
    (0x0051, 0x100C),  #
    (0x0051, 0x100E),  #
    (0x0051, 0x100F),  #
    (0x0051, 0x1011),  #
    (0x0051, 0x1016),  #
    (0x2001, 0x1003),  #
    (0x2001, 0x100B),  #
    (0x2001, 0x1013),  #
    (0x2001, 0x1014),  #
    (0x2001, 0x1018),  #
    (0x2001, 0x1020),  #
    (0x2001, 0x101B),  #
    (0x2001, 0x1081),  #
    (0x2005, 0x101D),  #
    (0x2005, 0x1074),  #
    (0x2005, 0x1075),  #
    (0x2005, 0x1076),  #
    (0x2005, 0x10A1),  #
    (0x2005, 0x10A9),  #
    (0x2005, 0x1013),  #
]

# /!\ Siemens VIDA and CSA header ?

# To force anonymization of patient Name into patient ID
forced_values = {(0x0010, 0x0010): 'xxxxx'}
