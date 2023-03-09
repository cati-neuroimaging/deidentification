# /!\ Disclaimer:
# Use at your own risk. Please verify your anonymization results.
# This script is not guaranteed to be complete.
# In particular, the detection of burnt-in PHI is not managed.

import hashlib
import os
import shutil
from glob import glob
from tempfile import mkdtemp

import pydicom

import deidentification as deid
from deidentification import DeidentificationError, tag_lists
from deidentification.archive import (is_archive_ext, is_archive_file, pack,
                                      unpack, unpack_first)
from deidentification.config import load_config_profile


def _load_config(config_profile, tags_to_keep, tags_to_delete, anonymous):
    """Load config if no conflict with other params.

    Parameters
    ----------
    config_profile : str
    tags_to_keep : list
    tags_to_delete : list
    anonymous : bool

    Returns
    -------
    tags_to_keep : list
    tags_to_delete : list

    Raises
    ------
    DeidentificationError
        In case of config profile AND tags_to_keep/tags_to_delete defined
    """
    tags_config = {}
    if config_profile:
        if tags_to_keep or tags_to_delete:
            raise DeidentificationError('Both tags_to_keep/tags_to_delete and config_profile have been specified.')
        
        tags_config = load_config_profile(config_profile, anonymous)
    else:
        if tags_to_keep:
            tags_config.update({k: {'action': 'K'} for k in tags_to_keep})
        if tags_to_delete:
            tags_config.update({x: {'action': 'X'} for x in tags_to_delete})
    return tags_config


def anonymize_file(dicom_file_in, dicom_folder_out,
                   tags_to_keep=None,
                   tags_to_delete=None,
                   forced_values=None,
                   config_profile=None,
                   anonymous=False):
    """Configures the Anonymizer and runs it on a DICOM file

    Parameters
    ----------
    dicom_file_in : str
    dicom_folder_out : str
    tags_to_keep : list, optional
    tags_to_delete : list, optional
    forced_values : dict, optional
    config_profile : str, optional
    anonymous : bool, optional
    """
    if os.path.isfile(dicom_folder_out):
        raise DeidentificationError('The DICOM output has to be a folder.')
    
    tags_config = _load_config(config_profile, tags_to_keep,
                               tags_to_delete, anonymous)
    
    if not os.path.exists(dicom_folder_out):
        os.makedirs(dicom_folder_out)
    dicom_file_out = os.path.join(dicom_folder_out,
                                  os.path.basename(dicom_file_in))

    # Only keep filename in case of config_profile path
    if config_profile:
        profile_name = os.path.basename(config_profile).rsplit('.', 1)[0]
    else:
        profile_name = config_profile
    
    anon = Anonymizer(dicom_file_in, dicom_file_out,
                      tags_config, forced_values,
                      anonymous=anonymous,
                      config_profile=profile_name)
    anon.run_ano()


def anonymize(dicom_in, dicom_out,
              tags_to_keep=None,
              tags_to_delete=None,
              forced_values=None,
              config_profile=None,
              anonymous=False,
              tempdir_prefix=None):
    """Configures the Anonymizer and runs it on DICOM files. It can configured using tags_to_keep
    or config_profile, and forced_values (ex: {(0x0010, 0x0010) : 'XXXX')})
    
    Parameters
    ----------
    dicom_in : str
        Path of DICOM to deidentify. Can be archive, folder or file.
    dicom_out : str
        Path where to save deidentified DICOM. Can be archive or folder.
    tags_to_keep : list, optional
    tags_to_delete : list, optional
    forced_values : dict, optional
    config_profile : str, optional
    anonymous : bool, optional
    tempdir_prefix : str, optional
    """
    if not os.path.exists(dicom_in):
        raise DeidentificationError('The DICOM input does not exists.')
    if not os.path.isfile(dicom_in) and not os.path.isdir(dicom_in):
        raise DeidentificationError('The DICOM input file type is not handled by this tool.')
    if not os.path.isfile(dicom_in) and os.path.isfile(dicom_out):
        raise DeidentificationError('The DICOM out could not be a file if DICOM in is not a file.')

    _ = _load_config(config_profile, tags_to_keep,
                     tags_to_delete, anonymous)

    # Handle archives
    is_dicom_in_archive = is_archive_file(dicom_in)
    is_dicom_out_archive = is_archive_ext(dicom_out)
    if is_dicom_in_archive:
        wip_dicom_in = mkdtemp(prefix=tempdir_prefix)
        try:
            unpack(dicom_in, wip_dicom_in)
        except Exception:
            shutil.rmtree(wip_dicom_in)
            raise DeidentificationError('Unpacking compressed file failed.')
    else:
        wip_dicom_in = os.path.abspath(dicom_in)
    if is_dicom_out_archive:
        wip_dicom_out = mkdtemp(prefix=tempdir_prefix)
    else:
        wip_dicom_out = os.path.abspath(dicom_out)

    # Launch deidentification
    try:
        if os.path.isfile(wip_dicom_in):
            anonymize_file(wip_dicom_in, wip_dicom_out,
                           tags_to_keep, tags_to_delete,
                           forced_values=forced_values,
                           anonymous=anonymous,
                           config_profile=config_profile)

        elif os.path.isdir(wip_dicom_in):
            for root, dirs, files in os.walk(wip_dicom_in):
                folder_out = root.replace(wip_dicom_in, wip_dicom_out)
                for name in files:
                    current_file = os.path.join(root, name)
                    anonymize_file(current_file, folder_out,
                                   tags_to_keep, tags_to_delete,
                                   forced_values=forced_values,
                                   anonymous=anonymous,
                                   config_profile=config_profile)
    except Exception as e:
        if is_dicom_out_archive and os.path.exists(wip_dicom_out):
            shutil.rmtree(wip_dicom_out)
        raise e
    finally:
        if is_dicom_in_archive and os.path.exists(wip_dicom_in):
            shutil.rmtree(wip_dicom_in)
    
    if is_dicom_out_archive:
        try:
            pack(os.path.abspath(dicom_out),
                 glob(os.path.join(wip_dicom_out, '*')))
        except Exception:
            raise DeidentificationError('Compress deidentification results failed.')
        finally:
            shutil.rmtree(wip_dicom_out)


