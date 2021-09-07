from setuptools import find_packages, setup

# Select appropriate modules
modules = find_packages()

# Build the setup
setup(
    name='deidentification',
    description='CATI dicom deidentification tool',
    author='CATI team',
    author_email='support@cati-neuroimaging.com',
    version='0.1.0',
    packages=modules,
    install_requires=['pydicom'],
)
