'''
This file computes the resouce requirements for a product set.
'''
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import logging
from utils.objfinder import objfinder
from utils.utils import check_path_in_dict
from .eic_custom_resources import get_containers_for_cassandra, get_pvcs_for_cassandra, generate_pvc_manifest

log = logging.getLogger('resource_requirements')
NA_STRING = 'N/A'
MEM_REQUIREMENTS_MAP = {'K': 1, 'M': 2, 'G': 3, 'T': 4, 'P': 5, 'E': 6}
PVC_ACCESSMODE_MAP = {
    'ReadWriteOnce': 'RWO',
    'ReadWriteMany': 'RWX',
    'ReadOnlyMany': 'ROX'
}

DAEMON_SET = 'DaemonSet'
DEPLOYMENT = 'Deployment'
STATEFUL_SET = 'StatefulSet'
REDIS_CLUSTER = 'RedisCluster'
EIC_CRD_KAFKA = 'Kafka'
EIC_CRD_CASSANDRA = 'CassandraCluster'
MAX_UN_AVAILABLE = 'maxUnavailable'
KIND = 'kind'
TYPE = 'type'
ROLLING_UPDATE_TYPE = 'RollingUpdate'
ROLLING_UPDATE = 'rollingUpdate'
RECREATE = 'Recreate'
UPDATE_STRATEGY_ROLLING_UPDATE_MAX_UNAVAILABLE_ERROR='Update strategy rollingUpdate '+\
                                                         'maxUnavailable should be set to 1.'
NO_AFFINITY_VALUE_SET = 'No affinity value set.'


def parse_cpu(storage):
    '''
    parse the cpu storage value and returns in mega.
    '''
    if storage is None:
        return 0
    mega = 1000
    if isinstance(storage, str):
        if storage[-1] == 'm':
            mega = 1
            storage = storage[:-1]
        storage = float(storage)
    return storage * mega


def parse_mem(storage, base):
    '''
    Parses the memory storage requirements.
    '''
    if storage is None or len(storage) == 0:
        return 0
    mem = 1
    if storage[-1] == 'i':
        mem = 2 ** (MEM_REQUIREMENTS_MAP[storage[-2]] * 10)
        val = float(storage[:-2])
    else:
        mem = 10 ** (MEM_REQUIREMENTS_MAP[storage[-1]] * 3)
        val = float(storage[:-1])
    return val * mem / 2 ** base


stsFinder = objfinder('spec.template.spec')
stsPodFinder = objfinder('spec.podTemplate.spec')
hardAffFinder = objfinder('affinity.podAntiAffinity.'+
                            'requiredDuringSchedulingIgnoredDuringExecution.*')
softAffFinder = objfinder('affinity.podAntiAffinity.'+
                            'preferredDuringSchedulingIgnoredDuringExecution.*')


def validate_pdb(workload, workload_pdb, errors):
    '''
    Validates the pdb for a workload and add errors if found.
    '''
    pdb_type = workload_pdb.pdbtype
    if pdb_type == MAX_UN_AVAILABLE:
        if workload.replicas > 1 and workload_pdb.value != 1:
            errors.setdefault(workload.name, []).append(f'Incorrect maxUnavailable value'
                                                  f' \'{workload_pdb.value}\' for Pod Disruption'
                                                  ' Budget it must be set to 1.')
    elif pdb_type == 'minAvailable' and workload.replicas > 1:
        errors.setdefault(workload.name, []).append(f'Incorrect Pod Disruption Budget type'
                                              f' \'{pdb_type}\' it must be set to maxUnavailable.')
    elif workload.replicas > 1:
        errors.setdefault(workload.name, []).append('Pod Disruption Budget not specified.')


def check_wl_enabled(app_name, optional_apps, wl_type=None) -> bool:
    '''
    Check whether a workload is enabled or not.
    '''
    optional_apps_list = []
    optional_jobs_list = []

    if app_name.startswith('gp'):
        app_name = app_name[2:]

    for release in optional_apps:
        for value_pack in release['value_packs']:
            for apps in value_pack['applications']:
                optional_apps_list.append(apps['name'])
            if 'jobs' in value_pack:
                optional_jobs_list.extend(value_pack['jobs'])
    app_enabled = not app_name.startswith(tuple(optional_apps_list))
    if wl_type == 'Job' and app_enabled:
        app_enabled = app_name not in optional_jobs_list
    return app_enabled


