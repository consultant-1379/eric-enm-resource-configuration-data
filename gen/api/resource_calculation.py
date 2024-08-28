'''
This file deals with calculating the total resources required based on deployment parameters.
'''
import logging
import math
import os
import rcd_exceptions

from model.overview import Overview
from model.summary import Summary, ResourceRequestsLimits
from model.config import Config
from utils.maximizer import Maximizer
from utils.utils import calculate_total, find, find_all
from utils.utils import read_json_file, calculate_total_for_ip_version
from utils.utils import remove_units_from_k8s_resource
from .eic_storage_requirements import set_storage_requirements
from generator import read_config_file
from output import output_excel

log = logging.getLogger('resource-calculation')

CONFIG_YAML_PATH = 'variant_config.yaml'
AFFINITY = 'affinity'
APP_ENABLED = 'app_enabled'
APPLICATIONS = 'applications'
BUR = 'bur'
CALC = 'calc'
CLIENT = 'client'
CONFIG_MAPS = 'config_maps'
CPU = 'cpu'
CPU_LIM = 'cpu_lim'
CPU_REQ = 'cpu_req'
CSAR = 'csar'
DATA_PATH = os.environ.get('RCD_DATA_PATH', '/data/')
DISK = 'disk'
DISK_STORAGE_SPACE = 'disk_storage_space'
EPS_LIM = 'eps_lim'
EPS_REQ = 'eps_req'
ERIC_INGRESSES = 'eric_ingresses'
EIC_APPS = "eic_apps"
ID = 'id'
IMAGES = 'images'
INGRESSES = 'ingresses'
JOB = 'Job'
KIND = 'kind'
LIMITS = 'limits'
MAX_UNAVAILABLE = 'maxUnavailable'
MEM_LIM = 'mem_lim'
MEM_REQ = 'mem_req'
NAME = 'name'
OPTIONAL_VALUE_PACKS = 'optional_value_packs'
OTHER_REQUIREMENTS = 'other_requirements'
OVERVIEW = 'overview'
PVCS = 'pvcs'
REGISTRY = 'registry'
REPLICAS = 'replicas'
REQUESTS = 'requests'
RWO = 'rwo'
RWX = 'rwx'
SECRETS = 'secrets'
SELECTED_VARIANT = 'selectedVariant'
SERVICES = 'services'
TOTAL_IMAGES_SIZE = 'total_images_size'
TYPE = 'type'
UPDATE_STRATEGY = 'update_strategy'
WL_MEM = 'wl_mem'
WL_CPU = 'wl_cpu'
WL_DISK = 'wl_disk'
WLDS_MEM = 'wlds_mem'
WLDS_DISK = 'wlds_disk'
WLDS_CPU = 'wlds_cpu'
WL_JOBS_MEM = 'wl_jobs_mem'
WL_JOBS_DISK = 'wl_jobs_disk'
WL_JOBS_CPU = 'wl_jobs_cpu'
WORKLOADS = 'workloads'
WORKER_CPU = 'worker_cpu'
WORKER_DISK = 'worker_disk'
WORKER_MEM = 'worker_mem'
WORKER_NODES = 'worker_nodes'
VALIDATION_ERRORS = 'validation_errors'
ISTIO_SIDE_CAR_CPU_REQ = 100
ISTIO_SIDE_CAR_CPU_LIM = 2000
ISTIO_SIDE_CAR_MEM_REQ = 128
ISTIO_SIDE_CAR_MEM_LIM = 1024
ISTIO_CPU_REQ = "istio_cpu_request"
ISTIO_CPU_LIM = "istio_cpu_limit"
ISTIO_MEM_REQ = "istio_mem_request"
ISTIO_MEM_LIM = "istio_mem_limit"
APPS = 'apps'
EIC_CLOUD_NATIVE_SERVICE_MESH_JSON='eric-cloud-native-service-mesh.json'

def prepare_data(variant, version, ip_version, enabled_optional_apps):
    '''
    This function prepares the data from the JSON product set file transforms
    it into a format ready for the front end.
    '''
    version = validate_version(version, variant)
    summary = Summary()
    data = read_json_file(DATA_PATH + variant + '/' + version + '.json')
    data[SELECTED_VARIANT] = variant
    data[VALIDATION_ERRORS] = prepare_validation_errors(data)
    enable_optional_applications(data, enabled_optional_apps)
    prepare_pvcs(data, summary)
    prepare_workloads(data, summary)
    data[CSAR] = prepare_images(data)
    prepare_other_requirements(data, summary)
    for resource in [CONFIG_MAPS, SECRETS, INGRESSES]:
        summary.overview.total[resource] = calculate_total(data[resource])
    for resource in [SERVICES, ERIC_INGRESSES]:
        summary.overview.total[resource] = calculate_total_for_ip_version(
            ip_version, data[resource], resource)

    calculate_workload_requirements(data, summary)
    data[OVERVIEW] = summary.overview
    return data


