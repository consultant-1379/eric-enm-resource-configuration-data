'''
This file contains some reusable utilities for the project.
'''
import json
import logging
import tarfile
import os
import tempfile
import re
import shutil
import subprocess
from zipfile import ZipFile
from pathlib import Path
import requests
import rcd_exceptions
from requests.auth import HTTPBasicAuth

log = logging.getLogger(__name__)

def find(lst, key, value):
    '''
    This function finds the index of a key in a list of dicts.
    '''
    for idx, dic in enumerate(lst):
        if dic[key].startswith(value):
            return idx
    return -1


def find_all(lst, key, value):
    '''
    This function finds all the indexs of a key in a list of dicts.
    '''
    res = []
    for idx, dic in enumerate(lst):
        if dic[key] == value or dic[key].startswith(value + '-'):
            res.append(idx)
    return res


def read_json_file(json_path):
    '''
    This function reads a json file and returns a dictionary
    '''
    with open(json_path, encoding="ascii") as tmp_file:
        data = json.load(tmp_file)
    return data


def calculate_total(resource_list):
    '''
    This function counts the total amount of a given resource is required for enabled applications.
    '''
    return len([k for k in resource_list if k['app_enabled']])


def calculate_total_for_ip_version(ip_version, resources, resource_name):
    '''
    This function creates and counts the amount of a resource based on the user's chosen IP version
    '''
    resource_total = []
    if ip_version == 'dual' or (ip_version == 'ipv6' and resource_name == 'services'):
        return calculate_total(resources)
    for resource in resources:
        if ip_version == 'ipv6':
            if resource["name"].endswith('ipv6'):
                resource_total.append(resource)
        else:
            if not resource["name"].endswith('ipv6'):
                resource_total.append(resource)
    return calculate_total(resource_total)


def extract_files_from_archive(archive_file_path, file_to_extract_path,
                               target_directory=None, target_filename=None):
    """
    Extract the given files from the archive into a target directory.

    Input:
        archive_file_path: The archive to extract.
        file_to_extract_path: The file pattern to extract from the archive file.
        target_directory: The optional target directory for the extracted files.
        target_filename: The optional target filename for the extracted files.

    Output:
        A list of extracted files is returned.
    """
    with tempfile.TemporaryDirectory() as directory_name:
        temporary_target_directory = directory_name

    if not target_directory:
        target_directory = temporary_target_directory

    log.debug("Extracting file pattern '%s' from '%s' to '%s'",
              file_to_extract_path,
              archive_file_path,
              target_directory)
    archive_file_path_object = Path(archive_file_path)
    if archive_file_path_object.suffix in ['.tgz', '.tar']:
        archive_option_function = tarfile.open
    else:
        archive_option_function = ZipFile

    if not Path(target_directory).exists():
        Path(target_directory).mkdir(parents=True, exist_ok=True)
    with archive_option_function(archive_file_path, 'r') as archive_file_object:
        if archive_file_path_object.suffix in ['.tgz', '.tar']:
            archive_file_name_list = archive_file_object.getnames()
        else:
            archive_file_name_list = archive_file_object.namelist()

        list_of_extracted_files = []
        for file_path_in_archive in archive_file_name_list:
            if re.search(file_to_extract_path, file_path_in_archive):
                log.debug("Extracting file '%s'", file_path_in_archive)
                archive_file_object.extract(file_path_in_archive, temporary_target_directory)
                original_extracted_file_path = \
                    Path(temporary_target_directory) / Path(file_path_in_archive)

                if target_filename:
                    final_extracted_file_path = shutil.move(original_extracted_file_path,
                                                            target_directory / target_filename)
                else:
                    final_extracted_file_path = original_extracted_file_path
                list_of_extracted_files.append(str(final_extracted_file_path))

    if len(list_of_extracted_files) == 0:
        raise FileNotFoundError("Could not find the file pattern '" + file_to_extract_path +
                                "' in the given archive '" + archive_file_path_object.name + "'")

    return list_of_extracted_files


def extract_tar_file(tar_file, directory):
    """
    Extract a given tar into a given directory.

    Input:
        tar_file: tar file to extract
        directory: directory to extract the tar file to
    """
    with tarfile.open(tar_file) as tar:
        tar.extractall(directory)


# pylint: disable=too-many-arguments
def download_file(url, filename, username, password, file_write_type, timeout_in_s=600):
    """
    Download a given file using the url.

    Input:
        url: This is the full url to the file
        filename: This will be used as the name of the file once downloaded
        username: username if the url requires it
        password: password if the url requires it
        file_write_type: parameter for the open file command to state how to write the file,
                         e.g. wb (Open file binary mode)

    Output:
        File is downloaded
    """
    try:
        response = requests.get(url, auth=HTTPBasicAuth(username, password), timeout=timeout_in_s)
        response.raise_for_status()
        with open(filename, file_write_type) as output_file:
            output_file.write(response.content)
    except Exception:
        log.error("File download returned an error")
        raise rcd_exceptions.FileDownloadError("File download returned an error")


def run_cli_command(command_and_args_list, **subprocess_run_options):
    """
    Run the given cli command and arguments through pythons subprocess run, with the given options.

    Input:
        command_and_args_list: List of commands to execute
        **subprocess_run_options: Optional key/value parameters for subprocess call
    """
    log.debug('Adding all environment variables from the image, \
              to the subprocess.run env variables')

    if 'env' not in subprocess_run_options:
        subprocess_run_options['env'] = {}
    subprocess_run_options['env'] = {**subprocess_run_options['env'], **dict(os.environ.items())}
    log.debug('Running the following cli command: %s', ' '.join(command_and_args_list))
    # pylint: disable=subprocess-run-check
    return subprocess.run(command_and_args_list, **subprocess_run_options)


def check_path_in_dict(dictionary, path):
    """
    This function checks the path in dictionary
    """
    if not path:
        return True
    key = path[0]
    if key in dictionary:
        if len(path) == 1:
            return True
        if isinstance(dictionary[key], dict):
            return check_path_in_dict(dictionary[key], path[1:])
    return False


def remove_units_from_k8s_resource(resource_str):
    """
    This function removes units from k8s resource strings
    """
    # Regular expression pattern to match numbers with optional units.
    pattern = r'(\d+(\.\d+)?)([A-Za-z]+)?'

    # Search for matches in the input string.
    matches = re.match(pattern, resource_str)

    if matches:
        # Extract the numeric part (value) and the unit part.
        value = matches.group(1)
        unit = matches.group(3)

        # If the unit is not present, or it's a valid unit, return just the value.
        if unit is None or unit in ('m', 'M', 'mi', 'Mi', 'k', 'K', 'ki', 'Ki', 'G', 'Gi'):
            return value
    return resource_str


def gib_to_mib(resource_string):
    """
    This function converts the resource string from GiB units to MiB units
    """
    try:
        gib_value = int(remove_units_from_k8s_resource(resource_string))
        mib_value = gib_value * 1024  # Convert GiB to MiB
        return f"{mib_value}Mi"
    except (ValueError, IndexError):
        return "Invalid input format"
