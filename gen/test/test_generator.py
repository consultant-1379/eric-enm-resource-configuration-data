import io
import json
from math import exp
import os
import shutil
import yaml
import utils
import rcd_exceptions
from datasrc.helmfile import build_manifest
from datasrc.csar import CSARInfo
from output import output_json
from generator import provision_rcd, provision_eic_rcd, setup_client_cluster_requirements
from generator import validate_pdb, prepare_optional_value_packs, add_istio_side_cars
from mock import patch
from model.summary import Summary, EICSummary
from model.config import CVersion, Config, Version
from model.resource_requirements import WL, Container, ContainerRR, Selector, WLRR, PDB
import generator
from generator import skip_validation_errors_for_sgs, clean_up_eic_tmp, change_to_app_dir
from generator import get_site_values_info, get_helm_file_info, get_credentials
import pytest

chart_file_name = '/charts.tgz'
chart_url = 'http://localhost:5005' + chart_file_name
values_file_name = '/test_values.yaml'
values_url = 'http://localhost:5005' + values_file_name
config_yml_path = 'gen/test/resources/config.yaml'
eic_manifest_yml_path = 'gen/test/resources/eic/helmfile-test-data/manifest.yaml'
eic_manifest_with_annotation_yml_path = 'gen/test/resources/eic/helmfile-test-data/manifest_with_annotation.yaml'
data_integration_values_path = 'gen/test/resources/data_main/eric-enm-integration-production-values/'
eic_data_integration_values_path = 'gen/test/resources/data_main/eric-eic-integration-fixed-size-production-values/'
data_json_path = os.path.join(data_integration_values_path, '21.13.97.json')
expected_data_json_path = 'gen/test/resources/expected_21.13.97.json'
index_json_path = 'gen/test/resources/data_main/index.json'
eic_data_json_dir_path = os.path.join(eic_data_integration_values_path, '2.23.0-120')
eic_data_json_apps_file_path = os.path.join(eic_data_json_dir_path, 'apps.json')
eic_data_json_dummy_app_path = os.path.join(eic_data_json_dir_path, 'dummy-app.json')
generator.CONFIG_YAML_PATH= config_yml_path
drop_content = {'csar_data': [{'csar_name': 'enm-installation-package', 'csar_dev_url': 'https://some_url'}],
                'integration_charts_data': [{'chart_version': '1.15.0-21', 'chart_name': 'eric-enm-monitoring-integration', 'chart_production_url': chart_url}],
                'integration_values_file_data': [{'values_file_production_url': 'values_url', 'values_file_name': 'eric-enm-integration-production-values'}],
                }