def check_anonymize_fast(dicom_in,
                         tags_to_keep=None,
                         tags_to_delete=None,
                         forced_values=None,
                         config_profile=None,
                         anonymous=False,
                         tempdir_prefix=None):
    """
    Configures the Anonymizer and runs it on one DICOM file to check if anonymization already done.
    """
        
    if not os.path.exists(dicom_in):
        raise DeidentificationError('The DICOM input does not exists.')

    tags_config = _load_config(config_profile, tags_to_keep,
                               tags_to_delete, anonymous)
    
    dicom_tmp = ''
    if is_archive_file(dicom_in):
        dicom_tmp = mkdtemp(prefix=tempdir_prefix)
        try:
            wip_dicom_in = unpack_first(dicom_in, dicom_tmp)
        except Exception:
            shutil.rmtree(dicom_tmp)
            raise DeidentificationError('Unpacking compressed file failed.')
    elif os.path.isfile(dicom_in):
        wip_dicom_in = dicom_in
    elif os.path.isdir(dicom_in):
        items_in_folder = glob.glob(os.path.join(dicom_in, '*'))
        wip_dicom_in = next(filter(os.path.isfile, items_in_folder), '')
    else:
        raise DeidentificationError('File input type is not handled by this tool.')
        
    if os.path.isfile(wip_dicom_in):
        try:
            anon = Anonymizer(wip_dicom_in, '',
                              tags_config, forced_values,
                              anonymous=anonymous)
            anon.runCheck()
            return anon.result
        finally:
            if dicom_tmp and os.path.exists(dicom_tmp):
                shutil.rmtree(dicom_tmp)
    else:
        raise DeidentificationError('File input type is not handled by this tool.')
    

def check_anonymize(dicom_in,
                    tags_to_keep=None,
                    tags_to_delete=None,
                    forced_values=None,
                    config_profile=None,
                    anonymous=False,
                    tempdir_prefix=None):
    """
    Check if dicom_in is an anonymized DICOM.
    Input can be DICOM file/folder or archive of DICOM files/folder
    """
    if not os.path.exists(dicom_in):
        raise DeidentificationError('The DICOM input does not exists.')

    tags_config = _load_config(config_profile, tags_to_keep,
                               tags_to_delete, anonymous)
    
    is_archive_in = is_archive_file(dicom_in)
    if is_archive_in:
        wip_dicom_in = mkdtemp(prefix=tempdir_prefix)
        try:
            unpack(dicom_in, wip_dicom_in)
        except Exception:
            shutil.rmtree(wip_dicom_in)
            raise DeidentificationError('Unpacking compressed file failed.')
    else:
        wip_dicom_in = dicom_in
        
    if os.path.isfile(wip_dicom_in):
        try:
            anon = Anonymizer(wip_dicom_in, '',
                              tags_config, forced_values,
                              anonymous=anonymous)
            anon.runCheck()
            return anon.result
        finally:
            if is_archive_in and os.path.exists(wip_dicom_in):
                shutil.rmtree(wip_dicom_in)
        
    elif os.path.isdir(wip_dicom_in):
        return check_folder_anonymize(wip_dicom_in,
                                      forced_values=forced_values,
                                      config_profile=config_profile)
    
    else:
        raise DeidentificationError('File input type is not handled by this tool.')
        

