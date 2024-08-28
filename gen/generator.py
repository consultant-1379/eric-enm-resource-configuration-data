#!/usr/bin/env python3
'''
This file loads the configuration needed for the product set file generation
and uses this configuration for generating product set files.
'''
import logging
import math
import os
import shutil
from pathlib import Path
import re
import json
import yaml
import requests
import rcd_exceptions
from cryptography.fernet import Fernet
from datasrc.ciportal import get_drop_content
from datasrc.csar import get_csar_info
from datasrc.helm import template
from datasrc.optionality import generate_optionality_maximum
from datasrc.helmfile import download_helmfile, fetch_helmfile_details, build_manifest
from datasrc.helmfile import get_all_templates, get_chart_templates
from model.chart import Chart
from model.config import Config, CVersion
from model.drop_content import DropContent
from model.resource_requirements import (PDB, PVC, WL, validate_pdb,
                                        UPDATE_STRATEGY_ROLLING_UPDATE_MAX_UNAVAILABLE_ERROR,
                                        NO_AFFINITY_VALUE_SET)
from model.summary import (ConfigMap, EricIngress, Ingress, Secret, Service,
                           Summary, EICSummary)
from model.values import Values
from model.version import Version
from output import output_json
from utils import utils

log = logging.getLogger('generator')
CONFIG_YAML_PATH = 'variant_config.yaml'
ENCODING_ASCII = "ascii"
LOAD_BALANCERS = 'load_balancers'

# EIC specific constants
EIC_OPTIONAL_APPS = []

EIC_HELM_FILE_DIR = "eric-eiae-helmfile"
EIC_HELM_FILE_NAME = "helmfile.yaml"
EIC_HELM_STATE_VALUES_FILE="build-environment/tags_true.yaml"
EIC_HELM_FILE_REPO = "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local"
EIC_TMP_DIR = 'eic_tmp'
EIC_SITE_VALUES_FILE = 'site_values.yaml'
EIC_ISTIO_SIDECAR_INJECTOR_A = "istio-sidecar-injector-a"
EIC_CRD_KAFKA = 'Kafka'
EIC_CRD_CASSANDRA = 'CassandraCluster'

EIC_CSAR_REPO = \
    "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars"

def change_to_app_dir():
    '''
    This function changes to the application directory
    '''
    file_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_path)
    parent_dir = os.path.dirname(file_dir)
    os.chdir(parent_dir)


def change_to_eic_tmp_dir():
    '''
    This function changes to eic tmp directory
    '''
    file_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_path)
    eic_tmp_dir = os.path.join(file_dir, EIC_TMP_DIR)
    os.chdir(eic_tmp_dir)


def get_site_values_info():
    '''
    This function gets the site value file contents and file path
    '''
    file_path = os.path.abspath(__file__)
    file_dir = os.path.dirname(file_path)
    site_values_file_path = os.path.join(file_dir, EIC_SITE_VALUES_FILE)

    if os.path.exists(site_values_file_path):
        with open(site_values_file_path, "r", encoding="utf-8") as values_file:
            contents = values_file.read()

    return site_values_file_path, contents


def clean_up_eic_tmp():
    '''
    This function removes all the files in eic_tmp dir.
    '''
    change_to_eic_tmp_dir()

    for variant_name in os.listdir(os.getcwd()):
        variant_path = os.path.join(os.getcwd(), variant_name)
        if os.path.isdir(variant_path):
            shutil.rmtree(variant_path, ignore_errors=True)
        elif os.path.isfile(variant_path):
            os.remove(variant_path)


def get_helm_file_info(product_set_version, values_file_path):
    '''
    This function downloads the helm file and
    fetches releases, CSARs and templates info
    '''
    clean_up_eic_tmp()
    download_helmfile(EIC_HELM_FILE_DIR, product_set_version,
                      EIC_HELM_FILE_REPO, username, password)

    helm_zip_file_name = f"{EIC_HELM_FILE_DIR}-{product_set_version}.tgz"
    utils.extract_tar_file(helm_zip_file_name, "./")
    os.chdir(EIC_HELM_FILE_DIR)
    releases_dict, csar_dict = fetch_helmfile_details(
        EIC_HELM_STATE_VALUES_FILE, EIC_HELM_FILE_NAME)

    helm_file_path = os.path.join(os.getcwd(), EIC_HELM_FILE_NAME)
    generate_optionality_maximum(helm_file_path, releases_dict)
    manifest_file_path = build_manifest(values_file_path, helm_file_path)
    templates = get_all_templates(manifest_file_path)

    return releases_dict, csar_dict, templates


