from setuptools import find_packages, setup
import deidentification

# Select appropriate modules
modules = find_packages()

# Build the setup
setup(
    name='deidentification',
    description='CATI dicom deidentification tool',
    author='CATI team',
    author_email='support@cati-neuroimaging.com',
    version=deidentification.__version__,
    script=['bin/deidentification'],
    packages=modules,
    install_requires=['pydicom'],
)
