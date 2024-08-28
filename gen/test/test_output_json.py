from output.output_json import Storage, json, ENCODING_ASCII
from model.config import Config
import yaml
import os
from model.summary import Summary
import json
import shutil
from mock import patch
from model.config import Config, CVersion
from model.version import Version

data_resources_folder_path = 'test/resources/data/eric-enm-integration-production-values'
cenm_21_10_90 = '21.10.90.json'
cenm_21_13_18 = '21.13.18.json'
config_file_path = 'gen/test/resources/config.test.yaml'
index_json_path = 'test/resources/data/index.json'
index_json_to_be_path = 'gen/test/resources/index_result_to_be.json'
test_resources_data_path = 'gen/test/resources/data'
cenm_21_13_18_json_path = os.path.join(data_resources_folder_path, cenm_21_13_18)
eic_config_file_path = 'gen/test/resources/eic.config.test.yaml'

def test_is_storage_instance_initiated():
    try:
        os.makedirs(data_resources_folder_path, exist_ok=True)
        open(os.path.join(data_resources_folder_path, cenm_21_10_90 ),'a').close()
        open(cenm_21_13_18_json_path,'a').close()
        config = Config.parse(yaml.load(open(config_file_path, 'r', encoding=ENCODING_ASCII).read(), yaml.Loader))
        jstorage = Storage(config)
        assert 'eric-enm-integration-production-values' in jstorage.variants
        assert len(jstorage.variants['eric-enm-integration-production-values']) == 2

    finally:
        if os.path.isdir(test_resources_data_path):
            shutil.rmtree(test_resources_data_path)


def test_storage_file_created():
    try:
        os.makedirs(data_resources_folder_path, exist_ok = True)
        variant = 'eric-enm-integration-production-values'
        version = '21.13.18'
        s = Summary()
        s.workloads = ["wl1", 'wl2']
        s.pvcs = ["pvc1", "pvc2"]
        config = Config.parse(yaml.load(open(config_file_path, 'r', encoding=ENCODING_ASCII).read(), yaml.Loader))
        jstorage = Storage(config)
        jstorage.store(s, variant, version)
        assert os.path.exists(cenm_21_13_18_json_path)
    finally:
        if os.path.isfile(cenm_21_13_18_json_path):
            os.remove(cenm_21_13_18_json_path)


@patch('output.output_json.get_drop_rstate', side_effect=['R1EK','R1EK', 'R1EH', 'R1EH'])
def test_store_index(m_get_drop_rstate):
    try:
        variants = {'eric-enm-integration-production-values': {'21.10.90', '21.13.18', '21.08.18'},
                    'eric-enm-integration-extra-large-production-values': {'21.10.90', '21.13.18', '21.08.18'}}
        config = Config.parse(yaml.load(open(config_file_path, 'r', encoding=ENCODING_ASCII).read(), yaml.Loader))
        jstorage = Storage(config)
        jstorage.variants = variants

        version_release= [['21.13.18'],['21.10.90', True], ['21.08.18', 2], ['21.09.100']]
        for index in range(len(version_release)):
            release= None
            if len(version_release[index]) > 1:
                release= version_release[index][1]
            else:
                release= None
            version = CVersion(Version.parse(version_release[index][0]), release, False)
            jstorage.store_index(version)
        loaded_json_result = json.loads(open(index_json_path, 'r').read())
        loaded_json_result_to_be = json.loads(open(index_json_to_be_path, 'r').read())
        print('loaded_json_result_to_be\n', loaded_json_result_to_be)
        print('loaded_json_result\n', loaded_json_result)
        assert loaded_json_result_to_be == loaded_json_result
    finally:
        if os.path.isdir(test_resources_data_path):
            shutil.rmtree(test_resources_data_path)

def test_store_index_eic_release():
    try:
        release_version = '2.23.0-122'
        variants = {
            'eric-eic-integration-fixed-size-production-values': {release_version}
        }
        config = Config.parse(yaml.load(open(eic_config_file_path, 'r', encoding=ENCODING_ASCII).read(), yaml.Loader))
        jstorage = Storage(config)
        jstorage.variants = variants
        version = CVersion(Version.parse(release_version), True, False)
        jstorage.store_index(version, True)
        updated_index_json_path = 'gen/test/resources/eic_data/index.json'
        expected_index_json_path = 'gen/test/resources/expected_index_2.23.0-122.json'
        loaded_updated_json_result = json.loads(open(updated_index_json_path, 'r').read())
        loaded_expected_json_result = json.loads(open(expected_index_json_path, 'r').read())
        assert loaded_expected_json_result == loaded_updated_json_result
    finally:
        if os.path.isfile(updated_index_json_path):
            os.remove(updated_index_json_path)