def prepare_excel_data(variant, version, ip_version, enabled_optional_apps):
    '''
    This function prepares the excel file.
    '''
    version = validate_version(version, variant)
    summary = Summary()
    data = read_json_file(DATA_PATH + variant + '/' + version + '.json')
    data[SELECTED_VARIANT] = variant
    data[VALIDATION_ERRORS] = prepare_validation_errors(data)
    enable_optional_applications(data, enabled_optional_apps)
    prepare_pvcs(data, summary)
    summary.pvcs = data[PVCS]
    prepare_workloads(data, summary)
    data[CSAR] = prepare_images(data)
    prepare_other_requirements(data, summary)
    for resource in [CONFIG_MAPS, SECRETS, INGRESSES]:
        summary.overview.total[resource] = calculate_total(data[resource])
    for resource in [SERVICES, ERIC_INGRESSES]:
        summary.overview.total[resource] = calculate_total_for_ip_version(
            ip_version, data[resource], resource)
    calculate_workload_requirements(data, summary)
    data[OVERVIEW] = summary.overview

    config = Config.parse(read_config_file(CONFIG_YAML_PATH))
    excel = output_excel.Storage(config)
    return excel.generate_workbook(summary, variant, version)


def prepare_eic_app_data(data, app_sum, ip_version, istio_resources):
    '''
    This function prepares the workload data for EIC application
    '''
    prepare_pvcs(data, app_sum)

    if len(data[WORKLOADS]) > 0:
        prepare_workloads(data, app_sum)

    for resource in [CONFIG_MAPS, SECRETS, INGRESSES]:
        app_sum.overview.total[resource] = calculate_total(data[resource])

    for resource in [SERVICES, ERIC_INGRESSES]:
        app_sum.overview.total[resource] = calculate_total_for_ip_version(
            ip_version, data[resource], resource)

    calculate_workload_requirements(data, app_sum, True)
    calculate_istio_sidecar_requirements(data, app_sum, istio_resources)
    apply_rounding(app_sum)


def agg_images_errors(data, agg_csar_images, agg_errors):
    '''
    This function aggregates the resources such as
    csar images and errors. Also
    returns the total image size
    '''
    app_csar = prepare_images(data)
    agg_csar_images.extend(app_csar[IMAGES])
    app_errors = prepare_validation_errors(data)
    agg_errors.extend(app_errors)
    return app_csar[TOTAL_IMAGES_SIZE]


def agg_pvcs_cms_secrets(data, agg_pvcs, agg_config_maps, agg_secrets):
    '''
    This function aggregates PVCs, Config Maps and Secrets
    from all EIC applications
    '''
    if PVCS in data:
        agg_pvcs.extend(data[PVCS])

    if CONFIG_MAPS in data:
        agg_config_maps.extend(data[CONFIG_MAPS])

    if SECRETS in data:
        agg_secrets.extend(data[SECRETS])


def agg_services_ingresses(data, agg_services, agg_ingresses, agg_eric_ingresses):
    '''
    This function aggregates Services, Config Maps and Secrets
    from all EIC applications
    '''
    if SERVICES in data:
        agg_services.extend(data[SERVICES])

    if INGRESSES in data:
        agg_ingresses.extend(data[INGRESSES])

    if ERIC_INGRESSES in data:
        agg_eric_ingresses.extend(data[ERIC_INGRESSES])


def cal_tot_sum_overview(tot_sum, app_sum):
    '''
    This function calculates the total resources summary
    by summing the total resources of the application
    '''
    tot_sum.overview.sum[RWX] += app_sum.overview.sum[RWX]
    tot_sum.overview.sum[RWO] += app_sum.overview.sum[RWO]
    tot_sum.overview.total[RWX] += app_sum.overview.total[RWX]
    tot_sum.overview.total[RWO] += app_sum.overview.total[RWO]

    for resource in [CONFIG_MAPS, SECRETS, INGRESSES, SERVICES, ERIC_INGRESSES]:
        if resource in tot_sum.overview.total:
            tot_sum.overview.total[resource] += app_sum.overview.total[resource]
        else:
            tot_sum.overview.total[resource] = app_sum.overview.total[resource]

    tot_sum.overview.limits[WL_MEM] += app_sum.overview.limits[WL_MEM]
    tot_sum.overview.limits[WL_CPU] += app_sum.overview.limits[WL_CPU]
    tot_sum.overview.limits[WL_DISK] += app_sum.overview.limits[WL_DISK]
    tot_sum.overview.limits[WLDS_CPU] += app_sum.overview.limits[WLDS_CPU]
    tot_sum.overview.limits[WLDS_MEM] += app_sum.overview.limits[WLDS_MEM]
    tot_sum.overview.limits[WLDS_DISK] += app_sum.overview.limits[WLDS_DISK]

    tot_sum.overview.limits[WL_JOBS_MEM] += \
        app_sum.overview.limits[WL_JOBS_MEM]

    tot_sum.overview.limits[WL_JOBS_CPU] += \
        app_sum.overview.limits[WL_JOBS_CPU]

    tot_sum.overview.limits[WL_JOBS_DISK] += \
        app_sum.overview.limits[WL_JOBS_DISK]

    tot_sum.overview.requests[WL_MEM] += app_sum.overview.requests[WL_MEM]
    tot_sum.overview.requests[WL_CPU] += app_sum.overview.requests[WL_CPU]
    tot_sum.overview.requests[WL_DISK] += app_sum.overview.requests[WL_DISK]
    tot_sum.overview.requests[WLDS_CPU] += app_sum.overview.requests[WLDS_CPU]
    tot_sum.overview.requests[WLDS_MEM] += app_sum.overview.requests[WLDS_MEM]
    tot_sum.overview.requests[WLDS_DISK] += app_sum.overview.requests[WLDS_DISK]

    tot_sum.overview.requests[WL_JOBS_MEM] += \
        app_sum.overview.requests[WL_JOBS_MEM]

    tot_sum.overview.requests[WL_JOBS_CPU] += \
        app_sum.overview.requests[WL_JOBS_CPU]

    tot_sum.overview.requests[WL_JOBS_DISK] += \
        app_sum.overview.requests[WL_JOBS_DISK]

    tot_sum.overview.total['pods'] += app_sum.overview.total['pods']