def check_folder_anonymize(dicom_folder,
                           tags_to_keep=None,
                           tags_to_delete=None,
                           forced_values=None,
                           config_profile=None,
                           anonymous=False):
    """Check deidentification for all files in the input folder.
    All the files in the folder have to be DICOM files.

    Parameters
    ----------
    dicom_folder : str
    tags_to_keep : list, optional
    tags_to_delete : list, optional
    forced_values : dict, optional
    config_profile : str, optional
    anonymous : bool, optional

    Returns
    -------
    bool
    """
    if not os.path.isdir(dicom_folder):
        raise DeidentificationError('DICOM folder input is not a folder path.')

    tags_config = _load_config(config_profile, tags_to_keep,
                               tags_to_delete, anonymous)
    
    for root, dirs, files in os.walk(dicom_folder):
        for filename in files:
            anon = Anonymizer(os.path.join(root, filename), '',
                              tags_config, forced_values,
                              anonymous=anonymous)
            anon.runCheck()
            if not anon.result:
                return False
    return True


class AnonymizerError(DeidentificationError):
    def __init__(self, message='', complement='', anonymous=False):
        self.message = message
        self.complement = complement
        self.anonymous = anonymous
        
    def __str__(self):
        if self.anonymous:
            return self.message.format('')
        return self.message.format(self.complement)