def prepare_optional_value_packs(version, summary, variant, config_file, optional_applications):
    '''
    This function loads optional value packs for release versions.
    '''
    sorted_optional_apps = sorted(optional_applications, key=lambda k: k['version'], reverse=True)
    for release in sorted_optional_apps:
        if float(version.psv.drop) >= release['version']:
            for value_pack in release['value_packs']:
                if 'app_enabled' not in value_pack:
                    value_pack['app_enabled'] = False
                check_valid_variant(value_pack, config_file)
                update_optional_value_packs(summary, variant, value_pack)


def update_optional_value_packs(summary, variant, value_pack):
    '''
    This function add an optional value pack to the summary if applicable.
    '''
    if 'variant' not in value_pack or value_pack['variant'] == variant:
        if not any(v['name'] == value_pack['name'] for v in summary.optional_value_packs):
            summary.optional_value_packs.append(value_pack)


def check_valid_variant(value_pack, config_file):
    '''
    This function validates the provided variant.
    '''
    allowed_variants = list(config_file.variants)
    if 'variant' in value_pack and value_pack['variant'] not in allowed_variants:
        log.error("Variant %s does not exist in current variants: %s ",
                                value_pack['variant'], allowed_variants)
        raise SystemExit(1)


def set_bur_storage_requirements(bur_config_file, summary):
    '''
    Calculate Backup and Restore storage requirements for the product set.
    '''
    num_of_backups_on_external_storage = bur_config_file["backupsOnExternalStorage"]
    num_of_backups_on_bro_pvc = bur_config_file["backupsOnBroPvc"]
    num_of_rollbacks_on_bro_pvc = bur_config_file["rollbacksOnBroPvc"]

    full_backup_storage = 0
    full_backup_compressed_storage = 0

    rollback_storage = 0
    rollback_compressed_storage = 0

    defined_bro_pvc_size = 0
    for pvc in summary.pvcs:

        if pvc.name == 'backup-data-eric-ctrl-bro':
            defined_bro_pvc_size = pvc.pvc_resource_requirements.size

        bur_pvc = bur_config_file["pvcs"].get(pvc.name)
        if bur_pvc:
            pvc_size = pvc.pvc_resource_requirements.size
            backup_size = pvc_size * bur_pvc["pvcDataRatio"]
            full_backup_storage += backup_size
            full_backup_compressed_storage += backup_size / bur_pvc["compressionRatio"]
            if bur_pvc["rollback"]:
                rollback_storage += backup_size
                rollback_compressed_storage += backup_size / bur_pvc["compressionRatio"]

    bro_pvc_storage_req = num_of_backups_on_bro_pvc * math.ceil(full_backup_compressed_storage) + \
        num_of_rollbacks_on_bro_pvc * math.ceil(rollback_compressed_storage)
    external_storage_req = num_of_backups_on_external_storage \
                            * math.ceil(full_backup_compressed_storage)

    if defined_bro_pvc_size < bro_pvc_storage_req:
        log.warning('Defined BRO PVC Size (%d) is smaller than \
                        Backup Size Requirement (%d)', defined_bro_pvc_size, bro_pvc_storage_req)

    summary.overview.bur['number_of_full_backups_on_external_storage'] = \
                                num_of_backups_on_external_storage
    summary.overview.bur['number_of_full_backups_on_bro_pvc'] = num_of_backups_on_bro_pvc
    summary.overview.bur['number_of_rollbacks_on_bro_pvc'] = num_of_rollbacks_on_bro_pvc
    summary.overview.bur['storage_requirement_full_backups'] = math.ceil(full_backup_storage)
    summary.overview.bur['storage_requirement_full_backups_compressed'] = \
                                math.ceil(full_backup_compressed_storage)
    summary.overview.bur['storage_requirement_rollbacks'] = math.ceil(rollback_storage)
    summary.overview.bur['storage_requirement_rollbacks_compressed'] = \
                                math.ceil(rollback_compressed_storage)
    summary.overview.bur['bro_pvc_storage_requirement'] = math.ceil(bro_pvc_storage_req)
    summary.overview.bur['external_storage_requirement'] = math.ceil(external_storage_req)


