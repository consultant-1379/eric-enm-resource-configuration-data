import os
from cleanup import JSON_EXTENSION, load_pdu_cu_versions, get_pdu_versions_older_than_release_version, delete_intermediate_ps_files, update_index_json, update_index_json_and_del_intermediate_ps, load_index_json, delete_file
import pytest


folder_path = '/gen/test/res/data/'
index_json_string = 'index.json'
original_index_json=[
    {
      "name": "Extra-Large Cloud Native ENM",
      "offering": "cENM",
      "shortName": "Extra-Large cENM",
      "datapath": "eric-enm-integration-extra-large-production-values",
      "versions": [
        {
          "name": "R1FA/1",
          "file": "22.03.95",
          "targetAudience": "cu"
        },
        {
            "name": "22.03.95 (R1FA/1)",
            "file": "22.03.95",
            "targetAudience": "pdu"
        },
        {
          "name": "22.03.90",
          "file": "22.03.90",
          "targetAudience": "pdu"
        }
      ]
    },
    {
      "name": "Small Cloud Native ENM",
      "offering": "cENM",
      "shortName": "Small cENM",
      "datapath": "eric-enm-integration-production-values",
      "versions": [
        {
          "name": "R1FA/1",
          "file": "22.03.95",
          "targetAudience": "cu"
        },
        {
          "name": "22.03.95 (R1FA/1)",
          "file": "22.03.95",
          "targetAudience": "pdu"
        }
      ]
    }
  ]


@pytest.fixture
def initialize_fs(fs):
    fs.create_dir(folder_path)
    fs.create_dir(folder_path + 'eric-enm-integration-extra-large-production-values')
    fs.create_dir(folder_path + 'eric-enm-integration-production-values')


def test_load_index_json(initialize_fs, fs):
    fs.create_file(folder_path + index_json_string, contents='{"key":"value"}')
    data_read_from_json = load_index_json(folder_path)
    assert 'key' in data_read_from_json
    assert 'value' == data_read_from_json['key']


def test_update_index_json(initialize_fs, fs):
    fs.create_file(folder_path + index_json_string, contents='{"key1":"value1", "key2":"value2"}')
    update_index_json({'key1':'value1'}, folder_path)
    data_read_from_json = load_index_json(folder_path)
    assert 'key2' not in data_read_from_json


def test_load_pdu_cu_versions(initialize_fs):
    data = [{
                "name": "Extra-Large Cloud Native ENM",
                "offering": "cENM",
                "shortName": "Extra-Large cENM",
                "datapath": "eric-enm-integration-extra-large-production-values",
                "versions": [
                    {
                        "name": "22.03.90",
                        "file": "22.03.90",
                        "targetAudience": "pdu"
                    },
                    {
                        "name": "R1FA/1",
                        "file": "22.03.95",
                        "targetAudience": "cu"
                    },
                    {
                        "name": "22.03.95 (R1FA/1)",
                        "file": "22.03.95",
                        "targetAudience": "pdu"
                    }
                ]
            },
            {
                "name": "Small Cloud Native ENM",
                "offering": "cENM",
                "shortName": "Small cENM",
                "datapath": "eric-enm-integration-production-values",
                "versions": [
                    {
                        "name": "22.03.90",
                        "file": "22.03.90",
                        "targetAudience": "pdu"
                    },
                    {
                        "name": "R1FA/1",
                        "file": "22.03.95",
                        "targetAudience": "cu"
                    },
                    {
                        "name": "22.03.95 (R1FA/1)",
                        "file": "22.03.95",
                        "targetAudience": "pdu"
                    }
                ]
            }
        ]
    pdu_versions, cu_versions = load_pdu_cu_versions(data)
    assert len(cu_versions) == 1
    assert '22.03.95' in cu_versions
    assert len(pdu_versions) == 2


