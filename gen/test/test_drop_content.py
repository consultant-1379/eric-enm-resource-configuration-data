import json

from model.chart import Chart
from model.drop_content import DropContent, production_or_dev_url

drop_content = """
{
    "csar_data": [{
        "csar_version": "1.8.0-14",
        "csar_production_url": "https://installation_package_prod_csar_url_lite",
        "csar_dev_url": "https://installation_package_dev_csar_url_lite",
        "csar_name": "enm-lite-installation-package"
    },
    {
        "csar_version": "1.8.0-14",
        "csar_production_url": "https://installation_package_prod_csar_url",
        "csar_dev_url": "https://installation_package_dev_csar_url",
        "csar_name": "enm-installation-package"
    }],
    "integration_charts_data": [{
        "chart_version": "1.8.0-16",
        "chart_dev_url": "https://deploy_integration_chart_dev_url",
        "chart_name": "eric-enm-pre-deploy-integration",
        "chart_production_url": "https://deploy_integration_prod_chart_url"
    }, {
        "chart_version": "1.13.0-20",
        "chart_dev_url": "https://monitoring_integration_chart_dev_url",
        "chart_name": "eric-enm-monitoring-integration",
        "chart_production_url": "https://monitoring_integration_prod_chart_url"
    }],
    "integration_values_file_data": [{
        "values_file_verify": true,
        "values_file_production_url": "https://integration_values_prod_url",
        "values_file_version": "1.20.0-2",
        "values_file_dev_url": "https://integration_values_dev_url",
        "values_file_name": "eric-enm-integration-production-values"
    }]
}
"""


def test_production_or_dev_url():
    prod_csar_url = 'some_csar_prod_url'
    prod_csar_dict = {'csar_production_url': prod_csar_url}
    dev_chart_url = 'some_chart_dev_url'
    dev_chart_dict = {'chart_dev_url': dev_chart_url}
    assert production_or_dev_url(prod_csar_dict, "csar") == prod_csar_url
    assert production_or_dev_url(dev_chart_dict, "chart") == dev_chart_url


def test_drop_content_parse():
    exp_response = DropContent(charts=[Chart(name='eric-enm-pre-deploy-integration',
                                             url='https://deploy_integration_prod_chart_url'),
                                       Chart(name='eric-enm-monitoring-integration',
                                             url='https://monitoring_integration_prod_chart_url')],
                               csar='https://installation_package_prod_csar_url',
                               values_file="https://integration_values_prod_url")
    assert DropContent.parse(json.loads(drop_content)) == exp_response
