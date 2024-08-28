import json
import pytest
import rcd_exceptions
import os
from utils.utils import find, find_all, read_json_file
from utils.utils import download_file, calculate_total, remove_units_from_k8s_resource
from utils.utils import extract_files_from_archive, check_path_in_dict


def test_find():
    lst = [{'name': 'amos'}, {'name': 'amos-0'}, {'name': 'notamos'}]
    assert find(lst, 'name', 'amos') == 0


def test_find_all():
    lst = [{'name': 'amos'}, {'name': 'notamos'}, {'name': 'amos-1'}]
    assert find_all(lst, 'name', 'amos') == [0, 2]


def test_read_json_file(fs):
    path = '/var/tmp/hello.json'
    fs.create_file(path, contents=json.dumps({'hello': 'world'}))
    res = read_json_file(path)
    print(res)
    assert res['hello'] == 'world'


def test_calculate_total_all_enabled():
    resource_list = [{'name': 'eshistory-bragentproperties', 'app_enabled': True},
                     {'name': 'eshistory-cfg', 'app_enabled': True},
                     {'name': 'eshistory-helmtest-config', 'app_enabled': True}
                    ]
    assert calculate_total(resource_list) == 3

def test_calculate_total_one_disabled():
    resource_list = [{'name': 'eshistory-bragentproperties', 'app_enabled': False},
                     {'name': 'eshistory-cfg', 'app_enabled': True},
                     {'name': 'eshistory-helmtest-config', 'app_enabled': True}
                    ]
    assert calculate_total(resource_list) == 2

def test_download_file_error():
    username = "dummy_user"
    password = "dummy_pwd"
    full_chart_name = "invalid"
    full_url = "invalid"
    with pytest.raises(rcd_exceptions.FileDownloadError) as exc_info:
        download_file(full_url, full_chart_name, username, password, 'wb')
    assert str(exc_info.value) == "File download returned an error"

def test_extract_files_from_archive_error():
    file_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_path)
    input_file= os.path.join(file_dir, "resources/charts.tgz")
    with pytest.raises(FileNotFoundError) as exc_info:
        extract_files_from_archive(input_file, file_to_extract_path='optionality.yaml')
    assert str(exc_info.value) == "Could not find the file pattern 'optionality.yaml' in the given archive 'charts.tgz'"

def test_extract_files_from_archive():
    file_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_path)
    input_file= os.path.join(file_dir, "resources/test-zip-file.zip")
    list_of_extracted_files = extract_files_from_archive(input_file, file_to_extract_path='test.txt')
    assert len(list_of_extracted_files) == 1

def test_check_path_in_dict():
    dictionary = {
        'a': {
                'b': {
                    'c': 42
                }
            }
    }
    path = ['a', 'b', 'c']
    assert check_path_in_dict(dictionary, path) == True

def test_check_empty_path_in_dict():
    dictionary = {'key': 'value'}
    assert check_path_in_dict(dictionary, None) == True

def test_remove_units_from_k8s_resource():
    resource_str = "dummy_str"
    assert remove_units_from_k8s_resource(resource_str) == resource_str