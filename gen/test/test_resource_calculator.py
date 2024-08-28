import pytest
from mock import patch
import json
import os
from model.overview import Overview
from output.output_json import MyEncoder
import api.resource_calculation
from api.resource_calculation import (prepare_data,
                                      prepare_excel_data,
                                      prepare_agg_data,
                                      get_resource_overview,
                                      prepare_data_comparison,
                                      validate_version,
                                      InvalidVersionException)
EXPECTED_RESULT_21_14_84_EBSLNM = 'gen/test/resources/expected_prepare_data_response_ebs_lnm.json'
EXPECTED_RESULT_21_15_84_EBSLNM = 'gen/test/resources/expected_prepare_data_response_ebs_lnm-ipv6.json'
EXPECTED_RESULT_EIC = 'gen/test/resources/eic/expected_prepare_agg_data_response_2.19.0-8.json'
EXPECTED_RESULT_EIC_WITH_ISTIO = 'gen/test/resources/eic/expected_prepare_agg_data_response_2.662.0.json'

expected_result_path_21_14_84_no_opt_apps = 'gen/test/resources/expected_prepare_data_response_no_opt_apps.json'
VARIANT = 'eric-enm-integration-production-values'

test_data_base = [
    'csar',
    'config_maps',
    'secrets',
    'services',
    'ingresses',
    'eric_ingresses',
    'optional_value_packs',
    'validation_errors',
    'selectedVariant',
    'pvcs',
    'workloads',
    'calc'
    ]
@pytest.mark.parametrize("val", test_data_base)
def test_prepare_data(val):
    enabled_apps = ['Event Based Statistics for MME (EBS-M)', 'Event Based Statistics for LTE (EBS-L) and MME (EBS-N)']
    result = prepare_data(VARIANT, '21.14.84', 'ipv4', enabled_apps)
    exp_result = json.load(open(EXPECTED_RESULT_21_14_84_EBSLNM))
    with open('out.json','w') as f:
        json.dump(result, f, cls=MyEncoder, indent=2)
    assert result[val] == exp_result[val]

def test_prepare_excel_data():
    enabled_apps = ['Event Based Statistics for MME (EBS-M)', 'Event Based Statistics for LTE (EBS-L) and MME (EBS-N)']
    result = prepare_excel_data(VARIANT, '21.14.84', 'ipv4', enabled_apps)
    expected_value = [('A52', 'ebscontroller'), ('C52', True), ('A56', 'ebsflow'), ('C56', True), ('A59', 'ebstopology'), ('C59', True)]
    for cell, value in expected_value:
        assert result['Workloads'][cell].value == value

def test_prepare_agg_data():
    variant = "eric-eic-integration-fixed-size-production-values"
    version = "2.19.0-8"
    ip_version = "default"
    enabled_apps = [
        'eric-oss-pm-stats-calc-handling',
        'eric-oss-ml-execution-env',
        'eric-cloud-native-service-mesh',
        'eric-cnbase-oss-config',
        'eric-cloud-native-base',
        'eric-oss-common-base',
        'eric-oss-oran-support',
        'eric-oss-adc',
        'eric-oss-dmm,eric-topology-handling',
        'eric-oss-ericsson-adaptation',
        'eric-oss-app-mgr',
        'eric-oss-config-handling',
        'eric-oss-task-automation-ae'
    ]

    result = prepare_agg_data(variant, version, ip_version, enabled_apps)
    exp_result = json.load(open(EXPECTED_RESULT_EIC))
    assert getattr(result["overview"], "total") == exp_result["overview"]["total"]

def test_prepare_agg_data_with_istio_values():
    variant = "eric-eic-integration-fixed-size-production-values"
    version = "2.662.0"
    ip_version = "default"
    enabled_apps = [
        'eric-oss-pm-stats-calc-handling',
        'eric-oss-ml-execution-env',
        'eric-cloud-native-service-mesh',
        'eric-cloud-native-base',
        'eric-oss-adc',
        'eric-service-exposure-framework'
    ]

    result = prepare_agg_data(variant, version, ip_version, enabled_apps)
    exp_result = json.load(open(EXPECTED_RESULT_EIC_WITH_ISTIO))
    assert getattr(result["overview"], "total") == exp_result["overview"]["total"]

test_data_overview = [
    ('overview', 'total'),
    ('overview', 'sum'),
    ('overview', 'requests'),
    ('overview', 'limits'),
    ('overview', 'max'),
    ('overview', 'min'),
    ('overview', 'client'),
    ('overview', 'cluster'),
    ('overview', 'registry'),
    ('overview', 'bur'),
    ('overview', 'other_requirements')
    ]
@pytest.mark.parametrize("val1,val2", test_data_overview)
def test_prepare_data_overview(val1, val2):
    enabled_apps = ['Event Based Statistics for MME (EBS-M)', 'Event Based Statistics for LTE (EBS-L) and MME (EBS-N)']
    result = prepare_data(VARIANT, '21.15.84', 'ipv6', enabled_apps)
    exp_result = json.load(open(EXPECTED_RESULT_21_15_84_EBSLNM))
    assert getattr(result[val1], val2) == exp_result[val1][val2]


def test_prepare_data_invalid_version():
    with pytest.raises(InvalidVersionException):
        prepare_data(VARIANT, '225.256', 'dual', [])


test_data_get_resource_overview = [
    'deployment_type',
    'application_version',
    'cpu',
    'cpu_daemon_set',
    'cpu_jobs',
    'memory',
    'memory_daemon_set',
    'memory_jobs',
    'ephemeral',
    'ephemeral_daemon_set',
    'ephemeral_jobs',
    'total_storage_rwo',
    'total_storage_rwx',
    'client_minimum_storage',
    'minimum',
    'external_networks',
    'total_application_images_size',
    'total_registry_size',
    'available_optional_apps',
    'enabled_optional_apps'
    ]
@pytest.mark.parametrize("val", test_data_get_resource_overview)
def test_get_resource_overview(val):
    expected_result_21_14_84_overview = 'gen/test/resources/expected_overview.json'
    result = get_resource_overview(VARIANT, '21.14.84', 'dual', [])
    exp_result = json.load(open(expected_result_21_14_84_overview))
    assert result[val] == exp_result[val]


def test_get_resource_overview_ipv4():
    result = get_resource_overview(VARIANT, '21.14.84', 'ipv4', [])
    assert result['external_networks'] == {"type": "ipv4",
                                           "vips_ipv4": 1,
                                           "load_balancers": 1}


def test_get_resource_overview_ipv6():
    result = get_resource_overview(VARIANT, '21.14.84', 'ipv6', [])
    assert result['external_networks'] == {"type": "ipv6",
                                           "vips_ipv6": 1,
                                           "load_balancers": 1}


test_data_comparison = [
    'total',
    'sum',
    'requests',
    'limits',
    'max',
    'min',
    'client',
    'cluster',
    'registry',
    'bur'
    ]
@pytest.mark.parametrize("val", test_data_comparison)
def test_prepare_data_comparison(val):
    expected_comparison_result = 'gen/test/resources/expected_comparison_response.json'
    result = prepare_data_comparison(VARIANT, '21.13.84', '21.14', 'dual', [], [])
    exp_result = json.load(open(expected_comparison_result))
    assert getattr(result, val) == exp_result[val]