def set_reg_client_other_requirements(tot_sum, disk_storage_space):
    '''
    This function sets the registry, client and
    other requirements for EIC
    '''
    # EIC specific configurtion
    tot_sum.overview.registry[DISK_STORAGE_SPACE] = f"{disk_storage_space} GB"
    tot_sum.overview.client[CPU] = "2 vCPU"
    tot_sum.overview.client['memory'] = "4 GB"
    tot_sum.overview.client[DISK] = "90 GB"
    tot_sum.overview.other_requirements['ips'] = 2
    tot_sum.overview.other_requirements['ipv6s'] = 2
    tot_sum.overview.other_requirements['pids'] = 10240
    tot_sum.overview.client['docker'] = 'not_set'
    tot_sum.overview.client['ports'] = 'not_set'


def prepare_agg_data(variant, version, ip_version, enabled_optional_apps):
    '''
    This function prepares the data from the JSON product set file transforms
    it into a format ready for the front end.
    '''
    total_images_size = 0
    agg_data = {}
    agg_errors = []
    agg_work_loads = []
    agg_pvcs = []
    agg_config_maps = []
    agg_secrets = []
    agg_services = []
    agg_ingresses = []
    agg_eric_ingresses = []
    agg_csar_images = []

    tot_sum = Summary()
    max_cpu_req = Maximizer()
    max_cpu_lim = Maximizer()
    max_mem_req = Maximizer()
    max_mem_lim = Maximizer()
    max_eps_req = Maximizer()
    max_eps_lim = Maximizer()
    min_worker_nodes = Maximizer()

    variant_path = os.path.join(DATA_PATH, variant)
    json_dir = os.path.join(variant_path, version)
    istio_resources = get_istio_resource_request_limits(json_dir)

    if os.path.exists(json_dir):
        app_sum_list = []
        app_id = 0
        for filename in os.listdir(json_dir):
            if filename.endswith('.json') and not filename.endswith('apps.json'):
                app_name = filename.replace(".json", "")
                if app_name in enabled_optional_apps:
                    file_full_path = os.path.join(json_dir, filename)
                    data = read_json_file(file_full_path)
                    data[SELECTED_VARIANT] = variant
                    app_sum = Summary()
                    prepare_eic_app_data(data, app_sum, ip_version, istio_resources)
                    agg_work_loads.extend(app_sum.workloads)
                    enable_optional_applications(data, enabled_optional_apps)
                    total_images_size += agg_images_errors(data, agg_csar_images, agg_errors)
                    agg_pvcs_cms_secrets(data, agg_pvcs, agg_config_maps, agg_secrets)
                    agg_services_ingresses(data, agg_services, agg_ingresses, agg_eric_ingresses)
                    cal_tot_sum_overview(tot_sum, app_sum)

                    app_cpu_req = app_sum.overview.requests[WL_CPU]
                    app_cpu_lim = app_sum.overview.limits[WL_CPU]
                    app_mem_req = app_sum.overview.requests[WL_MEM]
                    app_mem_lim = app_sum.overview.limits[WL_MEM]
                    app_eps_req = app_sum.overview.requests[WL_DISK]
                    app_eps_lim = app_sum.overview.limits[WL_DISK]

                    max_cpu_req.update(app_sum.overview.max[CPU_REQ])
                    max_cpu_lim.update(app_sum.overview.max[CPU_LIM])
                    max_mem_req.update(app_sum.overview.max[MEM_REQ])
                    max_mem_lim.update(app_sum.overview.max[MEM_LIM])
                    max_eps_req.update(app_sum.overview.max[EPS_REQ])
                    max_eps_lim.update(app_sum.overview.max[EPS_LIM])
                    min_worker_nodes.update(app_sum.overview.min[WORKER_NODES])

                    app_sum_for_print = {
                        "name": app_name,
                        "id": app_id,
                        "cpu_req": app_cpu_req ,
                        "cpu_lim": app_cpu_lim,
                        "mem_req": app_mem_req,
                        "mem_lim": app_mem_lim,
                        'eps_req': app_eps_req,
                        'eps_lim': app_eps_lim,
                        "max_cpu_requests": app_sum.overview.max[CPU_REQ],
                        "max_cpu_limits": app_sum.overview.max[CPU_LIM],
                        "max_mem_requests": app_sum.overview.max[MEM_REQ],
                        "max_mem_limits": app_sum.overview.max[MEM_LIM],
                        "max_eps_requests": app_sum.overview.max[EPS_REQ],
                        "max_eps_limits": app_sum.overview.max[EPS_LIM],
                        "min_worker_nodes": app_sum.overview.min[WORKER_NODES],
                        "app_enabled": True,
                        "ds_cpu_limits": app_sum.overview.limits[WLDS_CPU],
                        "ds_mem_limits": app_sum.overview.limits[WLDS_MEM],
                        "ds_disk_limits": app_sum.overview.limits[WLDS_DISK]
                    }

                    if app_cpu_req != 0 and \
                        app_cpu_lim != 0 and \
                        app_mem_req != 0 and \
                        app_mem_lim != 0:

                        app_id += 1
                        app_sum_list.append(app_sum_for_print)

        tot_sum.overview.max[CPU_REQ] = max_cpu_req.get()
        tot_sum.overview.max[CPU_LIM] = max_cpu_lim.get()
        tot_sum.overview.max[MEM_REQ] = max_mem_req.get()
        tot_sum.overview.max[MEM_LIM] = max_mem_lim.get()
        tot_sum.overview.max[EPS_REQ] = max_eps_req.get()
        tot_sum.overview.max[EPS_LIM] = max_eps_lim.get()

        tot_sum.overview.min[WORKER_CPU] = math.ceil(
            (max_cpu_lim.get() + tot_sum.overview.limits[WLDS_CPU]) / 1000)

        tot_sum.overview.min[WORKER_MEM] = math.ceil(
            (max_mem_lim.get() + tot_sum.overview.limits[WLDS_MEM]) / 1024)

        tot_sum.overview.min[WORKER_DISK] = math.ceil(
            max_eps_lim.get() + tot_sum.overview.limits[WLDS_DISK])

        tot_sum.overview.min[WORKER_NODES] = min_worker_nodes.get() + 1
        disk_storage_space = int(total_images_size / 1024**3)
        set_reg_client_other_requirements(tot_sum, disk_storage_space)
        set_storage_requirements(tot_sum, agg_pvcs)
        agg_data[SELECTED_VARIANT] = variant
        agg_data[VALIDATION_ERRORS] = agg_errors
        agg_data[PVCS] = agg_pvcs
        agg_data[OVERVIEW] = tot_sum.overview
        agg_data[WORKLOADS] = agg_work_loads
        agg_data[CONFIG_MAPS] = agg_config_maps
        agg_data[SECRETS] = agg_secrets
        agg_data[SERVICES] = agg_services
        agg_data[INGRESSES] = agg_ingresses
        agg_data[ERIC_INGRESSES] = agg_eric_ingresses
        agg_data[APPS] = app_sum_list
        agg_data[CSAR] = {
            IMAGES: agg_csar_images,
            TOTAL_IMAGES_SIZE: total_images_size
        }

    else:
        raise rcd_exceptions.MandatoryEnvironmentVariableNotSetError(
            "JSON not available for the selected version")

    return agg_data