def parse_pod_anti_affinity(manifest, name, values_file_name, replicas, errors):
    '''
    Parses pod anti-affinity and logs any errors if present.
    '''
    # https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/pod-v1/#PodAntiAffinity
    max_hard_replicas_small = 3
    max_hard_replicas_xl = 8
    spec = stsFinder(manifest)
    if not spec:
        spec = stsPodFinder(manifest)
    if not spec:
        if KIND in manifest and manifest[KIND] in ['CronJob', 'Job']:
            return NA_STRING
        errors.setdefault(name, []).append('Affinity rule without spec.')
        return None

    rules = []

    for pat in hardAffFinder(spec):
        label_selector = Selector.from_manifest(pat.get('labelSelector', {}))
        rules.append(f"hard pod anti affinity: {label_selector.ser()}")

    for wpat in softAffFinder(spec):
        weight = wpat.get('weight')
        pat = wpat.get('podAffinityTerm')
        label_selector = Selector.from_manifest(pat.get('labelSelector'))
        rules.append(f"soft pod anti affinity: {label_selector.ser()} with weight {weight}")

    if len(rules) > 1:
        errors.setdefault(name, []).append('More than one affinity rule specified. '
                                           'Currently only one affinity scheduling rule'
                                           ' per workload is supported.')
        return None
    if rules:
        affinity = rules[0]
        if "soft" in affinity and replicas > 1:
            if values_file_name == 'eric-enm-integration-production-values' and \
                                                         replicas <= max_hard_replicas_small:
                errors.setdefault(name, []).append(f'Soft anti-affinity cannot be set for small'
                                                   f' deployment if replicas is <='
                                                   f' {max_hard_replicas_small}.')
            elif values_file_name == 'eric-enm-integration-extra-large-production-values' and \
                    replicas <= max_hard_replicas_xl:
                errors.setdefault(name, []).append(f'Soft anti-affinity cannot be set for XL '
                                                   f'deployment if replicas is '
                                                   f'<= {max_hard_replicas_xl}.')
        return affinity
    if replicas > 1:
        errors.setdefault(name, []).append('No affinity value set.')
        return None
    return NA_STRING


def is_update_strategy_set_to_rolling_update(name, update_strategy, errors, replicas):
    '''
    Check whether upgrade strategy set to rolling update or not and log error.
    '''
    update_strategy_rolling_update= 'Update strategy type not set to rolling update.'
    if TYPE in update_strategy:
        if update_strategy[TYPE] != ROLLING_UPDATE_TYPE:
            if not(update_strategy[TYPE] == RECREATE and replicas <= 1):
                errors.setdefault(name, []).append(update_strategy_rolling_update)


def is_max_unavail_max_surge_set_to_rolling_update(name, kind, update_strategy, errors, replicas):
    '''
    Checks whether max unavailable and max surge set to rolling update or not.
    '''
    max_surge = 'maxSurge'
    update_strategy_max_unavailable='Update strategy rollingUpdate maxUnavailable should be set.'
    udpate_rolling_maxsurge_to_zero='Update strategy rollingUpdate maxSurge should be set to 0.'
    if ROLLING_UPDATE in update_strategy and MAX_UN_AVAILABLE in update_strategy[ROLLING_UPDATE]:
        if update_strategy[ROLLING_UPDATE][MAX_UN_AVAILABLE] != 1:
            errors.setdefault(name, []).append(UPDATE_STRATEGY_ROLLING_UPDATE_MAX_UNAVAILABLE_ERROR)
    elif kind == DEPLOYMENT:
        errors.setdefault(name, []).append(update_strategy_max_unavailable)
    if ROLLING_UPDATE in update_strategy and max_surge in update_strategy[ROLLING_UPDATE]:
        if update_strategy[ROLLING_UPDATE][max_surge] != 0 and replicas >= 1:
            errors.setdefault(name, []).append(udpate_rolling_maxsurge_to_zero)
    elif replicas > 1:
        errors.setdefault(name, []).append('Update strategy rollingUpdate maxSurge not set.')


