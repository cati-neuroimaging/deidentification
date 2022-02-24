version_major = 1
version_minor = 0
version_micro = 0
version_extra = ''

__version__ = f'{version_major}.{version_minor}.{version_micro}{version_extra}'

# Main setup parameters
NAME = 'deidentification'
DESCRIPTION = 'CATI dicom deidentification tool'
PROJECT = 'deidentification'
ORGANISATION = 'CATI'
AUTHOR = 'CATI'
LICENSE = 'MIT License'
AUTHOR_EMAIL = 'support@cati-neuroimaging.com'
VERSION = __version__
REQUIRES = ['pydicom']

brainvisa_build_model = 'pure_python'