class Anonymizer():

    """
    Anonymizes a DICOM file according to DICOM standard.
    """

    def __init__(self, dicom_filein, dicom_fileout,
                 tags_config=None,
                 forced_values=None, config_profile=None,
                 anonymous=False):
        """
        dicom_filein: the DICOM file to anonymize
        dicom_fileout: the file to write the output of the anonymization
        tags_config: a dict with action to do on tags (keep ('K'), remove ('X'), ...)
        forced_values: a dictionary constructed as shown here: {(0x0010,0x0010): "My forced patient name"}
        When a tag is in forced_values, it will be kept whether or not in tags_to_keep.
        """
        self._dicom_filein = dicom_filein
        self._dicom_fileout = dicom_fileout
        self._tags_config = tags_config
        self._forced_values = forced_values
        self.anonymous = anonymous
        self.config_profile = config_profile

        self.originalDict = {}
        self.outputDict = {}
        self._dataset = self._load_dataset()
        self.result = None
        self.ano_run = False

    def run_ano(self):
        """
        Reads the DICOM file, anonymizes it and write the result.
        """
        if not self.ano_run:
            self._dataset.walk(self._anonymize_check)
        
        # Patient Identity Removed
        self._dataset.add_new((0x0012, 0x0062), 'CS', 'YES')
        # De-identification Method
        method = f'CATI DEIDENTIFICATION - {deid.__version__}'
        if self.config_profile:
            method += f' - {self.config_profile}'
        self._dataset.add_new((0x0012, 0x0063), 'LO', method)

        pydicom.write_file(self._dicom_fileout, self._dataset)
        return 1
    
    def runCheck(self):
        """
        Check anonymization.
        """
        if not self.ano_run:
            self._dataset.walk(self._anonymize_check)

        self.result = self.originalDict == self.outputDict
        return self.result

    def _load_dataset(self):
        try:
            ds = pydicom.read_file(self._dicom_filein)
            meta_data = pydicom.filereader.read_file_meta_info(self._dicom_filein)
            if (meta_data.get((0x0002, 0x0002)) and
                    meta_data.get((0x0002, 0x0002)).value == "Media Storage Directory Storage"):
                raise AnonymizerError('The file is a DICOMDIR. {}', self._dicom_filein, self.anonymous)
        except Exception:
            raise AnonymizerError('The file is not a DICOM file. {}', self._dicom_filein, self.anonymous)
        return ds

    def _anonymize_check(self, ds, data_element):
        """
        Check anonymization on a single DICOM element.
        ds: the DICOM descriptor
        data_element: the current element to anonymize
        """
        group = data_element.tag.group
        element = data_element.tag.element
        tag = (group, element)
        
        # Check if the value must be forced
        if self._forced_values is not None and tag in self._forced_values:
            self.originalDict[data_element.tag] = data_element.value
            data_element.value = self._forced_values[tag]
            self.outputDict[data_element.tag] = self._forced_values[tag]
            return

        # Check if the data element has to be kept
        if self._tags_config is not None and tag in self._tags_config:
            do_apply_action = True
            # In case of private tag, check if private creator and check its value
            if (data_element.tag.is_private
                    and self._tags_config[tag].get('private_creator')
                    and not self._is_private_creator(data_element.tag.group, data_element.tag.element)):
                private_creator = ds.get(self._get_private_creator_tag(data_element), None)
                if not private_creator or private_creator.value not in self._tags_config[tag].get('private_creator'):
                    do_apply_action = False
            if do_apply_action:
                action = self._tags_config[tag]['action']
                self._apply_action(ds, data_element, action)
                return
        
        # Check if the data element is in the DICOM part 15/annex E tag list
        action = self._find_in_conf_profile(group, element)
        if action:
            self._apply_action(ds, data_element, action)
        
        # Check if the data element is private
        elif data_element.tag.is_private:
            if self._is_private_creator(group, element):
                self.originalDict[data_element.tag] = data_element.value
                self.outputDict[data_element.tag] = data_element.value
                return
            private_creator = ds.get(self._get_private_creator_tag(data_element), None)
            if not private_creator:
                del ds[data_element.tag]
                return
            private_creator_value = private_creator.value
            private_creator_tag = (private_creator.tag.group, private_creator.tag.element)
            # Check if private creator in tag_config
            if (self._tags_config is not None
                    and private_creator_tag in self._tags_config
                    and private_creator.value in self._tags_config[private_creator_tag]['private_creator']):
                self._apply_action(ds, data_element, self._tags_config[private_creator_tag]['action'])
                return
            # Check if the private creator is in the safe private attribute keys
            if private_creator_value not in list(tag_lists.safe_private_attributes.keys()):
                self.originalDict[data_element.tag] = data_element.value
                del ds[data_element.tag]
                return
            block = element & 0x00ff
            # Check if the data element is in the safe private attributes list
            if (group, block) not in tag_lists.safe_private_attributes[private_creator_value]:
                self.originalDict[data_element.tag] = data_element.value
                del ds[data_element.tag]
        # else:
            # self.originalDict[data_element.tag] = data_element.value
            # self.outputDict[data_element.tag] = data_element.value
                
    def _find_in_conf_profile(self, group: int, element: int) -> str:
        """
        Find (group, element) in confidentiality profiles and return action expected if found.
        """
        if (group, element) in tag_lists.conf_profile:
            return tag_lists.conf_profile[(group, element)]['profile'][0]
        
        for tag_range in tag_lists.conf_profile_range:
            (group_min, element_min), (group_max, element_max) = tag_range
            if group_min <= group <= group_max and element_min <= element <= element_max:
                return tag_lists.conf_profile_range[tag_range]['profile'][0]
        
        return ''
    
    def _apply_action(self, ds, data_element, action):
        """
        Apply confidentiality profiles action to data_element of ds
        - X means remove
        - U means replace with a cleaned but internally consistent UUID
        - D means replace with a non-zero length dummy value
        - Z means replace with a zero or non-zero length dummy value
        - K means keep

        Parameters
        ----------
        ds : pydicom.dataset.Dataset
        data_element : pydicom.dataelem.DataElement
        action : str
        """
        if action == 'X':
            self.originalDict[data_element.tag] = data_element.value
            del ds[data_element.tag]
        elif action == 'Z':
            self.originalDict[data_element.tag] = data_element.value
            data_element.value = ""
            self.outputDict[data_element.tag] = data_element.value
        elif action == 'D':
            self.originalDict[data_element.tag] = data_element.value
            data_element.value = self._get_cleaned_value(data_element)
            self.outputDict[data_element.tag] = data_element.value
        elif action == 'U':
            data_element.value = self._generate_uuid(data_element.value.encode())
        elif action == 'K':
            self.originalDict[data_element.tag] = data_element.value
            self.outputDict[data_element.tag] = data_element.value
        else:
            raise DeidentificationError(f'Action not recognized: {action}')

    def _generate_uuid(self, input):
        """
        Returns an UUID according to input.
        """
        return hashlib.md5(input).hexdigest()

    def _get_cleaned_value(self, data_element):
        """
        Gets a cleaned value of data_element value according to its representation.
        """
        if data_element.VR == 'UI':
            return self._generate_uuid(data_element.value)
        if data_element.VR == 'DA':
            return "19700101"
        if data_element.VR == 'TM':
            return "000000.00"
        if data_element.VR == 'DT':
            return "19700101000000.00"
        return "no value"

    def _is_private_creator(self, group, element):
        """
        Returns true if the (group, element) tag is a private creator and false otherwise.
        """
        return group % 2 != 0 and \
            element > 0x0000 and element < 0x00ff

    def _get_private_creator_tag(self, data_element):
        """
        Gets the private creator tag of data_element.
        """
        if self._is_private_creator(data_element.tag.group, data_element.tag.element):
            return data_element.tag
        group = data_element.tag.group
        element = (data_element.tag.element & 0xff00) >> 8
        return pydicom.tag.Tag(group, element)
