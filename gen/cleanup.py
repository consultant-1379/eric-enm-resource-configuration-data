'''
This module performs Cleanup of intermediate product set files i.e. other than release candidates.
'''
import fnmatch
import json
import logging
import os
import traceback
from model.config import Config
from model.version import Version
from generator import read_config_file, CONFIG_YAML_PATH


log= logging.getLogger('app')
FILE= 'file'
JSON_EXTENSION= '.json'
INDEX_JSON_STR= 'index.json'
ENCODING_ASCII= "ascii"
EIC='EIC'


def load_pdu_cu_versions(index_json_data):
    '''
        Returns pdu and cu versions from index.json file
    '''
    versions = []
    for variant in index_json_data:
        if variant['offering'] != EIC:
            versions.extend(variant['versions'][:])
    pdu_versions = set(map(lambda version_record: version_record[FILE],
                         filter(lambda versions_record: versions_record['targetAudience'] == 'pdu'
                         , versions)))
    cu_versions = set(map(lambda version_record: version_record[FILE],
                        filter(lambda versions_record: versions_record['targetAudience'] == 'cu'
                        , versions)))
    return pdu_versions, cu_versions


def get_pdu_versions_older_than_release_version(index_json_data, product_set):
    '''
    Returns pdu versions that are older than the "version"
    or latest cu version available in index.json.
    '''
    pdu_versions, cu_versions = load_pdu_cu_versions(index_json_data)
    pdu_version_files_other_than_cu = pdu_versions - cu_versions
    return list(filter(lambda x: x != product_set and Version.parse(x) < Version.parse(product_set),
                       pdu_version_files_other_than_cu))


def delete_file(file_name):
    '''
    Delete a given file.
    '''
    try:
        log.info('Deleting file: %s', file_name)
        os.remove(file_name)
    except (FileNotFoundError, OSError):
        log.error('Exception occured while deleting file: %s', file_name)
        log.error(traceback.print_exc())


def delete_intermediate_ps_files(folder_path, index_json_data, file_extension):
    '''
    Delete intermediate product set files.
    '''
    for variant in index_json_data:
        datapath = variant["datapath"]
        files_in_index_json = list(
            map(lambda version: version[FILE] + file_extension, variant['versions']))
        files = fnmatch.filter(
            os.listdir(os.path.join(folder_path, datapath)), '*' + file_extension)
        for file in files:
            if file not in files_in_index_json:
                delete_file(os.path.join(folder_path, datapath, file))


def update_index_json(index_json_data, folder_path):
    '''
    Updates the index json file with the index json data.
    '''
    with open(os.path.join(folder_path, INDEX_JSON_STR),
                'w', encoding=ENCODING_ASCII) as index_json:
        json.dump(index_json_data, index_json, indent=2)


def update_index_json_and_del_intermediate_ps(folder_path, product_sets_to_delete, index_json_data):
    '''
    Iterates over index json data and delete product set files
    that are present in product_sets_to_delete list and updates the index json file.
    '''
    for variant in index_json_data:
        versions = variant['versions']
        for version in versions[:]:
            if version[FILE] in product_sets_to_delete:
                versions.remove(version)
    update_index_json(index_json_data, folder_path)
    delete_intermediate_ps_files(folder_path, index_json_data, '.json')
    delete_intermediate_ps_files(folder_path, index_json_data, '.xlsx')


def load_index_json(folder_path):
    '''
    Reading index_json file and returns data.
    '''
    with open(os.path.join(folder_path, INDEX_JSON_STR), 'r',
                encoding=ENCODING_ASCII) as index_json:
        return json.loads(index_json.read())


def cleanup_intermediate_pdu_product_sets(product_set):
    '''
    Cleanup the intermediate product sets that are older than the release version.
    '''
    try:
        log.info('Initiated cleanup for versions lower than : %s' , product_set)
        config = Config.parse(read_config_file(CONFIG_YAML_PATH))
        folder_path = config.output_folder
        index_json_data = load_index_json(folder_path)
        product_sets_to_delete = get_pdu_versions_older_than_release_version(
                                                                index_json_data, product_set)
        update_index_json_and_del_intermediate_ps(folder_path,
                                                     product_sets_to_delete, index_json_data)
        log.info('Completed Cleanup.')
    except (FileNotFoundError, OSError):
        log.error('Cleanup Failed')
        log.error(traceback.print_exc())