def get_istio_resource_request_limits(json_dir):
    '''
    This function gets the istio resource reques and limis requirements
    '''
    istio_resources = ResourceRequestsLimits()
    file_path = os.path.join(json_dir, EIC_CLOUD_NATIVE_SERVICE_MESH_JSON)

    if os.path.exists(file_path):
        data = read_json_file(file_path)
        if ISTIO_CPU_LIM in data:
            istio_resources.cpu_lim = int(remove_units_from_k8s_resource(data[ISTIO_CPU_LIM]))
        if ISTIO_CPU_REQ in data:
            istio_resources.cpu_req = int(remove_units_from_k8s_resource(data[ISTIO_CPU_REQ]))
        if ISTIO_MEM_LIM in data:
            istio_resources.mem_lim = int(remove_units_from_k8s_resource(data[ISTIO_MEM_LIM]))
        if ISTIO_MEM_REQ in data:
            istio_resources.mem_req = int(remove_units_from_k8s_resource(data[ISTIO_MEM_REQ]))

    return istio_resources


def calculate_istio_sidecar_requirements(data, summary, istio_resources):
    '''
    This function calculates the istio sidecar requirements
    '''
    if istio_resources.cpu_req > 0:
        istio_cpu_req = istio_resources.cpu_req
    else:
        istio_cpu_req = ISTIO_SIDE_CAR_CPU_REQ

    if istio_resources.cpu_lim > 0:
        istio_cpu_lim = istio_resources.cpu_lim
    else:
        istio_cpu_lim = ISTIO_SIDE_CAR_CPU_LIM

    if istio_resources.mem_req > 0:
        istio_mem_req = istio_resources.mem_req
    else:
        istio_mem_req = ISTIO_SIDE_CAR_MEM_REQ

    if istio_resources.mem_lim > 0:
        istio_mem_lim = istio_resources.mem_lim
    else:
        istio_mem_lim = ISTIO_SIDE_CAR_MEM_LIM

    if 'istio_side_cars' in data:
        for side_car in data['istio_side_cars']:
            replicas = int(side_car['replicas'])

            if 'cpu_request' in side_car:
                summary.overview.requests[WL_CPU] += int(side_car['cpu_request']) * replicas
            else:
                summary.overview.requests[WL_CPU] += istio_cpu_req * replicas

            if 'cpu_limit' in side_car:
                summary.overview.limits[WL_CPU] += int(side_car['cpu_limit']) * replicas
            else:
                summary.overview.limits[WL_CPU] += istio_cpu_lim * replicas

            if 'mem_request' in side_car:
                summary.overview.requests[WL_MEM] += int(side_car['mem_request']) * replicas
            else:
                summary.overview.requests[WL_MEM] += istio_mem_req * replicas

            if 'mem_limit' in side_car:
                summary.overview.limits[WL_MEM] += int(side_car['mem_limit']) * replicas
            else:
                summary.overview.limits[WL_MEM] += istio_mem_lim * replicas


