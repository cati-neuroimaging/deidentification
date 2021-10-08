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
    if not is_archive(input_filename):
        raise AttributeError("Input_filename must be an archive (ex: .tar.gz, .zip)")
    if zipfile.is_zipfile(input_filename):
        unzip(input_filename, extract_dir)
    else:
        untar(input_filename, extract_dir)


def unpack_first(input_filename: str, extract_dir: str) -> str:
    """
    Unpacks the first file in input_filename archive to the extract_dir directory.
    """
    if not is_archive(input_filename):
        raise AttributeError("Input_filename must be an archive (ex: .tar.gz, .zip)")
    if zipfile.is_zipfile(input_filename):
        return unzip_first(input_filename, extract_dir)
    else:
        return untar_first(input_filename, extract_dir)


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


def untar_first(input_filename: str, extract_dir: str) -> str:
    """
    Extracts the first file in an archive file and return filepath extracted.
    """
    with tarfile.open(input_filename) as tar_data:
        file_to_extract = tar_data.next()
        while file_to_extract is not None and not file_to_extract.isfile():
            file_to_extract = tar_data.next()
            
        if file_to_extract is None:
            print(f'No file found in archive {input_filename}')
            res = ''
        else:
            tar_data.extract(file_to_extract, path=extract_dir)
            res = os.path.join(extract_dir, file_to_extract.name)
    return res


def unzip(input_filename, extract_dir):
    """
    Extracts the input_filename archive to the extract_dir directory.
    """
    if not zipfile.is_zipfile(input_filename):
        raise "%s is not a zip file" % (input_filename)
    zip_ds = zipfile.ZipFile(input_filename)
    zip_ds.extractall(path=extract_dir)
    zip_ds.close()


def unzip_first(input_filename: str, extract_dir: str) -> str:
    """
    Extracts the first file in a zip file and return filepath extracted.
    """
    with zipfile.ZipFile(input_filename) as zip_file:
        zip_file_list = zip_file.infolist()
        zip_index = 0
        while zip_index < len(zip_file_list) and zip_file_list[zip_index].is_dir():
            zip_index += 1
        if zip_index == len(zip_file_list):
            res = ''
        else:
            file_to_extract = zip_file_list[zip_index]
            zip_file.extract(file_to_extract, extract_dir)
            res = os.path.join(extract_dir, file_to_extract.filename)
    return res
        

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