def setup_client_cluster_requirements(version, summary):
    '''
    Includes the Client and Cluster requirements in the summary for a particular
    product set version.
    '''
    software_requirements = read_config_file('software_requirements_config.yml')
    sorted_software_requirements = sorted(software_requirements, key= Version.parse)
    requirements_temp = {'client': {}, 'cluster': {}, 'registry': {}}
    for software_version in sorted_software_requirements:
        if version.psv >= Version.parse(software_version):
            for requirement in software_requirements[software_version]:
                requirements_temp[requirement].update(
                        software_requirements[software_version][requirement])
    summary.overview.client = requirements_temp['client']
    summary.overview.cluster = requirements_temp['cluster']
    summary.overview.registry = requirements_temp['registry']


def setup_other_requirements(version, values, summary):
    '''
    Includes additional requirements in the product set file.
    '''
    other_requirements = read_config_file('other_requirements_config.yml')
    sorted_other_requirements = sorted(other_requirements, key=lambda k: k['version'])
    for release in sorted_other_requirements:
        if float(version.psv.drop) >= release['version']:
            for req, val in release['requirements'].items():
                summary.overview.other_requirements[req] = val

    # Count IP's required. The number of VIPs.
    ipv4_ips = dict(filter(lambda item: 'ipv6' not in item[0].lower(),
                    values.values['global']['vips'].items()))
    summary.overview.other_requirements['ips'] = len(ipv4_ips)

    ipv6_ips = dict(filter(lambda item: 'ipv6' in item[0].lower(),
                    values.values['global']['vips'].items()))
    summary.overview.other_requirements['ipv6s'] = len(ipv6_ips)


def read_config_file(file_name):
    '''
    Reads a specified config file from config folder and returns yaml object.
    '''
    try:
        file_dir = Path(__file__).parent.resolve()
        file_path = os.path.join(file_dir, 'config', file_name)
        with open(file_path, 'r', encoding=ENCODING_ASCII) as stream:
            return yaml.safe_load(stream)
    except FileNotFoundError:
        log.error('%s file not found!', file_name)
        raise


def basic_values_preparator(values):
    '''
    Initializes some default values in the values provided.
    '''
    values['global']['vips'] = {}
    values['global']['ip_version'] = 'Dual'
    values['global']['nodeSelector'] = {'testSelectorKey': 'testSelectorValue'}
    if 'tags' in values:
        for tag in values['tags']:
            values['tags'][tag] = True


def skip_validation_errors_for_sgs(validation_errors):
    '''
    This method accepts list of validation errors in cENM product set and
    excludes workloads to skip in validation errrors
    '''
    workloads_to_skip = {
        'stateless' : {
            'ebsflow': [
                'Incorrect maxUnavailable value \'\\d\' for '+
                'Pod Disruption Budget it must be set to 1.',
                UPDATE_STRATEGY_ROLLING_UPDATE_MAX_UNAVAILABLE_ERROR,
                NO_AFFINITY_VALUE_SET
                ]
        }
    }

    for chart, workloads in workloads_to_skip.items():
        if chart in validation_errors:
            for workload in workloads:
                all_errors = validation_errors[chart].pop(workload, [])
                errors_to_discard = '|'.join(workloads_to_skip[chart][workload])
                remaining_errors = [x for x in all_errors if not re.findall(errors_to_discard, x)]
                if remaining_errors:
                    validation_errors[chart][workload] = remaining_errors

# pylint: disable=too-many-arguments
def parse_charts(drop_content, values, summary, bur_config_file,
                 optional_applications, eic_product = False, eic_app_templates = None):
    '''
    This function parses the helm charts and extracts data from it.
    '''
    validation_errors = {}
    for chart in drop_content.charts:
        chart_validation_errors = {}
        wls = []
        pvcs = []
        pdbs = []
        log.info('  Handling Chart %s', chart.name)
        parse_templates(values, summary, chart, wls, pdbs,
                         pvcs, chart_validation_errors, bur_config_file, optional_applications,
                         eic_product, eic_app_templates)
        update_workloads_pdb(wls, pdbs, chart_validation_errors)
        log.info("    Processed: %3d  WLs | %3d PVCs | %3d PDBs", len(wls), len(pvcs), len(pdbs))
        summary.workloads += wls
        summary.pvcs += pvcs
        validation_errors[chart.alias] = chart_validation_errors
    total_load_balancers = summary.overview.other_requirements[LOAD_BALANCERS]
    summary.overview.other_requirements['ips'] += total_load_balancers
    summary.overview.other_requirements['ipv6s'] += total_load_balancers
    skip_validation_errors_for_sgs(validation_errors)
    summary.validation_errors = validation_errors