def test_get_pdu_versions_older_than_release_version():
    data = [{
                "name": "Extra-Large Cloud Native ENM",
                "offering": "cENM",
                "shortName": "Extra-Large cENM",
                "datapath": "eric-enm-integration-extra-large-production-values",
                "versions": [
                    {
                        "name": "22.03.90",
                        "file": "22.03.90",
                        "targetAudience": "pdu"
                    },
                    {
                        "name": "R1FA/1",
                        "file": "22.03.95",
                        "targetAudience": "cu"
                    },
                    {
                        "name": "22.03.95 (R1FA/1)",
                        "file": "22.03.95",
                        "targetAudience": "pdu"
                    }
                ]
            },
            {
                "name": "Small Cloud Native ENM",
                "offering": "cENM",
                "shortName": "Small cENM",
                "datapath": "eric-enm-integration-production-values",
                "versions": [
                    {
                        "name": "22.03.90",
                        "file": "22.03.90",
                        "targetAudience": "pdu"
                    },
                    {
                        "name": "R1FA/1",
                        "file": "22.03.95",
                        "targetAudience": "cu"
                    },
                    {
                        "name": "22.03.95 (R1FA/1)",
                        "file": "22.03.95",
                        "targetAudience": "pdu"
                    }
                ]
            }
        ]
    release_version = '22.03.95'
    pdu_version_candidate = get_pdu_versions_older_than_release_version(data, release_version)
    assert "22.03.90" in pdu_version_candidate


def test_get_pdu_versions_older_than_release_version_none():
    original_index_json = [
                            {
                              "name": "Extra-Large Cloud Native ENM",
                              "offering": "cENM",
                              "shortName": "Extra-Large cENM",
                              "datapath": "eric-enm-integration-extra-large-production-values",
                              "versions": [
                                {
                                  "name": "R1FA/1",
                                  "file": "22.03.95",
                                  "targetAudience": "cu"
                                }
                              ]
                            },
                            {
                              "name": "Small Cloud Native ENM",
                              "offering": "cENM",
                              "shortName": "Small cENM",
                              "datapath": "eric-enm-integration-production-values",
                              "versions": [
                                {
                                  "name": "R1FA/1",
                                  "file": "22.03.95",
                                  "targetAudience": "cu"
                                }
                              ]
                            }
                          ]
    release_version = '22.03'
    pdu_version_candidate = get_pdu_versions_older_than_release_version(original_index_json, release_version)
    assert len(pdu_version_candidate) == 0


def test_delete_intermediate_ps_files_json(initialize_fs, fs):
    variant = 'eric-enm-integration-production-values'
    file = '22.03.90'
    file_path = folder_path + variant + '/' + file + JSON_EXTENSION
    fs.create_file(file_path, contents='')
    delete_intermediate_ps_files(folder_path, original_index_json, JSON_EXTENSION)
    assert not os.path.exists(file_path)


def test_delete_intermediate_ps_files_xlsx(initialize_fs, fs):
    variant = 'eric-enm-integration-production-values'
    file = '22.03.90'
    xslx_ext = '.xlsx'
    file_path = folder_path + variant + '/' + file + xslx_ext
    fs.create_file(file_path, contents='')
    delete_intermediate_ps_files(folder_path, original_index_json, xslx_ext)
    assert not os.path.exists(file_path)


def test_delete_intermediate_ps_files_failed(initialize_fs, fs):
    variant = 'eric-enm-integration-production-values'
    file = '22.03.90'
    file_name = folder_path + variant + '/' + file + JSON_EXTENSION
    assert not os.path.exists(file_name)
    delete_file(file_name)
    assert not os.path.exists(file_name)


def test_delete_product_sets_index_json(initialize_fs, fs):
    index_json_data= original_index_json
    fs.create_file(folder_path+index_json_string, contents=str(original_index_json))
    for variant in index_json_data:
        for version in variant['versions']:
            if version['targetAudience'] != 'cu':
                fs.create_file(folder_path + variant['datapath'] + '/' + version['file'] + '.json', contents='')
    update_index_json_and_del_intermediate_ps(folder_path, ['22.03.90'], index_json_data)
    assert os.path.exists(os.path.join(folder_path, 'eric-enm-integration-production-values', '22.03.95.json'))
    assert not os.path.exists(os.path.join(folder_path, 'eric-enm-integration-production-values', '22.03.90.json'))

