'''
This file holds the implementation of product set summary.
'''
from typing import List
from dataclasses import dataclass
from .resource_requirements import EntryBase, PVC, WL, check_wl_enabled
from .overview import Overview


@dataclass
class ConfigObject(EntryBase):
    '''
    This class returns the Config object.
    '''
    app_enabled: bool
    @classmethod
    def from_manifest(cls, chart, manifest, optional_apps) -> 'ConfigObject':
        '''
        Initializes the instances attributes from parsed manifest.
        '''
        name = manifest['metadata']['name']

        app_enabled = check_wl_enabled(name, optional_apps)

        config_object = cls(
            chart,
            name,
            app_enabled
        )
        return config_object

    def ser(self):
        '''
        Serializes the ConfigObject information.
        '''
        return {
            "chart": self.chart,
            "name": self.name,
            "app_enabled": self.app_enabled,
        }


@dataclass
class ConfigMap(ConfigObject):
    '''
    This class holds the configmaps.
    '''
    pass


@dataclass
class Secret(ConfigObject):
    '''
    This class holds the Secrets.
    '''
    pass


@dataclass
class Service(ConfigObject):
    '''
    This class holds the Service information.
    '''
    pass


@dataclass
class Ingress(ConfigObject):
    '''
    This class holds Ingress information.
    '''
    pass


@dataclass
class EricIngress(ConfigObject):
    '''
    This class holds Eric Ingress information.
    '''
    pass

class ResourceRequestsLimits:
    '''
    This class contains the resource requests and limits information.
    '''
    def __init__(self) -> None:
        '''
        Initializes the Summary instance.
        '''
        self.cpu_lim = 0
        self.cpu_req = 0
        self.mem_lim = 0
        self.mem_req = 0

class Summary:
    '''
    This class contains the cENM product set information.
    '''
    def __init__(self) -> None:
        '''
        Initializes the Summary instance.
        '''
        self.workloads: List[WL] = []
        self.pvcs: List[PVC] = []
        self.csar: List[dict] = []
        self.config_maps: List[ConfigMap] = []
        self.secrets: List[Secret] = []
        self.services: List[Service] = []
        self.ingresses: List[Ingress] = []
        self.eric_ingresses: List[EricIngress] = []
        self.overview: Overview = Overview()
        self.optional_value_packs: List = []
        self.validation_errors: List[dict] = []

    def __repr__(self) -> str:
        '''
        Returns the string description of WLs and PVCs.
        '''
        obj_str_repr = ['WLs:']
        obj_str_repr += [f"  {wl}" for wl in self.workloads]
        obj_str_repr += ['\nPVCs:']
        obj_str_repr += [f"  {pvc}" for pvc in self.pvcs]
        return '\n'.join(obj_str_repr)


class EICSummary(Summary):
    '''
        This class contains EIC product set information.
    '''
    def __init__(self) -> None:
        super().__init__()
        self.istio_side_cars = []
        self.istio_cpu_limit = 0
        self.istio_cpu_request = 0
        self.istio_mem_limit = 0
        self.istio_mem_request = 0