def is_partition_set_to_rolling_update_strategy(name, update_strategy, errors):
    '''
    Check whether partition is set with rolling update strategy or not.
    '''
    partition = 'partition'
    update_strat_not_set='Update strategy rollingUpdate partition not set. It should be set to 0.'
    update_strategy_part_should_set='Update strategy rollingUpdate partition should be set to 0.'
    if ROLLING_UPDATE in update_strategy and partition in update_strategy[ROLLING_UPDATE]:
        if update_strategy[ROLLING_UPDATE][partition] != 0:
            errors.setdefault(name, []).append(update_strategy_part_should_set)
    else:
        errors.setdefault(name, []).append(update_strat_not_set)


def validate_update_strategy(name, kind, update_strategy, errors, replicas):
    '''
    Validates whether update strategy is rolling update or not.
    '''
    is_update_strategy_set_to_rolling_update(name, update_strategy, errors, replicas)
    if ROLLING_UPDATE in update_strategy or (TYPE in update_strategy and
                                                    update_strategy[TYPE] == ROLLING_UPDATE_TYPE):
        if kind in [DAEMON_SET, DEPLOYMENT]:
            is_max_unavail_max_surge_set_to_rolling_update(name, kind,
                                                             update_strategy, errors, replicas)
        if kind == STATEFUL_SET:
            is_partition_set_to_rolling_update_strategy(name, update_strategy, errors)
    else:
        if kind in [DAEMON_SET, DEPLOYMENT] and TYPE in update_strategy \
                                        and RECREATE not in update_strategy[TYPE]:
            errors.setdefault(name, []).append('Update strategy rollingUpdate not set.')


def get_update_strategy(name, kind, spec, errors):
    '''
    Gets the update strategy for a workload in spec.
    '''
    update_strategy = None
    update_strategy_type = 'updateStrategy'
    strategy = 'strategy'
    if kind in [DAEMON_SET, DEPLOYMENT, STATEFUL_SET]:
        update_strategy_format = None
        if kind in [DAEMON_SET, STATEFUL_SET]:
            update_strategy_format = update_strategy_type
        if kind == DEPLOYMENT:
            update_strategy_format = strategy
        if update_strategy_format in spec:
            update_strategy = spec[update_strategy_format]
        else:
            if kind in [DAEMON_SET, DEPLOYMENT]:
                errors.setdefault(name, []).append('Update strategy not set.')
    return update_strategy


def get_containers_for_kafka(template, name, containers_manifest):
    '''
    Get container information from kafka cluster
    '''
    if isinstance(template[name], dict):
        if 'resources' in template[name]:
            container = template[name]
            container['name'] = name
            container.setdefault('image', '')
            containers_manifest.append(container)
        else:
            for container_name in template[name]:
                get_containers_for_kafka(template[name], container_name, containers_manifest)


def get_pvcs_for_kafka(template, name, custom_resource, pvcs_manifest):
    '''
    Get pvcs information from kafka cluster
    '''
    zoo_keeper_volume_path = [custom_resource, 'storage']
    kafka_volume_path = [custom_resource, 'storage', 'volumes']

    if check_path_in_dict(template, kafka_volume_path):
        for volume in template[custom_resource]['storage']['volumes']:
            volume_name =  f'data-{volume["id"]}-{name}-{custom_resource}'
            pvc_manifest = generate_pvc_manifest(volume_name, volume['size'])
            pvcs_manifest.append(pvc_manifest)
    elif check_path_in_dict(template, zoo_keeper_volume_path):
        volume_name =  f'data-{name}-{custom_resource}'
        volume_size = template[custom_resource]['storage']['size']
        pvc_manifest = generate_pvc_manifest(volume_name, volume_size)
        pvcs_manifest.append(pvc_manifest)