csar_info = CSARInfo(images=['armdocker.rnd.ericsson.se/proj-enm/eric-enmsg-sa-service:1.14.0-23'], total_images_size=28970658816, values_files=[], charts=[])
csar_values_file = {'global': {'pullSecret': None, 'registry': {'url': None, 'pullSecret': None}, 'timezone': None, 'persistentVolumeClaim': {'storageClass': None}, 'ingress': {'enmHost': None, 'class': 'ingress-nginx'}, 'vips': {}, 'enmProperties': {'enm_deployment_type': 'Small_CloudNative_ENM', 'COM_INF_LDAP_ADMIN_CN': None, 'COM_INF_LDAP_ROOT_SUFFIX': None, 'host_system_identifier': None, 'PKI_EntityProfile_DN_COUNTRY_NAME': None, 'PKI_EntityProfile_DN_ORGANIZATION': None, 'PKI_EntityProfile_DN_ORGANIZATION_UNIT': None, 'certificatesRevListDistributionPointServiceDnsEnable': None, 'certificatesRevListDistributionPointServiceIpv4Enable': None, 'certificatesRevListDistributionPointServiceIpv6Enable': None, 'publicKeyInfraRegAutorithyPublicServerName': None}, 'nodeSelector': {"testSelectorKey": "testSelectorValue"}, 'emailServer': None, 'rwx': {'storageClass': None}, 'sentinelHostname': 'sentinel-0'}, 'eric-enm-version-configmap': {'enabled': True, 'productVersion': 'ENM 21.13 (CSAR Version: 1.10.0-26) AOM 901 151 R1EN', 'productionDate': '2021-08-18T09:41:33Z', 'productSet': '21.13.89'}, 'eric-oss-ingress-controller-nx': {'enabled': True, 'ingressClass': 'ingress-nginx', 'ingressClassResource': {'enabled': True}, 'service': {'loadBalancerIP': None, 'annotations': {}}, 'resources': {'requests': {'cpu': '600m', 'memory': '2048Mi'}, 'limits': {'cpu': '2000m', 'memory': '2048Mi'}}, 'imageCredentials': {'repoPath': 'proj-enm/proj-eric-oss-ingress-ctr-nx-dev'}}, 'eric-enm-monitoring-master': {'enabled': True, 'monitoring': {'autoUpload': {'enabled': True, 'ddpsite': None, 'account': None, 'password': None}}}, 'eric-enm-monitoring-remotewriter': {'enabled': True}, 'eric-pm-server': {'enabled': True, 'server': {'persistentVolume': {'storageClass': None, 'size': '25Gi'}}, 'resources': {'eric-pm-server': {'limits': {'cpu': '3', 'memory': '10Gi'}, 'requests': {'cpu': '1', 'memory': '5Gi'}}}, 'imageCredentials': {'repoPath': 'proj-enm/proj-common-assets-cd/monitoring/pm'}}, 'eric-pm-node-exporter': {'enabled': True, 'prometheus': {'nodeExporter': {'service': {'hostPort': None, 'servicePort': None}}}, 'imageCredentials': {'repoPath': 'proj-enm/proj_kds/erikube'}}, 'eric-pm-alert-manager': {'enabled': True, 'persistence': {'persistentVolumeClaim': {'storageClassName': None}}, 'imageCredentials': {'repoPath': 'proj-enm/proj-adp-pm-alert-manager-drop'}}, 'eric-enm-fm-alert-parser': {'enabled': True}, 'eric-net-ingress-l4': {'enabled': True, 'sidecars': {'eric-enm-snmp-trap-forwarder': {'enabled': True}, 'eric-enm-http-alarms-forwarder': {'enabled': True}}, 'fullnameOverride': {}, 'virtualRouterId': 106, 'tolerations': [{'key': 'node', 'operator': 'Equal', 'effect': 'NoSchedule', 'value': 'routing'}], 'nodeSelector': None, 'resources': {'requests': {'enabled': True, 'memory': '2048Mi', 'cpu': '300m'}, 'limits': {'enabled': True, 'memory': '2048Mi', 'cpu': '1000m'}}, 'interfaces': {'internal': None, 'external': None}, 'cniMode': None, 'podNetworkCIDR': None, 'rbac': {'create': True, 'serviceAccountName': None}, 'imageCredentials': {'logshipper': {'repoPath': 'proj-enm/proj-bssf/adp-log/release'}}}, 'eric-net-ingress-l4-crd': {'enabled': True}, 'eric-data-search-engine': {'enabled': True, 'jvmHeap': {'ingest': '1024m', 'master': '512m', 'data': '2048m'}, 'resources': {'ingest': {'limits': {'cpu': '500m', 'memory': '2Gi'}, 'requests': {'cpu': '500m', 'memory': '2Gi'}}, 'master': {'limits': {'cpu': '500m', 'memory': '2Gi'}, 'requests': {'cpu': '500m', 'memory': '2Gi'}}, 'data': {'limits': {'cpu': '1000m', 'memory': '8Gi'}, 'requests': {'cpu': '1000m', 'memory': '8Gi'}}}, 'persistence': {'data': {'persistentVolumeClaim': {'storageClassName': None}}, 'backup': {'persistentVolumeClaim': {'storageClassName': None}}, 'master': {'persistentVolumeClaim': {'storageClassName': None}}}, 'imageCredentials': {'repoPath': 'proj-enm/proj-adp-log-released'}}, 'eric-data-eshistory-search-engine': {'enabled': True, 'persistence': {'data': {'persistentVolumeClaim': {'storageClassName': None}}, 'backup': {'persistentVolumeClaim': {'storageClassName': None}}, 'master': {'persistentVolumeClaim': {'storageClassName': None}}}, 'imageCredentials': {'repoPath': 'proj-enm/proj-adp-log-released'}}, 'eric-data-graph-database-nj': {'enabled': True, 'persistentVolumeClaim': {'storageClass': None, 'backup': {'storageClass': None}, 'logging': {'storageClass': None}}, 'imageCredentials': {'repoPath': 'proj-enm/aia_releases'}}, 'eric-enm-troubleshooting-utils': {'enabled': True}, 'eric-enm-globalproperties': {'enabled': True}, 'eric-enm-rwxpvc': {'enabled': True}, 'eric-enm-serviceroles': {'enabled': True}, 'eric-enmsg-gossiprouter-cache': {'enabled': True, 'resources': {'requests': {'memory': '2000Mi', 'cpu': '272m'}, 'limits': {'memory': '3596Mi', 'cpu': '950m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-gossiprouter-remoting': {'enabled': True, 'resources': {'requests': {'memory': '2000Mi', 'cpu': '272m'}, 'limits': {'memory': '3596Mi', 'cpu': '950m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-gossiprouter-eap7': {'enabled': True, 'resources': {'requests': {'memory': '2000Mi', 'cpu': '272m'}, 'limits': {'memory': '3596Mi', 'cpu': '950m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-jmsserver': {'enabled': True, 'resources': {'requests': {'memory': '22324Mi', 'cpu': '2400m'}, 'limits': {'memory': '22324Mi', 'cpu': '8000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enm-modeldeployservice': {'enabled': True, 'resources': {'modeldeployservice': {'requests': {'memory': '7662Mi', 'cpu': '600m'}, 'limits': {'memory': '7662Mi', 'cpu': '2000m'}}}}, 'eric-enmsg-opendj': {'enabled': True}, 'eric-data-document-database-pg': {'enabled': True, 'persistentVolumeClaim': {'size': '25Gi'}, 'imageCredentials': {'repoPath': 'proj-enm/proj-document-database-pg/data'}}, 'eric-enmsg-sentinel': {'enabled': True, 'resources': {'requests': {'memory': '3596Mi', 'cpu': '600m'}, 'limits': {'memory': '3596Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}, 'persistentVolumeClaim': {'sentinelPVSize': '1Gi'}}, 'eric-enm-kvstore-hc': {'enabled': True, 'resources': {'requests': {'memory': '256Mi', 'cpu': '300m'}, 'limits': {'memory': '512Mi', 'cpu': '1000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}, 'persistentVolumeClaim': {'size': '1Gi'}}, 'eric-enmsg-vault-service': {'enabled': True, 'resources': {'requests': {'memory': '1954Mi', 'cpu': '600m', 'limits': {'memory': '1954Mi', 'cpu': '2000m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '100m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'elasticsearch-bragent': {'enabled': True, 'resources': {'limits': {'cpu': '2000m', 'memory': '512Mi'}, 'requests': {'cpu': '500m', 'memory': '256Mi'}}}, 'eshistory-bragent': {'enabled': True, 'resources': {'limits': {'cpu': '2000m', 'memory': '512Mi'}, 'requests': {'cpu': '500m', 'memory': '256Mi'}}}, 'eric-data-search-engine-curator': {'enabled': True, 'imageCredentials': {'repoPath': 'proj-enm/proj-adp-log-released'}}, 'eric-enmsg-solr-service': {'enabled': True, 'resources': {'requests': {'enabled': True, 'memory': '6144Mi', 'cpu': '600m'}, 'limits': {'enabled': True, 'memory': '6144Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}, 'persistentVolumeClaim': {'solrPVSize': '175Gi'}}, 'eric-ctrl-bro': {'enabled': True, 'resources': {'backupAndRestore': {'limits': {'cpu': 4, 'memory': '4Gi', 'ephemeral-storage': '50Gi'}, 'requests': {'cpu': 2, 'memory': '2Gi', 'ephemeral-storage': '500Mi'}}}, 'persistence': {'persistentVolumeClaim': {'size': '1Ti', 'storageClassName': None}}, 'imageCredentials': {'repoPath': 'proj-enm/proj-adp-eric-ctrl-bro-drop'}}, 'eric-enmsg-auto-id-solr': {'enabled': True, 'resources': {'requests': {'enabled': True, 'memory': '4096Mi', 'cpu': '600m'}, 'limits': {'enabled': True, 'memory': '4096Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}, 'persistentVolumeClaim': {'solrautoidPVSize': '1Gi'}}, 'eric-enmsg-autoid-service': {'enabled': True, 'resources': {'requests': {'memory': '5644Mi', 'cpu': '600m'}, 'limits': {'memory': '6144Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-access-control': {'enabled': True, 'resources': {'requests': {'memory': '3296Mi', 'cpu': '300m'}, 'limits': {'memory': '3596Mi', 'cpu': '1000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-amos': {'enabled': True, 'resources': {'requests': {'memory': '20280Mi', 'cpu': '1200m'}, 'limits': {'memory': '20280Mi', 'cpu': '4000m'}, 'httpd': {
    'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-autoprovisioning': {'enabled': True, 'resources': {'requests': {'memory': '4320Mi', 'cpu': '600m'}, 'limits': {'memory': '4620Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-cmevents': {'enabled': True, 'resources': {'requests': {'memory': '4320Mi', 'cpu': '600m'}, 'limits': {'memory': '4620Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-cmutilities': {'enabled': True, 'resources': {'requests': {'memory': '4320Mi', 'cpu': '600m'}, 'limits': {'memory': '4620Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-cmservice': {'enabled': True, 'resources': {'requests': {'memory': '6144Mi', 'cpu': '900m'}, 'limits': {'memory': '6144Mi', 'cpu': '3000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-com-ecim-mscm': {'enabled': True, 'resources': {'requests': {'memory': '7392Mi', 'cpu': '1200m'}, 'limits': {'memory': '7692Mi', 'cpu': '4000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-comecimpolicy': {'enabled': True, 'resources': {'requests': {'memory': '4320Mi', 'cpu': '600m'}, 'limits': {'memory': '4620Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-eventbasedclient': {'enabled': True, 'resources': {'requests': {'memory': '4320Mi', 'cpu': '600m'}, 'limits': {'memory': '4620Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-elex': {'enabled': True, 'resources': {'requests': {'memory': '1000Mi', 'cpu': '200m'}, 'limits': {'memory': '2000Mi', 'cpu': '500m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-flowautomation': {'enabled': True, 'resources': {'requests': {'memory': '3296Mi', 'cpu': '600m'}, 'limits': {'memory': '3596Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-fls': {'enabled': True, 'resources': {'requests': {'memory': '4096Mi', 'cpu': '600m'}, 'limits': {'memory': '4096Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '2000m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-fm-alarm-processing': {'enabled': True, 'resources': {'requests': {'memory': '8192Mi', 'cpu': '1200m'}, 'limits': {'memory': '8192Mi', 'cpu': '4000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-fm-service': {'enabled': True, 'resources': {'requests': {'memory': '8192Mi', 'cpu': '1200m'}, 'limits': {'memory': '8192Mi', 'cpu': '4000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-ip-service-management': {'enabled': True, 'resources': {'requests': {'memory': '3296Mi', 'cpu': '300m'}, 'limits': {'memory': '3596Mi', 'cpu': '1000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-kpi-calc-serv': {'enabled': True, 'resources': {'requests': {'memory': '7692Mi', 'cpu': '600m'}, 'limits': {'memory': '8192Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-lcmservice': {'enabled': True, 'resources': {'requests': {'memory': '3296Mi', 'cpu': '300m'}, 'limits': {'memory': '3596Mi', 'cpu': '1000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-medrouter': {'enabled': True, 'resources': {'requests': {'memory': '4320Mi', 'cpu': '600m'}, 'limits': {'memory': '4620Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-msap': {'enabled': True, 'resources': {'requests': {'memory': '4320Mi', 'cpu': '600m'}, 'limits': {'memory': '4620Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-mscm': {'enabled': True, 'resources': {'requests': {'memory': '7392Mi', 'cpu': '1200m'}, 'limits': {'memory': '7692Mi', 'cpu': '4000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-mscmip': {'enabled': True, 'resources': {'requests': {'memory': '6668Mi', 'cpu': '1200m'}, 'limits': {'memory': '6668Mi', 'cpu': '4000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-msfm': {'enabled': True, 'resources': {'requests': {'memory': '5644Mi', 'cpu': '600m'}, 'limits': {'memory': '6144Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-mspm': {'enabled': True, 'resources': {'requests': {'memory': '7392Mi', 'cpu': '1200m'}, 'limits': {'memory': '7692Mi', 'cpu': '4000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-mspmip': {'enabled': True, 'resources': {'requests': {'memory': '7392Mi', 'cpu': '1200m'}, 'limits': {'memory': '7692Mi', 'cpu': '4000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-mssnmpcm': {'enabled': True, 'resources': {'requests': {'memory': '4320Mi', 'cpu': '1200m'}, 'limits': {'memory': '4620Mi', 'cpu': '4000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-nedo-serv': {'enabled': True, 'resources': {'requests': {'memory': '4320Mi', 'cpu': '600m'}, 'limits': {'memory': '4620Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-networkexplorer': {'enabled': True, 'resources': {'requests': {'memory': '6144Mi', 'cpu': '1200m'}, 'limits': {'memory': '6144Mi', 'cpu': '4000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-openidm': {'enabled': True, 'resources': {'requests': {'memory': '4096Mi', 'cpu': '600m'}, 'limits': {'memory': '4096Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-pki-ra-service': {'enabled': True, 'resources': {'requests': {'memory': '4320Mi', 'cpu': '600m'}, 'limits': {'memory': '4620Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-pmic-router-policy': {'enabled': True, 'resources': {'requests': {'memory': '4320Mi', 'cpu': '600m'}, 'limits': {'memory': '4620Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-pmservice': {'enabled': True, 'resources': {'requests': {'memory': '6144Mi', 'cpu': '600m'}, 'limits': {'memory': '6144Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '2000m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-cellserv': {'enabled': True, 'resources': {'requests': {'memory': '4320Mi', 'cpu': '600m'}, 'limits': {'memory': '4620Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-security-service': {'enabled': True, 'resources': {'requests': {'memory': '5344Mi', 'cpu': '600m'}, 'limits': {'memory': '5644Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-sps-service': {'enabled': True, 'resources': {'requests': {'memory': '4320Mi', 'cpu': '300m'}, 'limits': {'memory': '4620Mi', 'cpu': '1000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-shmservice': {'enabled': True, 'resources': {'requests': {'memory': '5344Mi', 'cpu': '600m'}, 'limits': {'memory': '5644Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-smrs-service': {'enabled': True, 'resources': {'requests': {'memory': '7362Mi', 'cpu': '1200m'}, 'limits': {'memory': '7692Mi', 'cpu': '4000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-uiservice': {'enabled': True, 'resources': {'requests': {'memory': '5120Mi', 'cpu': '600m'}, 'limits': {'memory': '5120Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-web-push-service': {'enabled': True, 'resources': {'requests': {'memory': '5096Mi', 'cpu': '300m'}, 'limits': {'memory': '5096Mi', 'cpu': '1000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-supervisionclient': {'enabled': True, 'resources': {'requests': {'memory': '3296Mi', 'cpu': '600m'}, 'limits': {'memory': '3596Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-visinaming-sb': {'enabled': True, 'resources': {'requests': {'memory': '2048Mi', 'cpu': '600m'}, 'limits': {'memory': '2048Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-msnetlog': {'enabled': True, 'resources': {'requests': {'memory': '4096Mi', 'cpu': '600m'}, 'limits': {'memory': '4096Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-node-plugins': {'enabled': True, 'resources': {'requests': {'memory': '3296Mi', 'cpu': '600m'}, 'limits': {'memory': '3596Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-shm-core-service': {'enabled': True, 'resources': {'requests': {'memory': '5344Mi', 'cpu': '600m'}, 'limits': {'memory': '5644Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-mssnmpfm': {'enabled': True, 'resources': {'requests': {'memory': '7392Mi', 'cpu': '1200m'}, 'limits': {'memory': '7692Mi', 'cpu': '4000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-msapgfm': {'enabled': True, 'resources': {'requests': {'memory': '4320Mi', 'cpu': '600m'}, 'limits': {'memory': '4620Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-import-export-service': {'enabled': True, 'resources': {'requests': {'memory': '7392Mi', 'cpu': '1200m'}, 'limits': {'memory': '7692Mi', 'cpu': '4000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-kpi-service': {'enabled': True, 'resources': {'requests': {'memory': '5644Mi', 'cpu': '600m'}, 'limits': {'memory': '6144Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-mscmapg': {'enabled': True, 'resources': {'requests': {'memory': '7392Mi', 'cpu': '1200m'}, 'limits': {'memory': '7692Mi', 'cpu': '4000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-nodecli': {'enabled': True, 'resources': {'requests': {'memory': '3296Mi', 'cpu': '350m'}, 'limits': {'memory': '3596Mi', 'cpu': '1250m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-winfiol-sg': {'enabled': False, 'resources': {'requests': {'memory': '7692Mi', 'cpu': '600m'}, 'limits': {'memory': '8192Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-dpmediation': {'enabled': True, 'resources': {'requests': {'memory': '3296Mi', 'cpu': '600m'}, 'limits': {'memory': '3596Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-domain-proxy-coordinator': {'enabled': True, 'resources': {'requests': {'memory': '4320Mi', 'cpu': '600m'}, 'limits': {'memory': '4620Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-general-scripting': {'enabled': True, 'resources': {'requests': {'memory': '20280Mi', 'cpu': '1200m'}, 'limits': {'memory': '20280Mi', 'cpu': '4000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-nb-fm-snmp': {'enabled': True, 'resources': {'requests': {'memory': '4320Mi', 'cpu': '600m'}, 'limits': {'memory': '4620Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-mskpirt': {'enabled': True, 'resources': {'requests': {'memory': '4320Mi', 'cpu': '600m'}, 'limits': {'memory': '4620Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-nbi-bnsi-fm': {'enabled': True, 'resources': {'requests': {'memory': '4096Mi', 'cpu': '600m'}, 'limits': {'memory': '4096Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-visinaming-nb': {'enabled': True, 'resources': {'requests': {'memory': '2048Mi', 'cpu': '600m'}, 'limits': {'memory': '2048Mi', 'cpu': '2000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-sa-service': {'enabled': True, 'resources': {'requests': {'memory': '4096Mi', 'cpu': '600m'}, 'limits': {'memory': '4096Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-element-manager': {'enabled': False, 'resources': {'requests': {'memory': '8192Mi', 'cpu': '1200m'}, 'limits': {'memory': '8192Mi', 'cpu': '4000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-ops': {'enabled': False, 'resources': {'requests': {'memory': '3596Mi', 'cpu': '600m'}, 'limits': {'memory': '4096Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}, 'persistentVolumeClaim': {'size': '1Gi'}}, 'eric-enmsg-fm-history': {'enabled': True, 'resources': {'requests': {'memory': '6144Mi', 'cpu': '600m'}, 'limits': {'memory': '6144Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-dlms': {'enabled': True, 'resources': {'requests': {'memory': '4096Mi', 'cpu': '300m'}, 'limits': {'memory': '4096Mi', 'cpu': '1000m'}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-dc-history': {'enabled': True, 'resources': {'requests': {'memory': '4096Mi', 'cpu': '300m'}, 'limits': {'memory': '4096Mi', 'cpu': '1000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enmsg-identity-mgmt-service': {'enabled': True, 'resources': {'requests': {'memory': '4320Mi', 'cpu': '600m'}, 'limits': {'memory': '4620Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enm-omnidaemon': {'enabled': True, 'resources': {'requests': {'cpu': '567m'}, 'limits': {'cpu': '1700m'}}}, 'eric-enmsg-itservices': {'enabled': True, 'resources': {'requests': {'memory': '3596Mi', 'cpu': '300m'}, 'limits': {'memory': '4096Mi', 'cpu': '1200m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enm-int-log-transformer': {'enabled': True, 'eric-log-transformer': {'enabled': True, 'imageCredentials': {'repoPath': 'proj-enm/proj-adp-log-released'}}}, 'eric-enmsg-nb-alarm-irp-agent-corba': {'enabled': True, 'resources': {'requests': {'memory': '4096Mi', 'cpu': '600m'}, 'limits': {'memory': '5120Mi', 'cpu': '2000m'}, 'httpd': {'enabled': True, 'requests': {'memory': '400Mi', 'cpu': '250m'}, 'limits': {'memory': '1000Mi', 'cpu': '500m'}}, 'monitoring': {'enabled': True, 'requests': {'memory': '200Mi', 'cpu': '50m'}, 'limits': {'memory': '300Mi', 'cpu': '200m'}}}}, 'eric-enm-credm-controller': {'enabled': True}}
rcd_cache_path = '/var/tmp/rcd-cache/'
VERSION = CVersion(Version('22.01', '22.01.33', (22, 1, 33, 0)), None, False)
VARIANT = "eric-enm-integration-extra-large-production-values"
EIC_TMP_DIR = 'eic_tmp'
CONFIG_EXAMPLE = Config('data',
                        {'eric-enm-integration-production-values':
                             ('Small Cloud Native ENM', 'Small cENM'),
                         'eric-enm-integration-extra-large-production-values':
                             ('Extra-Large Cloud Native ENM', 'Extra-Large cENM')})


@patch('generator.requests.get')
@patch('generator.get_csar_info')
@patch('generator.get_drop_content')
def test_provision_rcd(m_get_drop_content, m_csar_info, m_request):
    try:
        if os.path.exists(rcd_cache_path):
            shutil.rmtree(rcd_cache_path)
            os.mkdir(rcd_cache_path)
        m_get_drop_content.return_value = drop_content
        m_csar_info.return_value = csar_info
        m_request.return_value.text = json.dumps(csar_values_file)
        yaml_load = None

        with open(config_yml_path, 'r') as stream:
            yaml_load =yaml.safe_load(stream)

        generator.config=Config.parse(yaml_load)
        generator.jstorage = output_json.Storage(generator.config)

        provision_rcd('21.13.97', 'False')

        assert os.path.exists(data_json_path) == 1
        assert os.path.exists(index_json_path) == 1
        result = json.load(open(data_json_path))
        exp_result = json.load(open(expected_data_json_path))
        assert sorted(result.items()) == sorted(exp_result.items())
    finally:
        if os.path.exists(index_json_path):
            os.remove(index_json_path)
        if os.path.exists(data_json_path):
            os.remove(data_json_path)


@patch('generator.requests.get')
@patch('generator.get_csar_info')
@patch('generator.get_drop_content')
def test_provision_rcd_product_set_exists(m_get_drop_content, m_csar_info, m_request, caplog):
    m_get_drop_content.return_value = drop_content
    m_csar_info.return_value = csar_info
    m_request.return_value.text = json.dumps(csar_values_file)
    yaml_load = None

    with open(config_yml_path, 'r') as stream:
        yaml_load =yaml.safe_load(stream)
    import logging
    logging.getLogger().setLevel(logging.INFO)
    generator.config=Config.parse(yaml_load)
    generator.jstorage = output_json.Storage(generator.config)

    provision_rcd('21.11.100', 'False')

    out = caplog.text
    assert 'Output file already exists. Nothing to do.' in out


def test_setup_client_cluster_requirements_file_not_found(fs):
    version = CVersion(psv=Version(drop='21.13', version='21.13.97', raw=(21, 13, 97, 0)), release=None, present=False)
    s = Summary()
    with pytest.raises(FileNotFoundError):
        setup_client_cluster_requirements(version, s)


def test_validate_pdb_incorrect_pdb_type_replicas_2():
    errors = {}
    wl = WL('monitoring','eric-pm-server', 'StatefulSet', '', 2,
            [Container('monitoring', 'logshipper', 'eric-log-shipper:5.7.0-12', ContainerRR(100, 200, 100.0, 200.0, 0, 0))],
            ['storage-volume-eric-pm-server'], {},
            {}, WLRR(1300, 3600, 5236.0, 10504.0, 0, 0), True, PDB('monitoring', 'eric-pm-server', Selector({}), 'minAvailable', 0))
    wl_pdb = PDB('monitoring', 'eric-pm-server', Selector({('app', 'eric-pm-server')}), 'minAvailable', 0)
    validate_pdb(wl, wl_pdb, errors)
    assert 'Incorrect Pod Disruption Budget type \'minAvailable\' it must be set to maxUnavailable.' in errors['eric-pm-server']


def test_validate_pdb_incorrect_pdb_type_replicas_1():
    errors = {}
    wl = WL('monitoring','eric-pm-server', 'StatefulSet', '', 1,
            [Container('monitoring', 'logshipper', 'eric-log-shipper:5.7.0-12', ContainerRR(100, 200, 100.0, 200.0, 0, 0))],
            ['storage-volume-eric-pm-server'], {},
            {}, WLRR(1300, 3600, 5236.0, 10504.0, 0, 0), True, PDB('monitoring', 'eric-pm-server', Selector({}), 'minAvailable', 0))
    wl_pdb = PDB('monitoring', 'eric-pm-server', Selector({('app', 'eric-pm-server')}), 'minAvailable', 0)
    validate_pdb(wl, wl_pdb, errors)
    assert 'eric-pm-server' not in errors


def test_validate_pdb_incorrect_pdb_max_unavailable():
    errors = {}
    wl = WL('monitoring','eric-pm-server', 'StatefulSet', '', 2,
            [Container('monitoring', 'logshipper', 'eric-log-shipper:5.7.0-12', ContainerRR(100, 200, 100.0, 200.0, 0, 0))],
            ['storage-volume-eric-pm-server'], {},
            {}, WLRR(1300, 3600, 5236.0, 10504.0, 0, 0), True, PDB('monitoring', 'eric-pm-server', Selector({}), 'minAvailable', 0))
    wl_pdb = PDB('monitoring', 'eric-pm-server', Selector({('app', 'eric-pm-server')}), 'maxUnavailable', 0)
    validate_pdb(wl, wl_pdb, errors)
    assert 'Incorrect maxUnavailable value \'0\' for Pod Disruption Budget it must be set to 1.' in errors['eric-pm-server']


def test_validate_pdb_incorrect_pdb_not_set():
    errors = {}
    wl = WL('monitoring','eric-pm-server', 'StatefulSet', '', 2,
            [Container('monitoring', 'logshipper', 'eric-log-shipper:5.7.0-12', ContainerRR(100, 200, 100.0, 200.0, 0, 0))],
            ['storage-volume-eric-pm-server'], {},
            {}, WLRR(1300, 3600, 5236.0, 10504.0, 0, 0), True, PDB('monitoring', 'eric-pm-server', Selector({}), 'minAvailable', 0))
    wl_pdb = PDB('monitoring', 'eric-pm-server', Selector({('app', 'eric-pm-server')}), '', 0)
    validate_pdb(wl, wl_pdb, errors)
    assert 'Pod Disruption Budget not specified.' in errors['eric-pm-server']


def test_optional_value_pack():
    s = Summary()
    optional_apps = [{'version': 21.17, 'value_packs':
        [{'name': 'Event Based Statistics for LTE (EBS-L) and MME (EBS-N)', 'tag': 'value_pack_ebs_ln',
          'description': 'Event Based Statistics for LTE and NR contains ebs-controller, '
                         'ebs-flow and ebs-topology services',
          'variant': 'eric-enm-integration-extra-large-production-values',
          'applications': [{'name': 'ebscontroller'}, {'name': 'ebsflow'}, {'name': 'ebstopology'}],
          'jobs': ['eric-enm-models-ebs-job']},
         {'name': 'Event Based Statistics for MME (EBS-M)', 'tag': 'value_pack_ebs_m',
          'description': 'Event Based Statistics for MME contains ebs-controller and ebs-flow services.',
          'variant': 'eric-enm-integration-extra-large-production-values',
          'applications': [{'name': 'ebscontroller'}, {'name': 'ebsflow'}], 'jobs': ['eric-enm-models-ebs-job']}]}]
    expected_optional_value_pack_output = [
        {
            "name": "Event Based Statistics for LTE (EBS-L) and MME (EBS-N)",
            "tag": "value_pack_ebs_ln",
            "description": "Event Based Statistics for LTE and NR contains ebs-controller, ebs-flow and ebs-topology services",
            "variant": "eric-enm-integration-extra-large-production-values",
            "applications": [
                {
                    "name": "ebscontroller"
                },
                {
                    "name": "ebsflow"
                },
                {
                    "name": "ebstopology"
                }
            ],
            "jobs": [
                "eric-enm-models-ebs-job"
            ],
            "app_enabled": False
        },
        {
            "name": "Event Based Statistics for MME (EBS-M)",
            "tag": "value_pack_ebs_m",
            "description": "Event Based Statistics for MME contains ebs-controller and ebs-flow services.",
            "variant": "eric-enm-integration-extra-large-production-values",
            "applications": [
                {
                    "name": "ebscontroller"
                },
                {
                    "name": "ebsflow"
                }
            ],
            "jobs": [
                "eric-enm-models-ebs-job"
            ],
            "app_enabled": False
        }
    ]
    prepare_optional_value_packs(VERSION, s, VARIANT, CONFIG_EXAMPLE, optional_apps)

    assert expected_optional_value_pack_output == s.optional_value_packs


def test_optional_value_pack_not_applicable_to_version():
    s = Summary()
    optional_apps = [{'version': 100.00, 'value_packs':
        [{'name': 'Event Based Statistics for LTE (EBS-L) and MME (EBS-N)', 'tag': 'value_pack_ebs_ln',
          'description': 'Event Based Statistics for LTE and NR contains ebs-controller, '
                         'ebs-flow and ebs-topology services',
          'variant': 'eric-enm-integration-extra-large-production-values',
          'applications': [{'name': 'ebscontroller'}, {'name': 'ebsflow'}, {'name': 'ebstopology'}],
          'jobs': ['eric-enm-models-ebs-job']},
         {'name': 'Event Based Statistics for MME (EBS-M)', 'tag': 'value_pack_ebs_m',
          'description': 'Event Based Statistics for MME contains ebs-controller and ebs-flow services.',
          'variant': 'eric-enm-integration-extra-large-production-values',
          'applications': [{'name': 'ebscontroller'}, {'name': 'ebsflow'}], 'jobs': ['eric-enm-models-ebs-job']}]}]
    expected_optional_value_pack_output = []
    prepare_optional_value_packs(VERSION, s, VARIANT, CONFIG_EXAMPLE, optional_apps)
    assert expected_optional_value_pack_output == s.optional_value_packs


def test_optional_value_pack_one_app_enabled_():
    s = Summary()
    optional_apps = [
        {'version': 21.17,
         'value_packs':[
             {
                 'name': 'Event Based Statistics for LTE (EBS-L) and MME (EBS-N)',
                 'tag': 'value_pack_ebs_ln',
                 'description': 'Event Based Statistics for LTE and NR contains ebs-controller, '
                                'ebs-flow and ebs-topology services',
                 'variant': 'eric-enm-integration-extra-large-production-values',
                 'applications': [
                     {'name': 'ebscontroller'},
                     {'name': 'ebsflow'},
                     {'name': 'ebstopology'}],
                 'jobs': ['eric-enm-models-ebs-job'],
                 'app_enabled': True
             },
             {
                 'name': 'Event Based Statistics for MME (EBS-M)',
                 'tag': 'value_pack_ebs_m',
                 'description': 'Event Based Statistics for MME contains ebs-controller and ebs-flow services.',
                 'variant': 'eric-enm-integration-extra-large-production-values',
                 'applications': [
                     {'name': 'ebscontroller'},
                     {'name': 'ebsflow'}
                 ],
                 'jobs': ['eric-enm-models-ebs-job']}]}]
    expected_optional_value_pack_output = [
        {
            "name": "Event Based Statistics for LTE (EBS-L) and MME (EBS-N)",
            "tag": "value_pack_ebs_ln",
            "description": "Event Based Statistics for LTE and NR contains ebs-controller, ebs-flow and ebs-topology services",
            "variant": "eric-enm-integration-extra-large-production-values",
            "applications": [
                {
                    "name": "ebscontroller"
                },
                {
                    "name": "ebsflow"
                },
                {
                    "name": "ebstopology"
                }
            ],
            "jobs": [
                "eric-enm-models-ebs-job"
            ],
            "app_enabled": True
        },
        {
            "name": "Event Based Statistics for MME (EBS-M)",
            "tag": "value_pack_ebs_m",
            "description": "Event Based Statistics for MME contains ebs-controller and ebs-flow services.",
            "variant": "eric-enm-integration-extra-large-production-values",
            "applications": [
                {
                    "name": "ebscontroller"
                },
                {
                    "name": "ebsflow"
                }
            ],
            "jobs": [
                "eric-enm-models-ebs-job"
            ],
            "app_enabled": False
        }
    ]
    prepare_optional_value_packs(VERSION, s, VARIANT, CONFIG_EXAMPLE, optional_apps)

    assert expected_optional_value_pack_output == s.optional_value_packs


def test_optional_value_pack_not_valid_variant():
    s = Summary()
    optional_apps = [{'version': 21.07, 'value_packs':
        [{'name': 'Event Based Statistics for LTE (EBS-L) and MME (EBS-N)', 'tag': 'value_pack_ebs_ln',
          'description': 'Event Based Statistics for LTE and NR contains ebs-controller, '
                         'ebs-flow and ebs-topology services',
          'variant': 'NOT-VALID-VARIANT',
          'applications': [{'name': 'ebscontroller'}, {'name': 'ebsflow'}, {'name': 'ebstopology'}],
          'jobs': ['eric-enm-models-ebs-job']},
         {'name': 'Event Based Statistics for MME (EBS-M)', 'tag': 'value_pack_ebs_m',
          'description': 'Event Based Statistics for MME contains ebs-controller and ebs-flow services.',
          'variant': 'eric-enm-integration-extra-large-production-values',
          'applications': [{'name': 'ebscontroller'}, {'name': 'ebsflow'}], 'jobs': ['eric-enm-models-ebs-job']}]}]

    with pytest.raises(SystemExit) as e:
        prepare_optional_value_packs(VERSION, s, VARIANT, CONFIG_EXAMPLE, optional_apps)

    assert e.type == SystemExit


def test_skip_validation_errors_for_sgs_is_ebs_skipped():
    validation_errors = {"stateless": {
      "domainproxy-httpd": [
        "No resource requests are specified for container.",
        "No resource limits are specified for container."
      ],
      "ebsflow": [
        "No affinity value set.",
        "Update strategy rollingUpdate maxUnavailable should be set to 1.",
        "Incorrect maxUnavailable value '6' for Pod Disruption Budget it must be set to 1."
      ],
    }
    }
    skip_validation_errors_for_sgs(validation_errors)
    assert 'ebsflow' not in validation_errors['stateless']


def test_skip_validation_errors_for_sgs_resource_requests_container():
    validation_errors = {"stateless": {
      "domainproxy-httpd": [
        "No resource requests are specified for container.",
        "No resource limits are specified for container."
      ],
      "ebsflow": [
        "No affinity value set.",
        "Update strategy rollingUpdate maxUnavailable should be set to 1.",
        "Incorrect maxUnavailable value '6' for Pod Disruption Budget it must be set to 1.",
        "No resource requests are specified for container."
      ],
    }
    }
    skip_validation_errors_for_sgs(validation_errors)
    assert 'ebsflow'  in validation_errors['stateless']
    assert len(validation_errors['stateless']['ebsflow']) == 1 and  "No resource requests are specified for container."  in validation_errors['stateless']['ebsflow']


def test_skip_validation_errors_for_sgs_without_ebs():
    validation_errors = {"stateless": {
      "domainproxy-httpd": [
        "No resource requests are specified for container.",
        "No resource limits are specified for container."
      ]
    }
    }
    expected_validations_error_result = validation_errors.copy()
    skip_validation_errors_for_sgs(validation_errors)
    assert validation_errors['stateless'] == expected_validations_error_result['stateless']

@patch('generator.get_helm_file_info')
def test_provision_eic_rcd(m_helm_file_info):
    try:
        if os.path.exists(rcd_cache_path):
            shutil.rmtree(rcd_cache_path)
            os.mkdir(rcd_cache_path)

        releases_dict = {
            'dummy-app': {
            'name': 'dummy-app',
            'version': 'dummy-version',
            'chart': 'dummy-chart',
            'labels': 'dummy-label',
            'installed': True,
            'condition': 'dummy-enabled',
            'namespace': 'dummy-ns',
            'values': ['./values-templates/dummy.gotmpl'],
            'url': 'dummy-url'
            }
        }

        csar_dict = {
            'dummy-app': 'dummy-app'
        }

        templates = [
            {"kind":"Deployment","metadata":{"name":"dummy-app","labels":{"app.kubernetes.io/instance": "dummy-app"}},"spec":{"replicas":3,"template":{"metadata":{"labels":{"app.kubernetes.io/instance":"dummy-app"}},"spec":{"containers":[{"name":"nginx","image":"nginx:1.14.2","resources":{"requests":{"memory":"64Mi","cpu":"250m"},"limits":{"memory":"128Mi","cpu":"500m"}}}]}}}},
            {"kind":"Deployment","metadata":{"labels":{"app":"nginx"},"name":"dummy-app"},"spec":{"replicas":3,"template":{"metadata":{"labels":{"app.kubernetes.io/instance":"dummy-app-2","sidecar.istio.io/inject":"true"}},"annotations":{"sidecar.istio.io/proxyCPU":"2000m","sidecar.istio.io/proxyCPULimit":"2000m","sidecar.istio.io/proxyMemory":"256Mi","sidecar.istio.io/proxyMemoryLimit":"4Gi"},"spec":{"containers":[{"image":"nginx:1.14.2","name":"nginx","resources":{"limits":{"cpu":"500m","memory":"128Mi"},"requests":{"cpu":"250m","memory":"64Mi"}}}]}}}},
            {"data": {"values": '{"resources": {"istio-proxy": {"limits": {"cpu": "2000m", "memory":"1024Mi"}, "requests": {"cpu": "100m", "memory": "128Mi"}}}}'}, "kind": "ConfigMap", "metadata": {"labels": {"app.kubernetes.io/instance": "dummy-app"}, "name": "istio-sidecar-injector-a"}},
            {"kind": "Kafka", "metadata": {"labels": {"app.kubernetes.io/instance": "dummy-app"}, "name": "dummy-crd"}, "spec": {"entityOperator": {"topicOperator": {"resources": {"limits": {"cpu": 1, "memory": "1Gi"}, "requests": {"cpu": "200m", "memory": "256Mi"}}}, "userOperator": {"resources": {"limits": {"cpu": 1, "memory": "1Gi"}, "requests": {"cpu": "200m", "memory": "256Mi"}}}}, "kafka": {"image": "dummy", "replicas": 3, "resources": {"limits": {"cpu": 2, "memory": "2Gi"}, "requests": {"cpu": 1, "memory": "512Mi"}},"storage": {"volumes": [{"id": "0","size": "50Gi"}]}},"zookeeper":{"image":"dummy","replicas":3,"storage":{"size":"2Gi"},"resources":{"requests":{"memory":"512Mi","cpu":"200m"},"limits":{"memory":"2Gi","cpu":1}}}}},
            {"kind":"CassandraCluster","metadata":{"labels":{"app.kubernetes.io/instance":"dummy-app"},"name":"dummy-cassandra"},"spec":{"dataCenters":[{"cassandra":{"imageDetails":{"image":"dummy_image"},"resourceRequirements":{"limits":{"cpu":"4","memory":"2Gi"},"requests":{"cpu":"1","memory":"2Gi"}}},"name":"datacenter1","replicas":1,"backupAndRestore":{"brsc":{"imageDetails":{"image":"armdocker.rnd.ericsson.se/proj-bssf/eric-data-wide-column-database-cd-brsc:1.2.80-6"},"resourceRequirements":{"requests":{"memory":"512Mi","cpu":"1"},"limits":{"memory":"512Mi","cpu":"4"}}}},"persistence":{"dataVolume":{"persistentVolumeClaim":{"size":"500Mi"}}}}],"podTemplate":{"metadata":{"labels":{"app.kubernetes.io/instance":"dummy-app"}}}}}
        ]
        m_helm_file_info.return_value = [releases_dict, csar_dict, templates]
        yaml_load = None

        with open(config_yml_path, 'r') as stream:
            yaml_load =yaml.safe_load(stream)

        generator.config=Config.parse(yaml_load)
        generator.jstorage = output_json.Storage(generator.config)
        generator.username = "dummy_user"
        generator.password = "dummy_password"
        provision_eic_rcd('2.23.0-120', 'False')
        assert os.path.exists(eic_data_json_apps_file_path) == 1
        assert os.path.exists(eic_data_json_dummy_app_path) == 1
    finally:
        if os.path.exists(eic_data_json_dir_path):
            shutil.rmtree(eic_data_json_dir_path)

@patch('generator.get_helm_file_info')
def test_provision_eic_rcd_release(m_helm_file_info):
    try:
        release_version = '2.23.0-121'
        releases_dict = {
            'dummy-app': {
            'name': 'dummy-app',
            'version': 'dummy-version',
            'chart': 'dummy-chart',
            'labels': 'dummy-label',
            'installed': True,
            'condition': 'dummy-enabled',
            'namespace': 'dummy-ns',
            'values': ['./values-templates/dummy.gotmpl'],
            'url': 'dummy-url'
            }
        }
        csar_dict = {
            'dummy-app': 'dummy-app'
        }
        templates = [{'dummy-template': 'dummy-template'}]
        m_helm_file_info.return_value = [releases_dict, csar_dict, templates]
        yaml_load = None

        with open(config_yml_path, 'r') as stream:
            yaml_load =yaml.safe_load(stream)

        generator.config=Config.parse(yaml_load)
        generator.jstorage = output_json.Storage(generator.config)
        generator.username = "dummy_user"
        generator.password = "dummy_password"
        output_dir_path = os.path.join(eic_data_integration_values_path, release_version)
        expected_apps_json_path = os.path.join(output_dir_path, 'apps.json')
        expected_dummy_app_path = os.path.join(output_dir_path, 'dummy-app.json')
        provision_eic_rcd(release_version, 'True')
        assert os.path.exists(expected_apps_json_path) == 1
        assert os.path.exists(expected_dummy_app_path) == 1
    finally:
        if os.path.exists(output_dir_path):
            shutil.rmtree(output_dir_path)

@patch('generator.get_helm_file_info')
def test_provision_eic_rcd_missing_userame_env(m_helm_file_info):
    releases_dict = { 'release_name': 'release_value'}
    csar_dict = {'dummy-app': 'dummy-app'}
    templates = [{'dummy-template': 'dummy-template'}]
    m_helm_file_info.return_value = [releases_dict, csar_dict, templates]
    yaml_load = None

    with open(config_yml_path, 'r') as stream:
        yaml_load =yaml.safe_load(stream)

    generator.config=Config.parse(yaml_load)
    generator.jstorage = output_json.Storage(generator.config)
    generator.username = None
    generator.password = None
    with pytest.raises(rcd_exceptions.MandatoryEnvironmentVariableNotSetError) as exc_info:
        provision_eic_rcd('2.23.0-120', 'False')
    assert str(exc_info.value) == "GERRIT_USERNAME environment variable is not set."

@patch('generator.get_helm_file_info')
def test_provision_eic_rcd_missing_pwd_env(m_helm_file_info):
    releases_dict = { 'release_name': 'release_value'}
    csar_dict = {'dummy-app': 'dummy-app'}
    templates = [{'dummy-template': 'dummy-template'}]
    m_helm_file_info.return_value = [releases_dict, csar_dict, templates]
    yaml_load = None

    with open(config_yml_path, 'r') as stream:
        yaml_load =yaml.safe_load(stream)

    generator.config=Config.parse(yaml_load)
    generator.jstorage = output_json.Storage(generator.config)
    generator.username = "dummy_user"
    generator.password = None
    with pytest.raises(rcd_exceptions.MandatoryEnvironmentVariableNotSetError) as exc_info:
        provision_eic_rcd('2.23.0-120', 'False')
    assert str(exc_info.value) == "GERRIT_PASSWORD environment variable is not set."

def test_add_istio_side_cars():
    s = EICSummary()
    yaml_load = None

    with open(eic_manifest_yml_path, 'r') as stream:
        yaml_load =yaml.safe_load(stream)

    add_istio_side_cars(yaml_load, s)
    assert len(s.istio_side_cars) == 1

def test_add_istio_side_cars_with_annotation():
    s = EICSummary()
    yaml_load = None

    with open(eic_manifest_with_annotation_yml_path, 'r') as stream:
        yaml_load =yaml.safe_load(stream)

    add_istio_side_cars(yaml_load, s)
    assert len(s.istio_side_cars) == 1

def test_clean_up_eic_tmp():
    clean_up_eic_tmp()
    current_directory = os.getcwd()
    current_directory_basename = os.path.basename(current_directory)
    assert current_directory_basename == EIC_TMP_DIR
    assert not os.listdir(current_directory)
    change_to_app_dir()

@patch('generator.fetch_helmfile_details')
@patch('generator.download_helmfile')
@patch('utils.utils.extract_tar_file')
@patch('generator.clean_up_eic_tmp')
@patch('generator.generate_optionality_maximum')
@patch('generator.build_manifest')
@patch('os.chdir')
def test_get_helm_file_info(m_os, m_build, m_gen, m_clean_up, m_extract, m_download, m_fetch):
    file_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_path)
    manifest_file_path = os.path.join(file_dir, "resources/eic/helmfile-test-data/manifest.yaml")

    releases_dict = {
        'dummy-app': {
        'name': 'dummy-app',
        'version': 'dummy-version',
        'chart': 'dummy-chart',
        'labels': 'dummy-label',
        'installed': True,
        'condition': 'dummy-enabled',
        'namespace': 'dummy-ns',
        'values': ['./values-templates/dummy.gotmpl'],
        'url': 'dummy-url'
        }
    }

    csar_dict = {
        'dummy-app': 'dummy-app'
    }

    m_fetch.return_value = [releases_dict, csar_dict]
    m_build.return_value = manifest_file_path

    values_file_path, values_contents = get_site_values_info()
    releases_dict, csar_dict, templates = get_helm_file_info('2.23.0-120', values_file_path)
    assert len(templates) == 1

def test_get_credentials():
   os.environ['GERRIT_USERNAME'] = 'dummy_user'
   os.environ['GERRIT_PASSWORD'] = "gAAAAABk8J2AhiVrTo04nZJgghJN4PVD0TaIitDkkCSep5XEzD1SCsJPwThN-oikDeN0ynp064Qx9F1PSQ0wFfzmdTFDI-Y8OQ=="
   username, password = get_credentials()
   assert username == 'dummy_user'
   assert password == 'dummy_pwd'