# pylint: disable=too-many-arguments
def parse_templates(values, summary, chart, wls, pdbs, pvcs, errors, bur_config_file,
                    optional_applications, eic_product = False, eic_app_templates = None):
    '''
    This functions parses metadata of each kind.
    '''
    if eic_product:
        templates = eic_app_templates
        skip_validate_update_strategy = True
    else:
        templates = template(values.values, chart.url)
        skip_validate_update_strategy = False

    for manifest in templates:
        kind = manifest['kind']
        if kind == 'ConfigMap':
            summary.config_maps.append(ConfigMap.from_manifest(chart.alias, manifest,
                                                               optional_applications))
            if eic_product and manifest['metadata']['name'] == EIC_ISTIO_SIDECAR_INJECTOR_A:
                get_istio_requests_limits(manifest, summary)

        elif kind == 'Secret':
            summary.secrets.append(Secret.from_manifest(chart.alias, manifest,
                                                        optional_applications))
        elif kind == 'Service':
            summary.services.append(Service.from_manifest(chart.alias, manifest,
                                                          optional_applications))
            if manifest['spec'].get('type') == 'LoadBalancer':
                current_load_balancers = summary.overview.other_requirements[LOAD_BALANCERS]
                summary.overview.other_requirements[LOAD_BALANCERS] = current_load_balancers + 1
        elif kind == 'Ingress':
            summary.ingresses.append(Ingress.from_manifest(chart.alias, manifest,
                                                           optional_applications))
        elif kind == 'EricIngress':
            summary.eric_ingresses.append(EricIngress.from_manifest(chart.alias, manifest,
                                                                    optional_applications))
        elif eic_product and kind == EIC_CRD_KAFKA:
            for cr_name in manifest['spec'].keys():
                workload, wlpvcs = WL.from_manifest(chart.alias, manifest, values.name, errors,
                                    bur_config_file, optional_applications,
                                    skip_validate_update_strategy, cr_name)
                wls.append(workload)
                pvcs += wlpvcs
        elif eic_product and kind == EIC_CRD_CASSANDRA:
            if 'dataCenters' in manifest['spec']:
                for data_center in manifest['spec']['dataCenters']:
                    workload, wlpvcs = WL.from_manifest(chart.alias, manifest, values.name, errors,
                    bur_config_file, optional_applications,
                    skip_validate_update_strategy, data_center)
                    wls.append(workload)
                    pvcs += wlpvcs
        elif kind in ['StatefulSet', 'Deployment', 'DaemonSet', 'Job', 'CronJob', 'RedisCluster']:
            workload, wlpvcs = WL.from_manifest(chart.alias, manifest, values.name, errors,
                                                bur_config_file, optional_applications,
                                                skip_validate_update_strategy)
            wls.append(workload)
            pvcs += wlpvcs
            if eic_product and kind in ['StatefulSet', 'Deployment']:
                add_istio_side_cars(manifest, summary)
        elif kind == 'PersistentVolumeClaim':
            pvcs.append(PVC.from_manifest(chart.alias, manifest, errors, bur_config_file))
        elif kind == 'PodDisruptionBudget':
            pdbs.append(PDB.from_manifest(chart.alias, manifest))


