import csv

from deidentification import CONFIG_FOLDER
from deidentification.config import tag_to_tuple

conf_profile_path = CONFIG_FOLDER.joinpath('confidentiality_profiles.tsv')
conf_profile = {}
conf_profile_range = {}
with open(conf_profile_path) as tsv_file:
    tsv_reader = csv.reader(tsv_file, delimiter='\t')
    header = next(tsv_reader)
    for d in tsv_reader:
        if 'X' not in d[0]:
            conf_profile[tag_to_tuple(d[0])] = {'name': d[2], 'profile': d[1]}
        else:
            range_key = (
                tag_to_tuple(d[0].replace('X', '0')),
                tag_to_tuple(d[0].replace('X', 'F'))
            )
            conf_profile_range[range_key] = {'name': d[2], 'profile': d[1]}

safe_private_path = CONFIG_FOLDER.joinpath('safe_private.tsv')
safe_private_attributes = {}
with open(safe_private_path) as tsv_file:
    tsv_reader = csv.reader(tsv_file, delimiter='\t')
    header = next(tsv_reader)
    for d in tsv_reader:
        safe_private_attributes.setdefault(d[1], [])
        safe_private_attributes[d[1]].append(tag_to_tuple(d[0]))
