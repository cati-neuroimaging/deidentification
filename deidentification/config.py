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
        if os.path.exists(profile):
            profile_path = profile
        else:
            raise DeidentificationError(f'Profile {profile} does not exists.')
    
    tag_load_error = ''
    try:
        with open(profile_path, 'r') as tsv_file:
            tsv_reader = csv.reader(tsv_file, delimiter='\t')
            _ = next(tsv_reader)  # header
            tags_profile = {}
            for d in tsv_reader:
                if len(d) <= 2 or not d[2]:
                    action = 'K'
                else:
                    action = d[2]
                tags_profile.setdefault(tag_to_tuple(d[0]), {}).update({'name': d[1], 'action': action})
                if len(d) > 3:
                    tags_profile[tag_to_tuple(d[0])].setdefault('private_creator', []).append(d[3])
    except ValueError as e:
        if anonymous:
            tag_load_error = 'Error occurs during config profile load.'
        else:
            raise e
    if tag_load_error:
        raise DeidentificationError(tag_load_error)

    return tags_profile
    
    
# /!\ Siemens VIDA and CSA header ?