def apply_rounding(summary):
    '''
    This function applies rounding for CPU and Memory resources.
    '''
    summary.overview.requests[WL_CPU] = math.ceil(summary.overview.requests[WL_CPU] / 1000) * 1000
    summary.overview.limits[WL_CPU] = math.ceil(summary.overview.limits[WL_CPU] / 1000) * 1000
    summary.overview.requests[WL_MEM] = math.ceil(summary.overview.requests[WL_MEM] / 1024) * 1024
    summary.overview.limits[WL_MEM] = math.ceil(summary.overview.limits[WL_MEM] / 1024) * 1024

# pylint: disable=too-many-locals,too-many-statements
def calculate_workload_requirements(data, summary, eic_product = False):
    '''
    This function calculates all the overall requirements.
    '''
    req_wl_cpu = 0
    req_wl_mem = 0
    req_wl_disk = 0
    lim_wl_cpu = 0
    lim_wl_mem = 0
    lim_wl_disk = 0
    # Daemon set workloads
    req_wlds_cpu = 0
    lim_wlds_cpu = 0
    req_wlds_mem = 0
    lim_wlds_mem = 0
    req_wlds_disk = 0
    lim_wlds_disk = 0

    req_wl_jobs_cpu = 0
    lim_wl_jobs_cpu = 0
    req_wl_jobs_mem = 0
    lim_wl_jobs_mem = 0
    req_wl_jobs_disk = 0
    lim_wl_jobs_disk = 0

    max_cpu_req = Maximizer()
    max_cpu_lim = Maximizer()
    max_mem_req = Maximizer()
    max_mem_lim = Maximizer()
    max_eps_req = Maximizer()
    max_eps_lim = Maximizer()

    max_replica_count = 0
    total_pods = 0

    for workload in data[WORKLOADS]:
        if workload[APP_ENABLED]:
            replicas = workload[REPLICAS]
            if replicas is None:
                replicas = 1
            if workload[AFFINITY] is not None and workload[AFFINITY].startswith('hard'):
                if replicas > max_replica_count:
                    max_replica_count = replicas
            if replicas == -1:
                req_wlds_cpu += workload[CPU_REQ]
                lim_wlds_cpu += workload[CPU_LIM]
                req_wlds_mem += workload[MEM_REQ]
                lim_wlds_mem += workload[MEM_LIM]
                req_wlds_disk += workload[EPS_REQ]
                lim_wlds_disk += workload[EPS_LIM]
            else:
                if (eic_product and workload[KIND] != JOB) or (not eic_product):
                    total_pods += replicas
                if workload[KIND] == JOB:
                    req_wl_jobs_cpu += workload[CPU_REQ] * replicas
                    lim_wl_jobs_cpu += workload[CPU_LIM] * replicas
                    req_wl_jobs_mem += workload[MEM_REQ] * replicas
                    lim_wl_jobs_mem += workload[MEM_LIM] * replicas
                    req_wl_jobs_disk += workload[EPS_REQ] * replicas
                    lim_wl_jobs_disk += workload[EPS_LIM] * replicas
                    continue
                req_wl_cpu += workload[CPU_REQ] * replicas
                lim_wl_cpu += workload[CPU_LIM] * replicas
                req_wl_mem += workload[MEM_REQ] * replicas
                lim_wl_mem += workload[MEM_LIM] * replicas
                req_wl_disk += workload[EPS_REQ] * replicas
                lim_wl_disk += workload[EPS_LIM] * replicas

                max_cpu_req.update(workload[CPU_REQ])
                max_cpu_lim.update(workload[CPU_LIM])
                max_mem_req.update(workload[MEM_REQ])
                max_mem_lim.update(workload[MEM_LIM])
                max_eps_req.update(workload[EPS_REQ])
                max_eps_lim.update(workload[EPS_LIM])

    summary.overview.max[CPU_REQ] = max_cpu_req.get()
    summary.overview.max[CPU_LIM] = max_cpu_lim.get()
    summary.overview.max[MEM_REQ] = max_mem_req.get()
    summary.overview.max[MEM_LIM] = max_mem_lim.get()
    summary.overview.max[EPS_REQ] = max_eps_req.get()
    summary.overview.max[EPS_LIM] = max_eps_lim.get()

    summary.overview.min[WORKER_CPU] = math.ceil((max_cpu_lim.get() + lim_wlds_cpu) / 1000)
    summary.overview.min[WORKER_MEM] = math.ceil((max_mem_lim.get() + lim_wlds_mem) / 1024)
    summary.overview.min[WORKER_DISK] = math.ceil(max_eps_lim.get() + lim_wlds_disk)
    if data[SELECTED_VARIANT] == 'eric-enm-integration-production-values':
        summary.overview.min[WORKER_NODES] = 4
    else:
        summary.overview.min[WORKER_NODES] = max_replica_count

    summary.overview.limits[WL_MEM] = lim_wl_mem
    summary.overview.limits[WL_CPU] = lim_wl_cpu
    summary.overview.limits[WL_DISK] = lim_wl_disk
    summary.overview.limits[WLDS_CPU] = lim_wlds_cpu
    summary.overview.limits[WLDS_MEM] = lim_wlds_mem
    summary.overview.limits[WLDS_DISK] = lim_wlds_disk
    summary.overview.limits[WL_JOBS_MEM] = lim_wl_jobs_mem
    summary.overview.limits[WL_JOBS_CPU] = lim_wl_jobs_cpu
    summary.overview.limits[WL_JOBS_DISK] = lim_wl_jobs_disk

    summary.overview.requests[WL_MEM] = req_wl_mem
    summary.overview.requests[WL_CPU] = req_wl_cpu
    summary.overview.requests[WL_DISK] = req_wl_disk
    summary.overview.requests[WLDS_CPU] = req_wlds_cpu
    summary.overview.requests[WLDS_MEM] = req_wlds_mem
    summary.overview.requests[WLDS_DISK] = req_wlds_disk
    summary.overview.requests[WL_JOBS_MEM] = req_wl_jobs_mem
    summary.overview.requests[WL_JOBS_CPU] = req_wl_jobs_cpu
    summary.overview.requests[WL_JOBS_DISK] = req_wl_jobs_disk

    summary.overview.total['pods'] = total_pods

    data[CALC] = {}
    data[CALC][CPU] = math.ceil((max_cpu_lim.get() + lim_wlds_cpu)/1000)
    data[CALC]['mem'] = math.ceil((max_mem_lim.get() + lim_wlds_mem)/1024)
    data[CALC][DISK] = math.ceil(max_eps_lim.get() + lim_wlds_disk)
    data[CALC]['node_count'] = 1


