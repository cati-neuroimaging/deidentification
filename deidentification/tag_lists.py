import csv

from deidentification import CONFIG_FOLDER

profile_path = CONFIG_FOLDER.joinpath('confidentiality_profiles.tsv')
conf_profile = {}
conf_profile_range = {}
with open(profile_path, 'r') as tsv_file:
    tsv_reader = csv.reader(tsv_file, delimiter='\t')
    for d in tsv_reader:
        if 'X' not in d[0]:
            conf_profile[eval(d[0])] = {'name': d[2], 'profile': d[1]}
        else:
            range_key = (
                eval(d[0].replace('X', '0')),
                eval(d[0].replace('X', 'F'))
            )
            conf_profile_range[range_key] = {'name': d[2], 'profile': d[1]}

safe_private_path = CONFIG_FOLDER.joinpath('safe_private.tsv')
safe_private_attributes = {}
with open(safe_private_path, 'r') as tsv_file:
    tsv_reader = csv.reader(tsv_file, delimiter='\t')
    header = next(tsv_reader)
    for d in tsv_reader:
        safe_private_attributes.setdefault(d[1], [])
        safe_private_attributes[d[1]].append(d[0])

# - X means the attribute must be removed
# - U means the attribute must be replaced with a cleaned but internally consistent UUID
# - D means replace with a non-zero length dummy value
# - Z means replace with a zero or non-zero length dummy value
# - C means the attribute can be kept if it is cleaned