def validate_node_selector(name, template_spec, errors):
    '''
    Validates whether node selector is configured or not.
    '''
    node_selector = 'nodeSelector'
    if node_selector in template_spec:
        node_selector = template_spec[node_selector]
        if node_selector['testSelectorKey'] != 'testSelectorValue':
            errors.setdefault(name, []).append('Node selector not set to correct value.')
    else:
        errors.setdefault(name, []).append('Node selector is not defined.')


@dataclass
class EntryBase:
    '''
    Holds the chart and it's name.
    '''
    chart: str
    name: str

    def ser(self) -> Dict[str, Any]:
        '''
        Serializes the Chart information.
        '''
        return {
            "chart": self.chart,
            "name": self.name
        }


@dataclass
class Selector:
    '''
    Has the implementation of selector in the manifest.
    '''
    # Match-label set. e.g.: [('appname': 'myapp'), ('labelname': 'value')]
    match_labels: Set[Tuple[str, str]]

    @classmethod
    def from_manifest(cls, manifest) -> 'Selector':
        '''
        Initializes the instances attributes from parsed manifest.
        '''
        # https://kubernetes.io/docs/reference/kubernetes-api/common-definitions/label-selector/#LabelSelector

        if 'matchLabels' in manifest:
            return cls(set(manifest['matchLabels'].items()))
        if 'matchExpressions' in manifest:
            mls = set()
            for lsr in manifest['matchExpressions']:
                if 'operator' not in lsr or 'values' not in lsr or 'key' not in lsr:
                    log.warning('Bad selector syntax: "operator", "values" and "key" fields are' \
                                                        ' required')
                    continue
                if lsr['operator'] == 'In':
                    values = lsr['values']
                    if len(values) == 1:
                        mls.add((lsr['key'], values[0]))
                    else:
                        log.warning('Multiple values are not yet supported by LabelSelector')
                        continue
                else:
                    log.warning('Operator "%s" is not yet implemented for LabelSelector',
                                                                         lsr['operator'])
                    continue
            return cls(mls)
        return cls(set())  # Empty set, should be matching against all other set

    def match(self, labels) -> bool:
        '''
        Checks whether given labels is subset of matchlabels or not.
        '''
        return self.match_labels.issubset(labels)

    def ser(self):
        '''
        Serializes the Selector information.
        '''
        return dict(self.match_labels)


@dataclass
class PDB(EntryBase):
    '''
    This class holds the selector, pdb type and its value for a workload.
    '''
    selector: Selector
    pdbtype: str
    value: int

    @classmethod
    def from_manifest(cls, chart, manifest) -> 'PDB':
        '''
        Initializes the instances attributes from parsed manifest.
        '''
        spec = manifest['spec']
        selector = spec['selector']
        if MAX_UN_AVAILABLE in spec:
            availability = MAX_UN_AVAILABLE
            availability_count = spec[availability]
        elif 'minAvailable' in spec:
            availability = 'minAvailable'
            availability_count = spec[availability]
        else:
            availability = 'NOT SPECIFIED'
            availability_count = 0
        return cls(
            chart,
            manifest['metadata']['name'],
            Selector.from_manifest(selector),
            availability,
            availability_count
        )

    def ser(self):
        '''
        Serializes the PDB information.
        '''
        return {
            "type": self.pdbtype,
            "value": self.value
        }


@dataclass
class PVCRR:
    '''
    Holds PVC resource requirements.
    '''
    size: int = 0

    def __iadd__(self, pvc_rr):
        '''
        Performs addition of PVC resources size.
        '''
        self.size += pvc_rr.size
        return self

    def __mul__(self, pvc_rr):
        '''
        Performs multiplication of PVC resources size.
        '''
        return PVCRR(self.size * pvc_rr)

    @classmethod
    def parse(cls, requests):
        '''
        Prases the storage requirements.
        '''
        return cls(parse_mem(requests.get('storage'), base=30))


