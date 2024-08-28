from datasrc.ciportal import get_latest_green_product_set_version, CI_API_BASE, get_drop_content, get_drop_rstate
from utils import cache
cache.IGNORE_CACHE = True


def test_get_latest_green_product_set_version(requests_mock):
    requests_mock.get(
        f"{CI_API_BASE}/api/cloudNative/getGreenProductSetVersion/21.13/", text='21.13.97-1')
    assert get_latest_green_product_set_version(drop='21.13') == '21.13.97-1'


def test_get_drop_content(requests_mock):
    ci_response = [{'csar_data': [{'csar_version': '1.10.0-31'}]},
                   {'integration_charts_data': [
                       {'chart_version': '1.10.0-27'}]},
                   {'integration_values_file_data': [
                       {'values_file_name': 'eric-enm-integration-production-values'}]},
                   {'deployment_utilities_data': []}
                   ]
    requests_mock.get(
        f"{CI_API_BASE}/api/cloudnative/getCloudNativeProductSetContent/21.13/21.13.97-1/", json=ci_response)
    exp_response = {'csar_data': [{'csar_version': '1.10.0-31'}],
                    'integration_charts_data': [{'chart_version': '1.10.0-27'}],
                    'integration_values_file_data': [{'values_file_name': 'eric-enm-integration-production-values'}],
                    'deployment_utilities_data': []
                    }
    assert get_drop_content('21.13', '21.13.97-1') == exp_response


def test_get_drop_rstate(requests_mock):
    ci_response = 'AOM 901 151 R1EN'
    requests_mock.get(
        f"{CI_API_BASE}/getAOMRstate/?product=ENM&drop=21.13", text=ci_response)
    assert get_drop_rstate('21.13') == 'R1EN'
