import os
from setuptools import find_packages, setup

# Select appropriate modules
modules = find_packages()

release_info = locals()
info_path = os.path.join(os.path.dirname(__file__), 'deidentification', 'info.py')
with open(info_path) as info_file:
    exec(info_file.read(), globals(), release_info)

# Build the setup
setup(
    name=release_info['NAME'],
    description=release_info['DESCRIPTION'],
    author=release_info['AUTHOR'],
    author_email=release_info['AUTHOR_EMAIL'],
    version=release_info['VERSION'],
    scripts=['bin/deidentification', 'bin/dicom_tag_diff'],
    packages=modules,
    install_requires=release_info['REQUIRES'],
    package_data={
        '': ['config/*.tsv', 'config/profiles/*.tsv'],
    },
)