@dataclass
class PVC(EntryBase):
    '''
    This class stores the PVC information.
    '''
    type: str
    storage_class: str
    appname: str
    instances: int
    app_enabled: bool
    default_scope: str
    rollback_scope: str
    pvc_resource_requirements: PVCRR = PVCRR()

    typeFinder = objfinder('spec.accessModes.*')
    storageClassFinder = objfinder('spec.storageClassName')
    appnameFinder = objfinder('metadata.labels."app.kubernetes.io/name"')

    resReqFinder = objfinder('spec.resources.requests')

    @classmethod
    def from_manifest(cls, chart, manifest, errors, bur_config, instances=1):
        '''
        Initializes all the instance attributes from the manifest.
        '''
        pvc_name = manifest['metadata']['name']
        default_scope = ""
        rollback_scope = ""

        app_enabled = True # Logic will come in optionality story

        bur_pvc = bur_config["pvcs"].get(pvc_name)
        if bur_pvc:
            default_scope = "✓"
            if bur_pvc['rollback']:
                rollback_scope = "✓"

        req = cls.resReqFinder(manifest)
        if not req:
            errors.setdefault(pvc_name, []).append("No resource requests are specified for PVC.")
            req = {}

        return cls(
            chart,
            pvc_name,
            ', '.join([PVC_ACCESSMODE_MAP[am] for am in cls.typeFinder(manifest)]),
            cls.storageClassFinder(manifest) or '',
            cls.appnameFinder(manifest) or '',
            instances,
            app_enabled,
            default_scope,
            rollback_scope,
            PVCRR.parse(req)
        )

    def ser(self):
        '''
        Serializes the PVC information.
        '''
        storage_class_info = super().ser()
        storage_class_info.update({
            "type": self.type,
            "storageClass": self.storage_class,
            "appName": self.appname,
            "instances": self.instances,
            "size": self.pvc_resource_requirements.size,
            "app_enabled": self.app_enabled,
            "total": self.instances * self.pvc_resource_requirements.size,
            "fullBackup": self.default_scope,
            "rollback": self.rollback_scope
        })
        return storage_class_info


@dataclass
class ContainerRR:
    '''
    This holds the container resource requirements.
    '''
    cpu_req: int = 0
    cpu_lim: int = 0
    mem_req: int = 0
    mem_lim: int = 0
    eps_req: int = 0
    eps_lim: int = 0

    def __iadd__(self, resource_requirements):
        '''
        Performs addition of container resources.
        '''
        self.cpu_req += resource_requirements.cpu_req
        self.cpu_lim += resource_requirements.cpu_lim
        self.mem_req += resource_requirements.mem_req
        self.mem_lim += resource_requirements.mem_lim
        self.eps_req += resource_requirements.eps_req
        self.eps_lim += resource_requirements.eps_lim
        return self

    def __mul__(self, resource_requirements):
        '''
        Performs multiplication of container resources.
        '''
        return ContainerRR(
            self.cpu_req * resource_requirements,
            self.cpu_lim * resource_requirements,
            self.mem_req * resource_requirements,
            self.mem_lim * resource_requirements,
            self.eps_req * resource_requirements,
            self.eps_lim * resource_requirements
        )

    @classmethod
    def parse(cls, requests, limits) -> 'ContainerRR':
        '''
        Parses the container requirements.
        '''
        return cls(
            parse_cpu(requests.get('cpu')),
            parse_cpu(limits.get('cpu')),
            parse_mem(requests.get('memory'), base=20),
            parse_mem(limits.get('memory'), base=20),
            parse_mem(requests.get('ephemeral-storage'), base=30),
            parse_mem(limits.get('ephemeral-storage'), base=30)
        )


