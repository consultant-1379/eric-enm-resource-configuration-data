'''
This file contains the Overview informaiton of cENM Product set information.
'''
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Overview:
    '''
    This class holds the product set informaiton.
    '''
    total: Dict[str, int] = field(default_factory=lambda: ({
        'pods': 0,
        'rwo': 0,
        'rwx': 0
    }))
    sum: Dict[str, int] = field(default_factory=lambda: ({
        'rwo': 0,
        'rwx': 0
    }))
    requests: Dict[str, int] = field(default_factory=lambda: ({
        'wl_cpu': 0,
        'wl_mem': 0,
        'wl_disk': 0,
        'wlds_cpu': 0,
        'wlds_mem': 0,
        'wlds_disk': 0,
        'wl_jobs_cpu': 0,
        'wl_jobs_mem': 0,
        'wl_jobs_disk': 0
    }))
    limits: Dict[str, int] = field(default_factory=lambda: ({
        'wl_cpu': 0,
        'wl_mem': 0,
        'wl_disk': 0,
        'wlds_cpu': 0,
        'wlds_mem': 0,
        'wlds_disk': 0,
        'wl_jobs_cpu': 0,
        'wl_jobs_mem': 0,
        'wl_jobs_disk': 0
    }))
    max: Dict[str, int] = field(default_factory=lambda: ({
        'replica_count': 0,
        'cpu_req': 0,
        'cpu_lim': 0,
        'mem_req': 0,
        'mem_lim': 0,
        'eps_req': 0,
        'eps_lim': 0
    }))
    min: Dict[str, int] = field(default_factory=lambda: ({
        'worker_nodes': 0,
        'worker_cpu': 0,
        'worker_mem': 0,
        'worker_disk': 0,
        'hot_spare_workers': 1
    }))
    client: Dict[str, str] = field(default_factory=lambda: ({
        'docker': '',
        'helm': '',
        'kubectl': '',
        'cpu': '',
        'memory': '',
        'ports': '',
        'disk': '',
        'python': '',
        'screen': '',
        'unzip': '',
    }))
    cluster: Dict[str, str] = field(default_factory=lambda: ({
        'kubernetes': ''
    }))
    registry: Dict[str, str] = field(default_factory=lambda: ({
        'disk_storage_space': '',
        'ports': '',
    }))
    bur: Dict[str, int] = field(default_factory=lambda: ({
        'storage_requirement_full_backups': 0,
        'storage_requirement_full_backups_compressed': 0,
        'storage_requirement_rollbacks': 0,
        'storage_requirement_rollbacks_compressed': 0,
        'bro_pvc_storage_requirement': 0,
        'external_storage_requirement': 0,
        'number_of_full_backups_on_external_storage': 0,
        'number_of_full_backups_on_bro_pvc': 0,
        'number_of_rollbacks_on_bro_pvc': 0,
    }))
    other_requirements: Dict[str, any] = field(default_factory=lambda: ({
        'ips': 0,
        'pids': 0,
        'ipv6s': 0,
        'load_balancers': 0,
        'supported_ip_versions': [],
    }))
