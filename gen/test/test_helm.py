import pytest
import yaml
from datasrc.helm import template
from utils import cache

cache.IGNORE_CACHE = True


def test_template():
    values_file = "gen/test/resources/test_values.yaml"
    values = yaml.load(open(values_file), yaml.Loader)
    chart_name = '/eric-enm-bro-integration-1.10.0-8.tgz'
    chart_url = 'http://localhost:5005' + chart_name
    username = "dummy_user"
    password = "dummy_pwd"
    result = {'apiVersion': 'policy/v1beta1',
              'kind': 'PodDisruptionBudget',
              'metadata': {'name': 'eric-ctrl-bro-pdb', 'labels': {'app.kubernetes.io/managed-by': 'Helm', 'chart': 'eric-ctrl-bro-4.5.0_47', 'app.kubernetes.io/name': 'eric-ctrl-bro', 'app.kubernetes.io/version': '4.5.0_47', 'app.kubernetes.io/instance': 'release-name'}, 'annotations': {'ericsson.com/product-name': 'Backup and Restore Orchestrator', 'ericsson.com/product-number': 'CXC 201 2182', 'ericsson.com/product-revision': '4.5.0'}},
              'spec': {'minAvailable': 0, 'selector': {'matchLabels': {'app.kubernetes.io/name': 'eric-ctrl-bro', 'app.kubernetes.io/instance': 'release-name'}}}}

    assert result in list(template(values, chart_url, username, password))


def test_template_execute_error():
    values_file = "gen/test/resources/test_values.yaml"
    values = yaml.load(open(values_file), yaml.Loader)
    chart_name = '/non_existing_chart.tgz'
    chart_url = 'http://localhost:5005' + chart_name
    with pytest.raises(SystemExit):
        list(template(values, chart_url))