@dataclass
class Container(EntryBase):
    '''
    This class holds the container information.
    '''
    image: str
    resource_requirements: ContainerRR

    resReqFinder = objfinder('resources.requests')
    resLimFinder = objfinder('resources.limits')
    resReqFinderSecondary = objfinder('resourceRequirements.requests')
    resLimFinderSecondary = objfinder('resourceRequirements.limits')

    @classmethod
    def from_manifest(cls, chart, manifest, errors):
        '''
        Initializes the instance attributes from the manifest.
        '''
        name = manifest['name']
        image = manifest['image'].split('/').pop()

        req = cls.resReqFinder(manifest)
        if not req:
            req = cls.resReqFinderSecondary(manifest)
            if not req:
                errors.setdefault(name, []).append('No resource requests are specified for container.')
                req = {}

        lim = cls.resLimFinder(manifest)
        if not lim:
            lim = cls.resLimFinderSecondary(manifest)
            if not lim:
                errors.setdefault(name, []).append('No resource limits are specified for container.')
                lim = {}

        return cls(
            chart,
            name,
            image,
            ContainerRR.parse(req, lim)
        )

    def ser(self):
        '''
        Serializes the Container information.
        '''
        return {
            "name": self.name,
            "image": self.image,
            "cpu_req": self.resource_requirements.cpu_req,
            "cpu_lim": self.resource_requirements.cpu_lim,
            "mem_req": self.resource_requirements.mem_req,
            "mem_lim": self.resource_requirements.mem_lim,
            "eps_req": self.resource_requirements.eps_req,
            "eps_lim": self.resource_requirements.eps_lim
        }


@dataclass
class WLRR:
    '''
    Holds workload resources requirements information.
    '''
    cpu_req: int = 0
    cpu_lim: int = 0
    mem_req: int = 0
    mem_lim: int = 0
    eps_req: int = 0
    eps_lim: int = 0