def prepare_data_comparison(variant, from_version, to_version, ip_version, optional_apps,
                            to_optional_apps):
    '''
    This function prepares the data from the JSON product set file transforms
    it into a format ready for the front end for the PS comparison.
    '''
    data = prepare_data(variant, from_version, ip_version, optional_apps)[OVERVIEW]
    data_to_state = prepare_data(variant, to_version, ip_version, to_optional_apps)[OVERVIEW]
    overview = Overview()

    setattr(overview, BUR, set_comparison_values_number(data, data_to_state, BUR))
    setattr(overview, 'max', set_comparison_values_number(data, data_to_state, 'max'))
    setattr(overview, 'min', set_comparison_values_number(data, data_to_state, 'min'))
    setattr(overview, 'sum', set_comparison_values_number(data, data_to_state, 'sum'))
    setattr(overview, 'total', set_comparison_values_number(data, data_to_state, 'total'))

    setattr(overview, CLIENT, set_comparison_values_string(data, data_to_state, CLIENT))
    setattr(overview, OTHER_REQUIREMENTS, set_comparison_values_number(data, data_to_state,
                                                                         OTHER_REQUIREMENTS))
    setattr(overview, REGISTRY, set_comparison_values_string(data, data_to_state, REGISTRY))

    setattr(overview, LIMITS, set_comparison_requests_limits(data, data_to_state, LIMITS))
    setattr(overview, REQUESTS, set_comparison_requests_limits(data, data_to_state, REQUESTS))
    return overview


def set_comparison_requests_limits(data, data_to_state, attribute):
    '''
    This function sets the values for the workload requests and limts for data comparison.
    This function also rounds up and converts to the nearest core/GiB.
    '''
    result = {}
    for req, to_state_val in getattr(data_to_state, attribute).items():
        from_state_val = getattr(data, attribute)[req]
        if '_cpu' in req:
            result[req] = math.ceil((to_state_val - from_state_val) / 1000)
        elif '_disk' in req:
            result[req] = math.ceil(to_state_val - from_state_val)
        elif '_mem' in req:
            result[req] = math.ceil((to_state_val - from_state_val) / 1024)
    return result


def set_comparison_values_number(data, data_to_state, attribute):
    '''
    This function sets the values for the comparison data.
    This function support only requests that are numbers types in the data.
    '''
    result = {}
    for req, to_state_val in getattr(data_to_state, attribute).items():
        result[req] = 0
        if req in getattr(data, attribute):
            from_state_val = getattr(data, attribute)[req]
            if to_state_val != from_state_val:
                result[req] = math.ceil(to_state_val - from_state_val)
    return result


def set_comparison_values_string(data, data_to_state, attribute):
    '''
    This function sets the values for the comparison data.
    This function support only requests that are type string in the data.
    '''
    result = {}
    for req, to_state_val in getattr(data_to_state, attribute).items():
        result[req] = ''
        if req in getattr(data, attribute):
            from_state_values = getattr(data, attribute)
            if req in from_state_values and from_state_values[req] != to_state_val:
                result[req] = to_state_val
    return result