def add_istio_side_cars(manifest, summary):
    '''
    This function checks for istio side cars in the template and add them in summary
    '''
    wl_name = manifest.get('metadata', {}).get('name')
    if 'spec' in manifest:
        replicas = manifest['spec'].get('replicas', 1)

        path = ['spec', 'template', 'metadata', 'labels', 'sidecar.istio.io/inject']

        if utils.check_path_in_dict(manifest, path) and \
            manifest['spec']['template']['metadata'] ['labels'] \
                ['sidecar.istio.io/inject'] == 'true':

            istio_side_car = {"name": wl_name, "replicas": replicas}
            proxy_cpu_req_annot_path = ['spec', 'template', 'metadata',
                                        'annotations', 'sidecar.istio.io/proxyCPU']
            proxy_cpu_lim_annot_path = ['spec', 'template', 'metadata',
                                        'annotations', 'sidecar.istio.io/proxyCPULimit']
            proxy_mem_req_annot_path = ['spec', 'template', 'metadata',
                                        'annotations', 'sidecar.istio.io/proxyMemory']
            proxy_mem_lim_annot_path = ['spec', 'template', 'metadata',
                                        'annotations', 'sidecar.istio.io/proxyMemoryLimit']

            if utils.check_path_in_dict(manifest, proxy_cpu_req_annot_path):
                istio_side_car['cpu_request'] = utils.remove_units_from_k8s_resource(
                    manifest['spec']['template']['metadata'] \
                    ['annotations']['sidecar.istio.io/proxyCPU']
                )

            if utils.check_path_in_dict(manifest, proxy_cpu_lim_annot_path):
                istio_side_car['cpu_limit'] = utils.remove_units_from_k8s_resource(
                    manifest['spec']['template']['metadata'] \
                    ['annotations']['sidecar.istio.io/proxyCPULimit']
                )

            if utils.check_path_in_dict(manifest, proxy_mem_req_annot_path):
                mem_resource_str = manifest['spec']['template']['metadata'] \
                    ['annotations']['sidecar.istio.io/proxyMemory']

                if "Gi" in mem_resource_str:
                    mem_resource_str = utils.gib_to_mib(mem_resource_str)

                istio_side_car['mem_request'] = utils.remove_units_from_k8s_resource(mem_resource_str)


            if utils.check_path_in_dict(manifest, proxy_mem_lim_annot_path):
                mem_resource_str = manifest['spec']['template']['metadata'] \
                    ['annotations']['sidecar.istio.io/proxyMemoryLimit']

                if "Gi" in mem_resource_str:
                    mem_resource_str = utils.gib_to_mib(mem_resource_str)

                istio_side_car['mem_limit'] = utils.remove_units_from_k8s_resource(mem_resource_str)

            summary.istio_side_cars.append(istio_side_car)


def get_istio_requests_limits(manifest, summary):
    '''
    This function gets requests/limits for istio from config map
    '''
    path = ['data', 'values']
    if utils.check_path_in_dict(manifest, path):
        config_map_values = json.loads(manifest['data']['values'])
        istio_proxy_limits_path = ['resources', 'istio-proxy', 'limits']
        istio_proxy_requests_path = ['resources', 'istio-proxy', 'requests']

        if utils.check_path_in_dict(config_map_values, istio_proxy_limits_path):
            summary.istio_cpu_limit = config_map_values['resources']['istio-proxy']['limits']['cpu']
            summary.istio_mem_limit = config_map_values['resources']['istio-proxy']['limits']['memory']

        if utils.check_path_in_dict(config_map_values, istio_proxy_requests_path):
            summary.istio_cpu_request = config_map_values['resources']['istio-proxy']['requests']['cpu']
            summary.istio_mem_request = config_map_values['resources']['istio-proxy']['requests']['memory']


def update_workloads_pdb(wls, pdbs, errors):
    '''
    Update the pdb's in workload.
    '''
    more_than_one_pdb_specified='more than 1 Pod Disruption Budget specified.'
    for workload in wls:
        pdb_match_labels = list(filter(lambda pdb: pdb.selector.match(workload.labels), pdbs))
        if len(pdb_match_labels) > 1:
            errors.setdefault(workload.name, []).append(more_than_one_pdb_specified)
        if len(pdb_match_labels) > 0:
            wl_pdb= pdb_match_labels[0]
            workload.pdb = wl_pdb
            validate_pdb(workload, wl_pdb, errors)


def get_credentials():
    '''
    Get RCD functional user credentials
    '''
    gerrit_username = os.environ.get('GERRIT_USERNAME', None)
    gerrit_password = os.environ.get('GERRIT_PASSWORD', None)

    if gerrit_username and gerrit_password:
        password_byte_str = gerrit_password.encode('utf-8')
        fernet = Fernet(b'M4DJALVZCJLxUVi271328cY0IRK31y6KorgyK1orVxg=')
        gerrit_password = fernet.decrypt(password_byte_str).decode()
        os.environ['GERRIT_PASSWORD'] = gerrit_password

    return gerrit_username, gerrit_password

bur_config = read_config_file('bur_config.yaml')
optional_apps = read_config_file('optional_value_packs.yml')
config = Config.parse(read_config_file(CONFIG_YAML_PATH))
jstorage = output_json.Storage(config)
username, password = get_credentials()