@dataclass
class WL(EntryBase):
    '''
    This class holds workload details.
    '''
    kind: str
    service_group: str
    replicas: int
    containers: List[Container]
    pvcs: List[str]
    labels: Set[Tuple[str, str]]
    update_strategy: Dict
    resource_requirements: WLRR
    app_enabled: bool
    pdb: Optional[PDB]
    affinity: str = field(default=NA_STRING)

    labelsFinder = objfinder('metadata.labels')
    templateSpecFinder = objfinder('template.spec')
    jobTemplateSpecFinder = objfinder('jobTemplate.spec.template.spec')
    podTemplateSpecFinder = objfinder('podTemplate.spec')
    containersFinder = objfinder('containers.*')
    volumeClaimTemplatesFinder = objfinder('volumeClaimTemplates.*')
    persistentVolumeClaimFinder = objfinder('volumes.*.persistentVolumeClaim.claimName!')

    @classmethod
    def from_manifest(cls, chart, manifest, values_file_name, errors, bur_config, optional_apps,
                      skip_validate_update_strategy = False,
                      custom_resource= None) -> Tuple['WL', List[PVC]]:
        '''
        Initializes the instances attributes from parsed manifest.
        '''
        spec = manifest['spec']
        kind = manifest[KIND]

        name = manifest['metadata']['name']
        labels = cls.labelsFinder(manifest)
        if not isinstance(labels, dict):
            labels = {}

        if kind == 'CronJob':
            template_spec = cls.jobTemplateSpecFinder(spec)
        elif kind == 'RedisCluster':
            template_spec = cls.podTemplateSpecFinder(spec)
        elif kind in EIC_CRD_KAFKA:
            template_spec = spec
        elif kind in EIC_CRD_CASSANDRA:
            template_spec = custom_resource
        else:
            template_spec = cls.templateSpecFinder(spec)

        if not isinstance(template_spec, dict):
            log.error("WL %s does not have a template", name)
            raise SystemExit(1)

        if kind == DAEMON_SET:
            replicas = -1
        elif kind == REDIS_CLUSTER:
            replicas = spec['numberOfMaster'] + (spec['replicationFactor']*spec['numberOfMaster'])
        elif kind in EIC_CRD_KAFKA and custom_resource:
            path = [custom_resource, 'replicas']
            if check_path_in_dict(template_spec, path):
                replicas = template_spec[custom_resource]['replicas']
            else:
                replicas = 1
        elif kind in EIC_CRD_CASSANDRA and custom_resource:
            if 'replicas' in custom_resource:
                replicas = custom_resource['replicas']
            else:
                replicas = 1
        else:
            replicas = spec.get('replicas')
            if replicas is None:
                if kind not in ['CronJob', 'Job']:
                    errors.setdefault(name, []).append('No Replica value set.')
                replicas = 1
        pvcs = []
        used_pvcs = []

        for volume_claim in cls.volumeClaimTemplatesFinder(spec):
            volume_claim['metadata']['name'] += f"-{name}"
            pvc = PVC.from_manifest(chart, volume_claim, errors, bur_config, replicas)
            pvcs.append(pvc)
            used_pvcs.append(pvc.name)

        for persistent_volume_claim in cls.persistentVolumeClaimFinder(template_spec):
            if isinstance(persistent_volume_claim, KeyError):
                errors.setdefault(name, []).append('PVC name not set.')
                continue
            used_pvcs.append(persistent_volume_claim)

        affinity = parse_pod_anti_affinity(manifest, name, values_file_name, replicas, errors)

        if kind == 'Job':
            app_enabled = check_wl_enabled(name, optional_apps, 'Job')
        else:
            app_enabled = check_wl_enabled(name, optional_apps)

        update_strategy = get_update_strategy(name, kind, spec, errors)
        if not skip_validate_update_strategy:
            if update_strategy and replicas > 0:
                validate_update_strategy(name, kind, update_strategy, errors, replicas)
            validate_node_selector(name, template_spec, errors)

        workload_resource_requirements = WLRR()
        containers = []
        containers_manifest = []
        pvcs_manifest = []

        if kind in [EIC_CRD_KAFKA, EIC_CRD_CASSANDRA] and custom_resource:
            if kind == EIC_CRD_KAFKA:
                get_containers_for_kafka(template_spec, custom_resource, containers_manifest)
                get_pvcs_for_kafka(template_spec, name, custom_resource, pvcs_manifest)
            elif kind == EIC_CRD_CASSANDRA:
                containers_manifest = get_containers_for_cassandra(template_spec)
                pvcs_manifest = get_pvcs_for_cassandra(template_spec)

            for volume_claim in pvcs_manifest:
                pvc = PVC.from_manifest(chart, volume_claim, errors, bur_config, replicas)
                pvcs.append(pvc)
                used_pvcs.append(pvc.name)
        else:
            containers_manifest = cls.containersFinder(template_spec)

        for container_manifest in containers_manifest:
            container = Container.from_manifest(chart, container_manifest, errors)
            workload_resource_requirements.cpu_req += container.resource_requirements.cpu_req
            workload_resource_requirements.cpu_lim += container.resource_requirements.cpu_lim
            workload_resource_requirements.mem_req += container.resource_requirements.mem_req
            workload_resource_requirements.mem_lim += container.resource_requirements.mem_lim
            workload_resource_requirements.eps_req += container.resource_requirements.eps_req
            workload_resource_requirements.eps_lim += container.resource_requirements.eps_lim
            containers.append(container)
        workload = cls(
            chart,
            name,
            kind,
            labels.get('sgname', ''),
            replicas,
            containers,
            used_pvcs,
            set(labels.items()),
            update_strategy,
            workload_resource_requirements,
            app_enabled,
            None,
            affinity
        )
        return workload, pvcs

    def ser(self):
        '''
        Serializes the workload information.
        '''
        workload_info = super().ser()
        pdb_value = None
        if isinstance(self.pdb, PDB):
            pdb_value = self.pdb.ser()
        elif self.pdb is None and self.replicas <= 1:
            pdb_value = NA_STRING

        workload_info.update({
            "kind": self.kind,
            "sg": self.service_group,
            "replicas": self.replicas,
            "containers": [c.ser() for c in self.containers],
            "pvcs": self.pvcs,
            "affinity": self.affinity,
            "update_strategy": self.update_strategy,
            "pdb": pdb_value,
            "cpu_req": self.resource_requirements.cpu_req,
            "cpu_lim": self.resource_requirements.cpu_lim,
            "mem_req": self.resource_requirements.mem_req,
            "mem_lim": self.resource_requirements.mem_lim,
            "eps_req": self.resource_requirements.eps_req,
            "eps_lim": self.resource_requirements.eps_lim,
            "app_enabled": self.app_enabled,
        })
        return workload_info