def get_resource_overview(deployment_type, version, ip_version, optional_apps):
    '''
    This function returns a subset of the total data in the JSON model.
    All units should be in GiB/cores
    '''
    cpu_daemon_set = 'cpu_daemon_set'
    cpu_jobs = 'cpu_jobs'
    external_networks = 'external_networks'
    load_balancers = 'load_balancers'
    memory = 'memory'
    vips_ipv4 = 'vips_ipv4'
    vips_ipv6 = 'vips_ipv6'
    version = validate_version(version, deployment_type)
    data = prepare_data(deployment_type, version, ip_version, optional_apps)
    overview = data[OVERVIEW]
    result = {}
    result['deployment_type'] = deployment_type
    result['application_version'] = version
    result[CPU] = {
        REQUESTS: round(overview.requests[WL_CPU]/1000, 2),
        LIMITS: round(overview.limits[WL_CPU]/1000, 2)
    }
    result[cpu_daemon_set] = {
        REQUESTS: round(overview.requests[WLDS_CPU]/1000, 2),
        LIMITS: round(overview.limits[WLDS_CPU]/1000, 2)
    }
    result[cpu_jobs] = {
        REQUESTS: round(overview.requests[WL_JOBS_CPU]/1000, 2),
        LIMITS: round(overview.limits[WL_JOBS_CPU]/1000, 2)
    }
    result[memory] = {
        REQUESTS: round(overview.requests[WL_MEM]/1024, 2),
        LIMITS: round(overview.limits[WL_MEM]/1024, 2)
    }
    result['memory_daemon_set'] = {
        REQUESTS: round(overview.requests[WLDS_MEM]/1024, 2),
        LIMITS: round(overview.limits[WLDS_MEM]/1024, 2)
    }
    result['memory_jobs'] = {
        REQUESTS: round(overview.requests[WL_JOBS_MEM]/1024, 2),
        LIMITS: round(overview.limits[WL_JOBS_MEM]/1024, 2)
    }
    result['ephemeral'] = {
        REQUESTS: math.ceil(overview.requests[WL_DISK]),
        LIMITS: math.ceil(overview.limits[WL_DISK])
    }
    result['ephemeral_daemon_set'] = {
        REQUESTS: math.ceil(overview.requests[WLDS_DISK]),
        LIMITS: math.ceil(overview.limits[WLDS_DISK])
    }
    result['ephemeral_jobs'] = {
        REQUESTS: math.ceil(overview.requests[WL_JOBS_DISK]),
        LIMITS: math.ceil(overview.limits[WL_JOBS_DISK])
    }
    result['total_storage_rwo'] = math.ceil(overview.sum[RWO])
    result['total_storage_rwx'] = math.ceil(overview.sum[RWX])
    result['client_minimum_storage'] = int(overview.client[DISK].split()[0])
    result['minimum'] = {
        WORKER_NODES: overview.min[WORKER_NODES],
        WORKER_CPU: round(overview.max[CPU_LIM]/1000, 2),
        'worker_memory': round(overview.max[MEM_LIM]/1024, 2),
        'worker_ephemeral_storage': round(overview.max[EPS_LIM], 2)
    }
    result[external_networks] = {
        TYPE: ip_version,
        vips_ipv4: overview.other_requirements.get('ips', 0) - overview.other_requirements.get(
            load_balancers, 0),
        vips_ipv6: overview.other_requirements.get('ipv6s', 0) - overview.other_requirements.get(
            load_balancers, 0),
        load_balancers: overview.other_requirements.get(load_balancers, 0)
    }
    if ip_version == 'ipv4':
        result[external_networks].pop(vips_ipv6)
    elif ip_version == 'ipv6':
        result[external_networks].pop(vips_ipv4)
    result['total_application_images_size'] = round(data[CSAR][TOTAL_IMAGES_SIZE]/(2**30), 2)
    result['total_registry_size'] = round(int(overview.registry[DISK_STORAGE_SPACE].split()[0]), 2)
    result['available_optional_apps'] = [app[NAME]for app in data[OPTIONAL_VALUE_PACKS]]
    result['enabled_optional_apps'] = optional_apps
    return result


def prepare_other_requirements(data, summary):
    '''
    This function prepares the other requirements data.
    '''
    for field in [REGISTRY, 'cluster', CLIENT, BUR]:
        update_overview_attribute(data, summary, field)
    # Remove any keys that have value 0
    if OTHER_REQUIREMENTS in data[OVERVIEW]:
        summary.overview.other_requirements = {
            k: v for k, v in data[OVERVIEW][OTHER_REQUIREMENTS].items() if v != 0}


def update_overview_attribute(data, summary, field):
    '''
    Update an attribute of the Summary overview object.
    '''
    if field in data[OVERVIEW]:
        setattr(summary.overview, field, data[OVERVIEW][field])


def prepare_images(data):
    '''
    This function prepares the image data.
    '''
    images = 'images'
    csar_info = {images: []}
    csar_info[TOTAL_IMAGES_SIZE] = data[CSAR][TOTAL_IMAGES_SIZE]
    for index, image in enumerate(data[CSAR].pop(images)):
        image[ID] = index
        csar_info[images].append(image)
    return csar_info


def prepare_workloads(data, summary):
    '''
    This function prepares the workload data.
    '''
    for index, workload in enumerate(data.pop(WORKLOADS)):
        workload[ID] = index
        workload['expanded'] = False
        workload['hover'] = False
        data.setdefault(WORKLOADS, []).append(workload)
    summary.workloads = data[WORKLOADS]


