"""Module for the manipulating optionality related files."""
import logging
from pathlib import Path
import os
import yaml

from utils import utils
from . import helmfile

LOG = logging.getLogger(__name__)

def generate_optionality_maximum(path_to_helmfile, releases_dict):
    """
    Generate an optionality maximum file, based on the provided helmfile and site values file.

    Args:
        path_to_helmfile: Path to the helmfile.yaml
        releases_dict: helm releases

    Returns:
        Writes updated yaml to state_values_file after enabling specified tags
    """
    LOG.debug("Starting generating the optionality maximum file.")

    optionality_dicts = get_optionality_dicts(path_to_helmfile=path_to_helmfile,
                                              releases_dict=releases_dict)

    merged_optionality_dicts = logical_or_merge_optionality_dicts(
        optionality_dicts=optionality_dicts)

    write_dict_to_yaml_file(yaml_file_path=Path(path_to_helmfile).parent /
                            'build-environment/optionality_maximum.yaml',
                            yaml_dict=merged_optionality_dicts)
    LOG.debug("Finished generating the optionality maximum file.")


def get_optionality_dicts(path_to_helmfile, releases_dict):
    """
    Return a list of optionality yaml dictionaries found in the helmfile and its dependencies.

    Args:
        path_to_helmfile: Path to the helmfile.yaml
        chart_cache_directory: the path to where the downloaded packages should be cached to/from

    Returns:
        Returns a list of optionality dictionaries from the downloaded dependencies
    """
    optionality_dicts = [get_helmfile_optionality(path_to_helmfile=path_to_helmfile)]
    username = os.environ.get('GERRIT_USERNAME', None)
    password = os.environ.get('GERRIT_PASSWORD', None)

    for _, release_info in releases_dict.items():
        if 'url' in release_info:
            app_name = release_info['name']
            app_version = release_info['version']
            app_repo = release_info['url']
            helm_chart_file_name = f"{app_name}-{app_version}.tgz"
            helm_chart_full_path = os.path.join(os.getcwd(), helm_chart_file_name)

            helmfile.download_helmfile(app_name,
                                       app_version,
                                       app_repo,
                                       username,
                                       password)

            try:
                extracted_optionality_yaml = utils.extract_files_from_archive(
                    archive_file_path=helm_chart_full_path,
                    file_to_extract_path='optionality.yaml')[0]

            except FileNotFoundError:
                extracted_optionality_yaml = None

            if extracted_optionality_yaml:
                LOG.debug("Loading the optionality.yaml found from %s", helm_chart_full_path)
                with open(str(extracted_optionality_yaml), "r", encoding='utf-8') as yaml_file:
                    optionality_dicts.append(yaml.safe_load(yaml_file))

    return optionality_dicts


def write_dict_to_yaml_file(yaml_file_path, yaml_dict):
    """
    Write a dict to a yaml file.

    Args:
        yaml_file_path: The file to write to.
        yaml_dict: The yaml object to write into the file.

    Returns:
        Writes the given dictionary to a yaml file
    """
    with open(yaml_file_path, 'w', encoding='utf-8') as yaml_file:
        yaml.dump(yaml_dict, yaml_file)


def logical_or_merge_optionality_dicts(optionality_dicts):
    """
    Merge the optionality dicts doing a logical or on the enabled key values.

    Args:
        optionality_dicts: A list of optionality dictionaries to merge.

    Returns:
        Returns a resulting optionality dictionary.
    """
    merged_optionality_dict = {}
    for optionality_dict in optionality_dicts:
        logical_or_extend_dict(extend_me=merged_optionality_dict, extend_by=optionality_dict)
    return merged_optionality_dict


def logical_or_extend_dict(extend_me, extend_by):
    """
    Merge the contents of a dictionary into an existing dictionary, recursively.

    Args:
        extend_me: Object to be extended.
        extend_by: Object to extend.

    Returns:
        Updates the given extend_me object
    """
    if isinstance(extend_me, dict):
        for key, value in extend_by.items():
            if key in extend_me:
                if value is True:
                    extend_me[key] = value
                else:
                    logical_or_extend_dict(extend_me=extend_me[key], extend_by=value)
            else:
                extend_me[key] = value
    else:
        extend_me += extend_by


def get_helmfile_optionality(path_to_helmfile):
    """
    Get the optionality.yaml file contents as a dict if present.

    Args:
        path_to_helmfile: Path to the helmfile.yaml

    Returns:
        Returns an optionality dictionary read from the base of the given helmfile.
    """
    try:
        with open(Path(path_to_helmfile).parent / 'optionality.yaml',
                  encoding='utf-8') as optionality_yaml_file:
            return yaml.safe_load(optionality_yaml_file)
    except FileNotFoundError:
        return {}
