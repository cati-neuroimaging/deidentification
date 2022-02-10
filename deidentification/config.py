import csv
import os

from deidentification import CONFIG_FOLDER, DeidentificationError


def tag_to_tuple(tag_str: str) -> tuple:
    tag = tag_str
    for char in '() ':
        tag = tag.replace(char, '')

    tag_tuple = tag.split(',')
    if len(tag_tuple) != 2:
        raise ValueError("Input tag '{}' must contains 2 elements".format(tag_str))
    
    try:
        tag_tuple = tuple(int(t, 16) for t in tag_tuple)
    except ValueError:
        raise ValueError("Input tag '{}' must contains hexadecimal values".format(tag_str))
    for tag in tag_tuple:
        if tag > 0xFFFF:
            raise ValueError("Input tag '{}' must contains values between '0x0000' and '0xFFFF'".format(tag_str))
    return tag_tuple


def load_config_profile(profile: str, anonymous: bool = False):
    profile_path = os.path.join(CONFIG_FOLDER, 'profiles', profile + '.tsv')
    if not os.path.exists(profile_path):
        raise DeidentificationError('Profile {} does not exists.'.format(profile))
    
    tag_load_error = ''
    try:
        with open(profile_path, 'r') as tsv_file:
            tsv_reader = csv.reader(tsv_file, delimiter='\t')
            _ = next(tsv_reader)  # header
            data = [tag_to_tuple(d[0]) for d in tsv_reader]
    except ValueError as e:
        if anonymous:
            tag_load_error = 'Error occurs during config profile load.'
        else:
            raise e
    if tag_load_error:
        raise DeidentificationError(tag_load_error)

    return data
    
    
# /!\ Siemens VIDA and CSA header ?
