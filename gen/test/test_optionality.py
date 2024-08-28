import json
import os
from pathlib import Path
from datasrc.optionality import generate_optionality_maximum, get_helmfile_optionality

def test_generate_optionality_maximum_success():
    file_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_path)
    helmfile_path = os.path.join(file_dir, "resources/eic/eric-eiae-helmfile/helmfile.yaml")
    helm_releases_json_path = os.path.join(file_dir, "resources/eic/helm_releases.json")
    helmfile_dir = os.path.dirname(helmfile_path)
    optionality_maximum_file = os.path.join(helmfile_dir, 'build-environment/optionality_maximum.yaml')
    releases_dict = json.loads(open(helm_releases_json_path, 'r').read())
    generate_optionality_maximum(helmfile_path, releases_dict)
    assert os.path.exists(optionality_maximum_file) == 1

def test_generate_optionality_maximum_empty():
    file_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_path)
    helmfile_path = os.path.join(file_dir, "resources/eic/eric-eiae-helmfile/helmfile.yaml")
    helm_releases_json_path = os.path.join(file_dir, "resources/eic/helm_releases_invalid.json")
    helmfile_dir = os.path.dirname(helmfile_path)
    optionality_maximum_file = os.path.join(helmfile_dir, 'build-environment/optionality_maximum.yaml')
    releases_dict = json.loads(open(helm_releases_json_path, 'r').read())
    generate_optionality_maximum(helmfile_path, releases_dict)
    assert os.path.exists(optionality_maximum_file) == 1

def test_get_helmfile_optionality():
    file_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_path)
    path_to_helmfile = os.path.join(file_dir, "resources/eic/eric-eiae-helmfile/helmfile.yaml")
    optionality_dicts = get_helmfile_optionality(path_to_helmfile=path_to_helmfile)
    assert len(optionality_dicts) == 0