def provision_rcd(product_set_version, is_release):
    '''
    Provision the product set into RCD.
    '''
    version = CVersion(Version.parse(product_set_version), is_release, False)

    log.info('Handling \x1b[1m%s\x1b[0m', version.psv.version)
    drop_content = DropContent.parse(
        get_drop_content(version.psv.drop, version.psv.version))

    log.info('Loading CSAR info')
    csar = get_csar_info(drop_content.csar)

    for variant in config.variants:
        csar.values_files.append(Values.parse(variant,
                                 requests.get(drop_content.values_file.replace(
                                            'eric-enm-integration-production-values',
                                             variant)).text))

    for values in csar.values_files:
        log.info('Handling \x1b[1m%s\x1b[0m',
                config.get_variant(values.name)[1])

        if version.psv.version in jstorage.variants[values.name]:
            log.info('  Output file already exists. Nothing to do.')
            log.debug('  JStorage for current variant: %s',
                    jstorage.variants[values.name])
            continue

        summary = Summary()
        csar_info = {}
        csar_info['images'] = csar.images
        csar_info['total_images_size'] = csar.total_images_size
        summary.csar = csar_info
        setup_client_cluster_requirements(version, summary)
        setup_other_requirements(version, values, summary)
        values.prepare(basic_values_preparator)
        parse_charts(drop_content, values, summary, bur_config, optional_apps)
        set_bur_storage_requirements(bur_config, summary)
        prepare_optional_value_packs(version, summary, values.name, config, optional_apps)
        jstorage.store(summary, values.name, version.psv.version)
        log.info('Product set %s has been provisioned for %s', version.psv.version, values.name)

    jstorage.store_index(version)


def provision_eic_rcd(product_set_version, is_release):
    '''
    Provision the EIC product set into RCD.
    '''
    eic_apps = []
    version = CVersion(Version.parse(product_set_version), is_release, False)

    if not username:
        raise rcd_exceptions.MandatoryEnvironmentVariableNotSetError(
            "GERRIT_USERNAME environment variable is not set.")
    if not password:
        raise rcd_exceptions.MandatoryEnvironmentVariableNotSetError(
            "GERRIT_PASSWORD environment variable is not set.")

    values_file_path, values_contents = get_site_values_info()
    releases_dict, csar_dict, templates = get_helm_file_info(
        product_set_version, values_file_path)

    for key, release in releases_dict.items():
        if 'url' in release:
            charts = []
            app_name = release['name']

            chart_url =  \
                f"{release['url'].rstrip('/')}/{app_name}/{app_name}-{release['version']}.tgz"

            csar_url =  \
                f"{EIC_CSAR_REPO}/{csar_dict[key]}/{release['version']}/{app_name}-{release['version']}.csar"

            app_optional = bool(app_name in EIC_OPTIONAL_APPS)
            eic_apps.append({
                "name": app_name,
                "description": app_name,
                "id": app_name,
                "app_enabled": app_optional,
                "csar": csar_url,
                "chart": chart_url,
                "optional": app_optional
                })

            chart = Chart(app_name, chart_url)
            charts.append(chart)
            log.info('Loading CSAR info')
            csar = get_csar_info(csar_url, username, password)
            csar.charts = charts
            csar.values_files.append(
                Values.parse('eric-eic-integration-fixed-size-production-values', values_contents))

            for values in csar.values_files:
                log.info('Handling \x1b[1m%s\x1b[0m',
                        config.get_variant(values.name)[1])

                if version.psv.version in jstorage.variants[values.name]:
                    log.info('  Output file already exists. Nothing to do.')
                    log.debug('  JStorage for current variant: %s',
                            jstorage.variants[values.name])
                    continue

                eic_summary = EICSummary()
                eic_summary.csar = csar
                chart_templates = get_chart_templates(app_name, templates)
                parse_charts(csar, values, eic_summary, bur_config, optional_apps,
                             eic_product=True, eic_app_templates=chart_templates)

                jstorage.store(eic_summary, values.name, version.psv.version, True, app_name)
                log.info('Application %s in Product set %s has been provisioned for %s',
                            app_name, version.psv.version, values.name)

    jstorage.store_apps(eic_apps, values.name, version.psv.version)
    clean_up_eic_tmp()
    change_to_app_dir()

    jstorage.add_version_in_variants(
        version.psv.version,
        'eric-eic-integration-fixed-size-production-values')

    jstorage.store_index(version, True)
    log.info('EIC Product set version %s has been provisioned', version.psv.version)