def prepare_pvcs(data, summary):
    '''
    This function prepares the PVC data.
    '''
    instances = 'instances'
    pvcs = 'pvcs'
    size = 'size'
    sum_s_rwo = 0
    sum_s_rwx = 0
    total_rwo = 0
    total_rwx = 0
    for index, pvc in enumerate(data.pop(pvcs)):
        pvc[ID] = index
        data.setdefault(pvcs, []).append(pvc)
        if pvc[APP_ENABLED]:
            if pvc[TYPE] == RWO.upper():
                total_rwo += pvc[instances]
                sum_s_rwo += pvc[size] * pvc[instances]
            if pvc[TYPE] == RWX.upper():
                total_rwx += 1
                sum_s_rwx += pvc[size]
    summary.overview.sum[RWX] = sum_s_rwx
    summary.overview.sum[RWO] = sum_s_rwo
    summary.overview.total[RWX] = total_rwx
    summary.overview.total[RWO] = total_rwo


def prepare_validation_errors(data):
    '''
    This function prepares the validation error data.
    '''
    error_list = []
    error_index = 0
    if VALIDATION_ERRORS in data:
        for chart_name in data[VALIDATION_ERRORS]:
            for sg_name in data[VALIDATION_ERRORS][chart_name]:
                error_index += 1
                error_list.append({ID: error_index,
                                NAME: sg_name,
                                'chart': chart_name,
                                'error': '<br>'.join(data[VALIDATION_ERRORS][chart_name][sg_name]),
                                APP_ENABLED: True
                                })
    return error_list


def enable_optional_applications(data, enabled_optional_apps):
    '''
    This function enables optional applications.
    '''
    for enabled_app_name in enabled_optional_apps:
        for optional_vp in data[OPTIONAL_VALUE_PACKS]:
            if optional_vp[NAME] == enabled_app_name:
                enable_optional_resources(data, optional_vp, enabled_optional_apps)


def enable_optional_resources(data, optional_vp, enabled_optional_apps):
    '''
    This function enables the resources for any enabled optional applications.
    '''
    jobs = 'jobs'
    for resource in [CONFIG_MAPS, SECRETS, SERVICES, INGRESSES, ERIC_INGRESSES, WORKLOADS]:
        for optional_app in optional_vp[APPLICATIONS]:
            app_name = optional_app[NAME]
            apps_to_enable = find_all(data[resource], NAME, app_name)
            if jobs in optional_vp:
                for job_name in optional_vp[jobs]:
                    job_index = find(data[resource], NAME, job_name)
                    if job_index >= 0:
                        apps_to_enable.append(job_index)
            if resource == CONFIG_MAPS:
                cm_index = find(data[resource], NAME, 'gp' + app_name)
                if cm_index >= 0:
                    apps_to_enable.append(cm_index)
            if len(apps_to_enable) > 0:
                for app_idx in apps_to_enable:
                    workload = data[resource][app_idx]
                    workload[APP_ENABLED] = True
                    if resource == WORKLOADS and workload[KIND] != JOB:
                        check_connected_vp(
                            optional_vp, optional_app, app_name, workload, enabled_optional_apps)


def check_connected_vp(optional_vp, optional_app, app_name, workload, enabled_optional_apps):
    '''
    This function updates some parameters for optional resources if an optional application has
    another linked optional application enabled.
    '''
    connected_vp = 'connected_vp'
    if connected_vp in optional_vp:
        connected_vp_val = optional_vp[connected_vp][0][APPLICATIONS]
        vp_idx = find(connected_vp_val, NAME, app_name)
        if vp_idx >= 0 and optional_vp[connected_vp][0][NAME] in enabled_optional_apps:
            workload[REPLICAS] = optional_app[REPLICAS] + connected_vp_val[vp_idx][REPLICAS]
            if UPDATE_STRATEGY in optional_app:
                max_unavailable = optional_app[UPDATE_STRATEGY][MAX_UNAVAILABLE] + \
                    connected_vp_val[vp_idx][UPDATE_STRATEGY][MAX_UNAVAILABLE]
                set_workload_parameters(optional_app, workload, max_unavailable)
        else:
            if REPLICAS in optional_app:
                workload[REPLICAS] = optional_app[REPLICAS]
                if UPDATE_STRATEGY in optional_app:
                    max_unavailable = optional_app[UPDATE_STRATEGY][MAX_UNAVAILABLE]
                    set_workload_parameters(optional_app, workload, max_unavailable)


def set_workload_parameters(optional_app, workload, max_unavailable):
    '''
    This function updates the PDB and Update Strategy fields of a workload.
    '''
    if workload[KIND] != JOB and UPDATE_STRATEGY in optional_app:
        workload[UPDATE_STRATEGY]['rollingUpdate'][MAX_UNAVAILABLE] = max_unavailable
        workload['pdb']['value'] = max_unavailable


def validate_version(drop_or_version, variant):
    '''
    This function validates the version specified in the request.
    If a drop version is specified it will find the latest available.
    '''
    data = read_json_file(DATA_PATH + 'index.json')
    for var in data:
        if var['datapath'] == variant:
            versions = [d['file'] for d in var['versions']]
            break
    if drop_or_version in versions:
        log.info('Received version: %s is available.', drop_or_version)
        return drop_or_version
    if len(drop_or_version.split('.')) == 2:
        for ver in versions:
            if ver.startswith(drop_or_version):
                log.info('Version requested was %s Version %s is the latest available',
                         drop_or_version,
                         ver)
                return ver
    log.error('Specified version %s not found in available versions.', drop_or_version)
    raise InvalidVersionException


class InvalidVersionException(Exception):
    """
    Simple Invalid version exception.
    """
    pass
