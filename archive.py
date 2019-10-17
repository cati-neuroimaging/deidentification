# -*- coding: utf-8 -*-
import tarfile
import zipfile
import os


def is_archive(filename):
    """
    Returns true if filename is an archive and false otherwise.
    """
    if zipfile.is_zipfile(filename):
        return True
    else:
        try:
            tarfile.open(filename)
            return True
        except:
            pass
    if os.path.splitext(filename)[1] in get_archive_extensions():
        return True
    return False


def get_archive_extensions():
    return ['.zip', '.gz', '.tar', '.bz2', '.tgz']


def unpack(input_filename, extract_dir):
    """
    Unpacks the input_filename archive to the extract_dir directory.
    """
    if zipfile.is_zipfile(input_filename):
        unzip(input_filename, extract_dir)
    else:
        untar(input_filename, extract_dir)


def pack(output_filename, sources):
    """
    Packs the source_dir directory in the output_filename archive.
    """
    ext = os.path.splitext(output_filename)[1][1:]
    if ext == 'zip':
        pack_zip(output_filename, sources)
    elif ext == 'gz' or ext == 'tgz' or ext == 'bz2' or ext == 'tar':
        pack_tar(output_filename, sources, ext)


def untar(input_filename, extract_dir):
    """
    Extracts the input_filename archive to the extract_dir directory.
    """
    try:
        tar_ds = tarfile.open(input_filename)
    except tarfile.TarError:
        raise "%s is not a tar file" % (input_filename)
    tar_ds.extractall(path=extract_dir)
    tar_ds.close()


def unzip(input_filename, extract_dir):
    """
    Extracts the input_filename archive to the extract_dir directory.
    """
    if not zipfile.is_zipfile(input_filename):
        raise "%s is not a zip file" % (input_filename)
    zip_ds = zipfile.ZipFile(input_filename)
    zip_ds.extractall(path=extract_dir)
    zip_ds.close()


def pack_tar(output_filename, sources, type='gz'):
    """
    Creates a tar archive in output_filename from the source_dir directory.
    """
    if type == 'tgz':
        type = 'gz'
    elif type == 'tar':
        type = ''
    tar_ds = tarfile.open(output_filename, 'w:' + type)
    if not isinstance(sources, (list, tuple)) and \
       isinstance(sources, str):
        sources = [sources]
    for source in sources:
        tar_ds.add(source, arcname=os.path.basename(source))
    tar_ds.close()


def pack_zip(output_filename, sources):
    """
    Creates a zip archive in output_filename from the source_dir directory.
    """
    previous_dir = os.getcwd()
    if not isinstance(sources, (list, tuple)) and \
       isinstance(sources, str):
        sources = [sources]
    zip_ds = zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED)
    for source in sources:
        os.chdir(os.path.dirname(source))
        if os.path.isdir(source):
            for root, dirs, files in os.walk(os.path.basename(source)):
                for file in files:
                    zip_ds.write(os.path.join(root, file))
        else:
            zip_ds.write(os.path.basename(source))
    zip_ds.close()
    os.chdir(previous_dir)
