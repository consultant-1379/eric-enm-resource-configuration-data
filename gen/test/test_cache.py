import logging
import os
import json
import pytest
from utils.cache import init_cache, CACHE_DIR, cached

normalized_response_21_13_18 = '{"csar_data": [{"gerrit_sha": "https://gerrit-gamma.gic.ericsson.se/gitweb?p=OSS/com.ericsson.oss.containerisation/eric-enm-csar-package.git;a=commitdiff;h=c229ae38ba47d2b7cf1c989f630bb094a0392e75", "csar_version": "1.10.0-5", "csar_verify": false, "csar_production_url": "", "csar_dev_url": "https://arm902-eiffel004.athtem.eei.ericsson.se:8443/nexus/content/repositories/releases//cENM/csar/enm-installation-package/1.10.0-5/enm-installation-package-1.10.0-5.csar", "date_created": "2021-08-03 08:39:14", "size (MB)": "17407", "csar_name": "enm-installation-package"}], "integration_charts_data": [{"chart_version": "1.15.0-5", "gerrit_sha": "https://gerrit-gamma.gic.ericsson.se/gitweb?p=OSS/com.ericsson.oss.containerisation/eric-enm-monitoring-integration.git;a=commitdiff;h=ae9f4b0186321dcb4f7eca899c73a866b0456111", "chart_dev_url": "https://arm.epk.ericsson.se/artifactory/proj-enm-dev-internal-helm/eric-enm-monitoring-integration/eric-enm-monitoring-integration-1.15.0-5.tgz", "size(B)": 53718, "chart_verfied": true, "chart_name": "eric-enm-monitoring-integration", "date_created": "2021-08-03T07:05:31", "chart_production_url": "https://arm.epk.ericsson.se/artifactory/proj-enm-helm/eric-enm-monitoring-integration/eric-enm-monitoring-integration-1.15.0-5.tgz"}, {"chart_version": "1.10.0-6", "gerrit_sha": "https://gerrit-gamma.gic.ericsson.se/gitweb?p=OSS/com.ericsson.oss.containerisation/eric-enm-pre-deploy-integration.git;a=commitdiff;h=c96b50d5e64bfbfc29bdd485691b19fbd10aea1a", "chart_dev_url": "https://arm.epk.ericsson.se/artifactory/proj-enm-dev-internal-helm/eric-enm-pre-deploy-integration/eric-enm-pre-deploy-integration-1.10.0-6.tgz", "size(B)": 27750, "chart_verfied": true, "chart_name": "eric-enm-pre-deploy-integration", "date_created": "2021-08-03T07:06:10", "chart_production_url": "https://arm.epk.ericsson.se/artifactory/proj-enm-helm/eric-enm-pre-deploy-integration/eric-enm-pre-deploy-integration-1.10.0-6.tgz"}, {"chart_version": "1.15.0-6", "gerrit_sha": "https://gerrit-gamma.gic.ericsson.se/gitweb?p=OSS/com.ericsson.oss.containerisation/eric-enm-infra-integration.git;a=commitdiff;h=81b6ff6d52e017494bdb91b6a84b183a1252ca91", "chart_dev_url": "https://arm.epk.ericsson.se/artifactory/proj-enm-dev-internal-helm/eric-enm-infra-integration/eric-enm-infra-integration-1.15.0-6.tgz", "size(B)": 249361, "chart_verfied": true, "chart_name": "eric-enm-infra-integration", "date_created": "2021-08-03T07:23:33", "chart_production_url": "https://arm.epk.ericsson.se/artifactory/proj-enm-helm/eric-enm-infra-integration/eric-enm-infra-integration-1.15.0-6.tgz"}, {"chart_version": "1.15.0-5", "gerrit_sha": "https://gerrit-gamma.gic.ericsson.se/gitweb?p=OSS/com.ericsson.oss.containerisation/eric-enm-stateless-integration.git;a=commitdiff;h=eb9430496e619282c0e82ff3166544bb07dc2c78", "chart_dev_url": "https://arm.epk.ericsson.se/artifactory/proj-enm-dev-internal-helm/eric-enm-stateless-integration/eric-enm-stateless-integration-1.15.0-5.tgz", "size(B)": 916386, "chart_verfied": true, "chart_name": "eric-enm-stateless-integration", "date_created": "2021-08-03T07:26:34", "chart_production_url": "https://arm.epk.ericsson.se/artifactory/proj-enm-helm/eric-enm-stateless-integration/eric-enm-stateless-integration-1.15.0-5.tgz"}, {"chart_version": "1.9.0-2", "gerrit_sha": "https://gerrit-gamma.gic.ericsson.se/gitweb?p=OSS/com.ericsson.oss.containerisation/eric-enm-bro-integration.git;a=commitdiff;h=f91e2f75f5cccf228454db5de0157f3854642d1c", "chart_dev_url": "https://arm.epk.ericsson.se/artifactory/proj-enm-dev-internal-helm/eric-enm-bro-integration/eric-enm-bro-integration-1.9.0-2.tgz", "size(B)": 13194, "chart_verfied": true, "chart_name": "eric-enm-bro-integration", "date_created": "2021-08-03T07:28:15", "chart_production_url": "https://arm.epk.ericsson.se/artifactory/proj-enm-helm/eric-enm-bro-integration/eric-enm-bro-integration-1.9.0-2.tgz"}], "integration_values_file_data": [{"values_file_verify": true, "values_file_production_url": "https://arm.epk.ericsson.se/artifactory/proj-enm-helm/eric-enm-integration-values/eric-enm-integration-production-values-1.11.0-2.yaml", "values_file_version": "1.11.0-2", "values_file_dev_url": "https://arm.epk.ericsson.se/artifactory/proj-enm-dev-internal-helm/eric-enm-integration-values/eric-enm-integration-production-values-1.11.0-2.yaml", "values_file_name": "eric-enm-integration-production-values"}], "deployment_utilities_data": []}'

def test_init_cache_dir_creation_failure(fs):
    fs.create_file(CACHE_DIR)
    with pytest.raises(SystemExit):
        init_cache()

def test_init_cache_mkdir(fs):
    fs.create_dir('/var/tmp')
    init_cache()
    assert os.path.exists(CACHE_DIR)

def test_write_to_cache(fs):
    fs.create_dir('/var/tmp/rcd-cache')
    @cached
    def mock_cached_function(drop, drop_version):
        return json.loads(normalized_response_21_13_18)
    mock_cached_function('21.13', '21.13.18')
    assert os.path.exists('/var/tmp/rcd-cache/7e9aa9a21e9db2feacf235120d90fde9')

def test_read_from_cache():
    @cached
    def mock_cached_function(drop, drop_version):
        return json.loads(normalized_response_21_13_18)
    drop_content_response = mock_cached_function('21.13', '21.13.18')
    assert json.dumps(json.loads(normalized_response_21_13_18), sort_keys=True) == json.dumps(drop_content_response, sort_keys=True)