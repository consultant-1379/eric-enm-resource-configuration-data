import os
import pytest
import rcd_exceptions
from datasrc.helmfile import get_chart_templates, fetch_helmfile_details
from datasrc.helmfile import build_manifest, get_all_templates, execute_helmfile_command

def test_get_chart_templates():
    templates = [{"kind":"Deployment","metadata":{"labels":{"app.kubernetes.io/instance":"dummy-app"}}}]
    chart_templates = get_chart_templates("dummy-app", templates)
    assert len(chart_templates) == 1

def test_fetch_helmfile_details():
    file_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_path)
    helmfile = os.path.join(file_dir, "resources/eic/eric-eiae-helmfile/helmfile.yaml")
    state_values_file = os.path.join(file_dir, "resources/eic/eric-eiae-helmfile/build-environment/tags_true.yaml")
    releases_dict, csar_dict = fetch_helmfile_details(state_values_file, helmfile)
    assert len(releases_dict) == 1
    assert len(csar_dict) == 1

def test_get_all_templates():
    file_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_path)
    helmfile = os.path.join(file_dir, "resources/eic/helmfile-test-data/helmfile.yaml")
    state_values_file = os.path.join(file_dir, "resources/eic/helmfile-test-data/build-environment/tags_true.yaml")
    manifest_file_path = build_manifest(state_values_file, helmfile)
    assert os.path.exists(manifest_file_path) == 1
    templates = get_all_templates(manifest_file_path)
    assert len(templates) == 2
    if os.path.exists(manifest_file_path):
        os.remove(manifest_file_path)


def test_execute_helmfile_command():
    file_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_path)
    helmfile = os.path.join(file_dir, "resources/eic/helmfile-test-data/helmfile-fail.yaml")
    state_values_file = os.path.join(file_dir, "resources/eic/helmfile-test-data/build-environment/tags_true.yaml")
    manifest_file_path = os.path.join(file_dir, "resources/eic/helmfile-test-data/manifest.yaml")

    with pytest.raises(rcd_exceptions.HelmfileTemplateBuildError) as exc_info:
        execute_helmfile_command(state_values_file, helmfile, manifest_file_path, "template")

    assert str(exc_info.value) == "The helmfile build returned an error"
