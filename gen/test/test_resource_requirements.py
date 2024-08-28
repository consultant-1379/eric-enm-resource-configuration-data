import pytest
from model.resource_requirements import (PDB, PVC, PVCRR, WL, Container,
                                         ContainerRR, EntryBase, Selector, WLRR,
                                         parse_cpu, parse_mem, validate_node_selector,
                                         parse_pod_anti_affinity, validate_update_strategy,
                                         get_update_strategy, NA_STRING, get_containers_for_kafka)
APP_NAME = 'app_name'
VALUES_FILE_NAME = 'values_file_name'
OPTIONAL_APPS = [{'version': 21.15,
                 'value_packs': [
                     {
                         'name': 'Event Based Statistics for LTE (EBS-L) and MME (EBS-N)',
                         'tag': 'value_pack_ebs_ln',
                         'description': 'Event Based Statistics for NR contains ebs controller, ebs-flow and ebs-topology services',
                         'variant': 'eric-enm-integration-extra-large-production-values',
                         'applications': [
                             {
                                 'name': 'ebscontroller'
                             },
                             {
                                 'name': 'ebsflow'
                             },
                             {
                                 'name': 'ebstopology'
                             }
                         ],
                         'jobs': [
                             'eric-enm-models-ebs-job'
                         ]
                     }
                 ]
                 }]


def test_parse_cpu():
    assert parse_cpu('100m') == 100
    assert parse_cpu('2') == 2000
    assert parse_cpu(None) == 0


def test_parse_mem():
    assert parse_mem('35Gi', 30) == 35.0
    assert parse_mem('35G', 30) == 32.59629011154175
    assert parse_mem(None, 20) == 0


def test_parse_pod_anti_affinity_none():
    errors = {}
    pod_anti_affinity_na = {'metadata': {'name': 'rwxpvc-bragent'},'kind': 'Deployment', 'spec': {
        'template': {'spec': {'containers': [{'name': 'rwxpvc-bragent'}]}}}}

    assert parse_pod_anti_affinity({}, APP_NAME, VALUES_FILE_NAME, 1, errors) == None

    assert 'Affinity rule without spec.' in errors[APP_NAME]
    assert parse_pod_anti_affinity(pod_anti_affinity_na, APP_NAME, VALUES_FILE_NAME, 1, errors) == NA_STRING


def test_parse_pod_anti_affinity_required_under_scheduling():

    required_under_scheduling_anti_affinity = {
        'metadata': {'name': 'fmalertparser'},
        'spec': {
            'template': {
                'spec': {
                    'affinity': {'podAntiAffinity': {'requiredDuringSchedulingIgnoredDuringExecution':
                                                     [{'labelSelector': {'matchExpressions': [
                                                         {'key': 'app', 'operator': 'In', 'values': ['fmalertparser']}]}}]}}}}}}
    affinity = parse_pod_anti_affinity(required_under_scheduling_anti_affinity, APP_NAME, VALUES_FILE_NAME, 1, {})
    assert affinity == "hard pod anti affinity: {'app': 'fmalertparser'}"


def test_parse_pod_anti_affinity_preferred_under_scheduling():
    preferred_under_scheduling_anti_affinity = {
        'metadata': {'name': 'fmalertparser'},
        'spec': {
            'template': {
                'spec': {
                    'affinity': {'podAntiAffinity':
                                 {'preferredDuringSchedulingIgnoredDuringExecution':
                                  [{'weight': 100, 'podAffinityTerm': {
                                      'labelSelector':
                                      {'matchExpressions': [
                                          {'key': 'app', 'operator': 'In', 'values': ['fmalertparser']}]}}}]}}}}}}
    affinity = parse_pod_anti_affinity(preferred_under_scheduling_anti_affinity, APP_NAME, VALUES_FILE_NAME, 1, {})
    assert affinity == "soft pod anti affinity: {'app': 'fmalertparser'} with weight 100"


def test_parse_pod_anti_affinity_two_affinity_rules_unsupported():
    errors = {}
    exception_two_affinity_rules_not_supported = {
        'metadata': {'name': 'fmalertparser'},
        'spec': {'template': {
            'spec': {'affinity': {
                'podAntiAffinity': {
                    'requiredDuringSchedulingIgnoredDuringExecution':
                    [{'labelSelector': {'matchExpressions':  [
                        {'key': 'app', 'operator': 'In', 'values': ['fmalertparser2']}]}},
                     {'labelSelector': {'matchExpressions': [
                         {'key': 'app', 'operator': 'In', 'values': ['fmalertparser2']}]}}]}}}}}}
    affinity = parse_pod_anti_affinity(exception_two_affinity_rules_not_supported, APP_NAME, VALUES_FILE_NAME, 1, errors)
    assert affinity == None
    assert 'More than one affinity rule specified. Currently only one affinity scheduling rule per workload is supported.' in errors[APP_NAME]


def test_parse_pod_anti_affinity_soft_affinity_not_supported():
    errors = {}
    preferred_under_scheduling_anti_affinity = {
        'metadata': {'name': 'fmalertparser'},
        'spec': {
            'template': {
                'spec': {
                    'affinity': {'podAntiAffinity':
                                 {'preferredDuringSchedulingIgnoredDuringExecution':
                                  [{'weight': 100, 'podAffinityTerm': {
                                      'labelSelector':
                                      {'matchExpressions': [
                                          {'key': 'app', 'operator': 'In', 'values': ['fmalertparser']}]}}}]}}}}}}
    parse_pod_anti_affinity(preferred_under_scheduling_anti_affinity, APP_NAME, 'eric-enm-integration-production-values', 3, errors)
    assert 'Soft anti-affinity cannot be set for small deployment if replicas is <= 3.' in errors[APP_NAME]
    parse_pod_anti_affinity(preferred_under_scheduling_anti_affinity, APP_NAME, 'eric-enm-integration-extra-large-production-values', 8, errors)
    assert 'Soft anti-affinity cannot be set for XL deployment if replicas is <= 8.' in errors[APP_NAME]

def test_validate_update_strategy_type_not_rollingupdate():
    errors = {}
    us_type_not_rolling_update = {
        'rollingUpdate': {
            'maxSurge': 0,
            'maxUnavailable': 1
        },
        'type': 'notRollingUpdate'
    }
    validate_update_strategy(APP_NAME, 'DaemonSet', us_type_not_rolling_update, errors, 1)
    assert 'Update strategy type not set to rolling update.' in errors[APP_NAME]


def test_validate_update_strategy_daemonset_or_deployment_rollingupdate_maxunavailable_not_1():
    errors = {}
    us_daemonset_or_deployment_rollingupdate_maxunavailable_not_1 = {
        'rollingUpdate': {
            'maxSurge': 0,
            'maxUnavailable': 0
        },
        'type': 'RollingUpdate'
    }
    validate_update_strategy(APP_NAME, 'DaemonSet', us_daemonset_or_deployment_rollingupdate_maxunavailable_not_1, errors, 1)

    assert 'Update strategy rollingUpdate maxUnavailable should be set to 1.' in errors[APP_NAME]


def test_validate_update_strategy_deployment_no_rollingupdate_maxunavailable():
    errors = {}
    us_deployment_no_rollingupdate_maxunavailable = {
        'rollingUpdate': {
            'maxSurge': 0,
            'notmaxUnavailable': 1
        },
        'type': 'RollingUpdate'
    }
    validate_update_strategy(APP_NAME, 'Deployment', us_deployment_no_rollingupdate_maxunavailable, errors, 1)
    assert 'Update strategy rollingUpdate maxUnavailable should be set.' in errors[APP_NAME]


def test_validate_update_strategy_daemonset_or_deployment_rollingupdate_maxsurge_not_0():
    errors = {}
    us_daemonset_or_deployment_rollingupdate_maxsurge_not_0 = {
        'rollingUpdate': {
            'maxSurge': 1,
            'maxUnavailable': 1
        },
        'type': 'RollingUpdate'
    }
    validate_update_strategy(APP_NAME, 'DaemonSet', us_daemonset_or_deployment_rollingupdate_maxsurge_not_0, errors, 1)
    assert 'Update strategy rollingUpdate maxSurge should be set to 0.' in errors[APP_NAME]


def test_validate_update_strategy_daemonset_or_deployment_no_rollingupdate_maxsurge():
    errors = {}
    us_daemonset_or_deployment_no_rollingupdate_maxsurge = {
        'rollingUpdate': {
            'notmaxSurge': 0,
            'maxUnavailable': 1
        },
        'type': 'RollingUpdate'
    }
    validate_update_strategy(APP_NAME, 'DaemonSet', us_daemonset_or_deployment_no_rollingupdate_maxsurge, errors, 2)
    assert 'Update strategy rollingUpdate maxSurge not set.' in errors[APP_NAME]


def test_validate_update_strategy_statefulset_rollingupdate_partition_not_0():
    errors = {}
    us_statefulset_rollingupdate_partition_not_0 = {
        'type': 'RollingUpdate',
        'rollingUpdate': {
            'partition': 1
        }
    }
    validate_update_strategy(APP_NAME, 'StatefulSet', us_statefulset_rollingupdate_partition_not_0, errors, 1)
    assert 'Update strategy rollingUpdate partition should be set to 0.' in errors[APP_NAME]


def test_validate_update_strategy_daemonset_or_deployment_no_rollingupdate():
    errors = {}
    us_daemonset_or_deployment_no_rollingupdate = {
        'notrollingUpdate': {
            'maxSurge': 0,
            'maxUnavailable': 1
        },
        'type': ''
    }
    validate_update_strategy(APP_NAME, 'DaemonSet', us_daemonset_or_deployment_no_rollingupdate, errors, 1)
    assert 'Update strategy rollingUpdate not set.' in errors[APP_NAME]


def test_get_update_strategy_daemonset_or_statefulset():
    spec_daemonset_or_statefulset = {
        'updateStrategy': {
            'type': 'RollingUpdate',
            'rollingUpdate': {
                'maxUnavailable': 1,
                'maxSurge': 0
            }
        }
    }
    update_strategy = get_update_strategy(APP_NAME, 'DaemonSet', spec_daemonset_or_statefulset, {})
    exp_result = {
        'type': 'RollingUpdate',
        'rollingUpdate': {
            'maxUnavailable': 1,
            'maxSurge': 0
        }
    }
    assert update_strategy == exp_result


def test_get_update_strategy_daemonset_no_updatestrategy():
    errors = {}
    spec_daemonset_no_updatestrategy = {
        'notupdateStrategy': {
            'type': 'RollingUpdate',
            'rollingUpdate': {
                'maxUnavailable': 1,
                'maxSurge': 0
            }
        }
    }
    get_update_strategy(APP_NAME, 'DaemonSet', spec_daemonset_no_updatestrategy, errors)
    assert 'Update strategy not set.' in errors[APP_NAME]


def test_get_update_strategy_deployment():
    spec_deployment = {
        'strategy': {
            'type': 'RollingUpdate',
            'rollingUpdate': {
                'maxUnavailable': 1,
                'maxSurge': 0
            }
        }
    }
    update_strategy = get_update_strategy(APP_NAME, 'Deployment', spec_deployment, {})
    exp_result = {
        'type': 'RollingUpdate',
        'rollingUpdate': {
            'maxUnavailable': 1,
            'maxSurge': 0
        }
    }
    assert update_strategy == exp_result


def test_get_update_strategy_deployment_no_updatestrategy():
    errors = {}
    spec_deployment_no_updatestrategy = {
        'notstrategy': {
            'type': 'RollingUpdate',
            'rollingUpdate': {
                'maxUnavailable': 1,
                'maxSurge': 0
            }
        }
    }
    get_update_strategy(APP_NAME, 'Deployment', spec_deployment_no_updatestrategy, errors)
    assert 'Update strategy not set.' in errors[APP_NAME]



def test_get_update_strategy_not_daemonset_or_deployment_or_statefulset():
    spec_not_daemonset_or_deployment_or_statefulset = {
        'spec': {
            'strategy': {
                'type': 'RollingUpdate',
                'rollingUpdate': {
                    'maxUnavailable': 1,
                    'maxSurge': 0
                }
            }
        }
    }
    update_strategy = get_update_strategy('wlname', 'notDaemonset', spec_not_daemonset_or_deployment_or_statefulset, {})
    exp_result = None
    assert update_strategy == exp_result

def test_entry_base_ser():
    eb = EntryBase(chart='monitoring', name='name')
    assert eb.ser() == {'chart': 'monitoring', 'name': 'name'}


def test_selector_from_manifest_match_expression():
    m_match_expression = {'matchExpressions': [
        {'key': 'app', 'operator': 'In', 'values': ['fmalertparser']}]}
    exp_response = Selector(match_labels={('app', 'fmalertparser')})
    assert Selector.from_manifest(m_match_expression) == exp_response


def test_selector_from_manifest_match_label():
    m_match_label = {'matchLabels': {'app': 'fmalertparser'}}
    exp_response = Selector(match_labels={('app', 'fmalertparser')})
    assert Selector.from_manifest(m_match_label) == exp_response


def test_selector_from_manifest_missing_key(caplog):
    m_missing_key = {'matchExpressions': [
        {'operator': 'In', 'values': ['fmalertparser']}]}
    assert Selector.from_manifest(m_missing_key) == Selector(set())
    out = caplog.text
    assert 'Bad selector syntax: \"operator\", \"values\" and \"key\" fields are required' in out


def test_selector_from_manifest_match_expression_multiple_values(caplog):
    m_match_expression_multiple_values = {'matchExpressions': [
        {'key': 'app', 'operator': 'In', 'values': ['fmalertparser', 'another']}]}
    assert Selector.from_manifest(
        m_match_expression_multiple_values) == Selector(set())
    out = caplog.text
    assert 'Multiple values are not yet supported by LabelSelector' in out


def test_selector_from_manifest_unsupported_operator(caplog):
    m_match_unsupported_operator = {'matchExpressions': [
        {'key': 'app', 'operator': 'gt', 'values': ['fmalertparser']}]}
    assert Selector.from_manifest(
        m_match_unsupported_operator) == Selector(set())
    out = caplog.text
    assert 'Operator \"gt\" is not yet implemented for LabelSelector' in out


def test_selector_from_manifest_no_expresion_or_label():
    assert Selector.from_manifest({}) == Selector(set())


def test_selector_match():
    sel = Selector({('fmalertparser')})
    assert sel.match(('app', 'fmalertparser'))


def test_pdb_from_manifest_max_unavailable():
    m_max_unavailable = {'metadata': {'name': 'eric-enm-fm-alert-parser-pdb'},
                         'spec': {'maxUnavailable': 1, 'selector': {'matchLabels': {'app': 'fmalertparser'}}}}
    exp_response = PDB('monitoring', 'eric-enm-fm-alert-parser-pdb',
                       Selector(match_labels={('app', 'fmalertparser')}), 'maxUnavailable', 1)
    assert PDB.from_manifest('monitoring', m_max_unavailable) == exp_response


def test_pdb_from_manifest_min_unavailable():
    m_min_unavailable = {'metadata': {'name': 'eric-enm-fm-alert-parser-pdb'},
                         'spec': {'minAvailable': 1, 'selector': {'matchLabels': {'app': 'fmalertparser'}}}}
    exp_response = PDB('monitoring', 'eric-enm-fm-alert-parser-pdb',
                       Selector(match_labels={('app', 'fmalertparser')}), 'minAvailable', 1)
    assert PDB.from_manifest('monitoring', m_min_unavailable) == exp_response


def test_pdb_from_manifest_not_defined():
    m_not_defined = {'metadata': {'name': 'eric-enm-fm-alert-parser-pdb'},
                     'spec': {'undefined': 1, 'selector': {'matchLabels': {'app': 'fmalertparser'}}}}
    exp_response = PDB('monitoring', 'eric-enm-fm-alert-parser-pdb',
                       Selector(match_labels={('app', 'fmalertparser')}), 'NOT SPECIFIED', 0)
    assert PDB.from_manifest('monitoring', m_not_defined) == exp_response


def test_pdb_ser():
    pdb = PDB('monitoring', 'eric-enm-fm-alert-parser-pdb',
              Selector(match_labels={('app', 'fmalertparser')}), 'NOT SPECIFIED', 0)
    assert pdb.ser() == {'type': 'NOT SPECIFIED', 'value': 0}


def test_pvc_rr_iadd():
    p1 = PVCRR(size=5)
    p2 = PVCRR(size=4)
    p1 += p2
    assert p1.size == 9


def test_pvc_rr_mul():
    p1 = PVCRR(4)
    p2 = p1 * 2
    assert p2.size == 8


def test_pvc_from_manifest():
    bur_config = {"pvcs": {"key": []}}
    m = {'kind': 'PersistentVolumeClaim',
         'metadata': {'name': 'eric-enm-rwxpvc-amos'},
         'spec': {'accessModes': ['ReadWriteMany'],
                  'resources': {'requests': {'storage': '100Gi'}}}}
    exp_response = PVC('pre-deploy', 'eric-enm-rwxpvc-amos',
                       'RWX', '', '', 1, True, '', '', PVCRR(100.0))
    assert PVC.from_manifest('pre-deploy', m, {}, bur_config) == exp_response


def test_pvc_from_manifest_no_requests():
    errors = {}
    bur_config = {"pvcs": {"key": []}}
    m = {'kind': 'PersistentVolumeClaim',
         'metadata': {'name': 'eric-enm-rwxpvc-amos'},
         'spec': {'accessModes': ['ReadWriteMany'],
                  'resources': {...}}}
    exp_response = PVC('pre-deploy', 'eric-enm-rwxpvc-amos',
                       'RWX', '', '', 1, True, '', '', PVCRR(0))
    assert PVC.from_manifest('pre-deploy', m, errors, bur_config) == exp_response
    assert 'No resource requests are specified for PVC.' in errors['eric-enm-rwxpvc-amos']


def test_pvc_ser():
    pvc = PVC('pre-deploy', 'eric-enm-rwxpvc-amos',
              'RWX', 'not set', 'app1', 1, True, '', '', PVCRR(0))
    exp_result = {
        'chart': 'pre-deploy',
        'name': 'eric-enm-rwxpvc-amos',
        'type': 'RWX',
        'storageClass': 'not set',
        'appName': 'app1',
        'instances': 1,
        'size': 0,
        'app_enabled': True,
        'total': 0,
        'fullBackup': '',
        'rollback': ''}
    assert pvc.ser() == exp_result


def test_container_rr_iadd():
    c1 = ContainerRR(cpu_lim=1, cpu_req=1, mem_req=1,
                     mem_lim=1, eps_req=0, eps_lim=1)
    c2 = ContainerRR(cpu_lim=2, cpu_req=1, mem_req=1,
                     mem_lim=1, eps_req=1, eps_lim=0)
    c1 += c2
    assert c1.cpu_lim == 3
    assert c1.cpu_req == 2
    assert c1.mem_req == 2
    assert c1.mem_lim == 2
    assert c1.eps_req == 1
    assert c1.eps_lim == 1


def test_containe_rr_mul():
    c1 = ContainerRR(cpu_lim=2, cpu_req=1, mem_req=1,
                     mem_lim=1, eps_req=0, eps_lim=1)
    c2 = c1 * 2
    assert c2.cpu_lim == 4
    assert c2.cpu_req == 2
    assert c2.mem_req == 2
    assert c2.mem_lim == 2
    assert c2.eps_req == 0
    assert c2.eps_lim == 2


def test_container_ser():
    c = Container('pre-deploy', 'eric-enm-symlink-creation', 'SLESimage',
                  ContainerRR(1000, 5000, 128.0, 640.0, 1.171875, 2.0))
    exp_result = {
        'name': 'eric-enm-symlink-creation',
        'image': 'SLESimage',
        'cpu_req': 1000,
        'cpu_lim': 5000,
        'mem_req': 128.0,
        'mem_lim': 640.0,
        'eps_req': 1.171875,
        'eps_lim': 2.0}
    assert c.ser() == exp_result


def test_container_from_manifest():
    m = {'name': 'eric-enm-symlink-creation',
         'image': 'armdocker.rnd.ericsson.se/proj-enm/eric-enm-sles-base:latest',
         'resources': {'requests': {'memory': '128Mi', 'cpu': '1', 'ephemeral-storage': '1200Mi'},
                       'limits': {'memory': '640Mi', 'cpu': '5', 'ephemeral-storage': '2Gi'}}}
    exp_response = Container('pre-deploy', 'eric-enm-symlink-creation',
                             'eric-enm-sles-base:latest', ContainerRR(1000, 5000, 128.0, 640.0, 1.171875, 2.0))
    assert Container.from_manifest('pre-deploy', m, {}) == exp_response


def test_container_from_manifest_no_response():
    errors = {}
    m = {'name': 'eric-enm-symlink-creation', 'image': 'armdocker.rnd.ericsson.se/proj-enm/eric-enm-sles-base:latest'}
    exp_response = Container(
        'pre-deploy', 'eric-enm-symlink-creation', 'eric-enm-sles-base:latest', ContainerRR())
    assert Container.from_manifest('pre-deploy', m, errors  ) == exp_response
    assert 'No resource requests are specified for container.' in errors['eric-enm-symlink-creation']


def test_wl_from_manifest_stateful_set():
    errors = {}
    bur_config = {"pvcs": {"key": []}}
    m_stateful_set = {'kind': 'StatefulSet',
                      'metadata': {'name': 'eric-pm-alert-manager'},
                      'spec': {'replicas': 3,
                               'updateStrategy': {
                                   'type': 'RollingUpdate',
                                   'rollingUpdate': {
                                       'partition': 0
                                   }
                               },
                               'template': {
                                   'spec': {
                                       'volumes': [
                                           {'name': 'config-volume',
                                               'configMap': {'name': 'eric-pm-alert-manager'}},
                                           {'name': 'amos',
                                            'persistentVolumeClaim': None},
                                           {'name': 'batch', 'persistentVolumeClaim': {'claimName': 'eric-enm-rwxpvc-batch'}}],
                                       'containers': [{'name': 'eric-pm-alert-manager',
                                                       'image': 'armdocker.rnd.ericsson.se/proj-adp-pm-alert-manager-drop/eric-pm-alert-manager:1.1.0-6',
                                                       'resources': {
                                                           'limits': {'cpu': '250m', 'memory': '1024Mi'},
                                                           'requests': {'cpu': '100m', 'memory': '512Mi'}}}]}},
                               'serviceName': 'eric-pm-alert-manager-headless',
                               'volumeClaimTemplates': [
                                   {'metadata': {'name': 'eric-pm-alert-manager-storage'},
                                    'spec': {'accessModes': ['ReadWriteOnce'],
                                             'resources': {'requests': {'storage': '100Gi'}}}}]}}
    exp_stateful_wl = WL('monitoring', 'eric-pm-alert-manager', 'StatefulSet', '', 3,
                         [Container('monitoring', 'eric-pm-alert-manager', 'eric-pm-alert-manager:1.1.0-6',
                                    ContainerRR(100, 250, 512.0, 1024.0, 0, 0))],
                         ['eric-pm-alert-manager-storage-eric-pm-alert-manager',
                          'eric-enm-rwxpvc-batch'], set(), {
                             'type': 'RollingUpdate',
                             'rollingUpdate': {
                                 'partition': 0
                             }
                         }, WLRR(100, 250, 512.0, 1024.0, 0, 0), True, None, None)
    exp_stateful_pvc = [PVC(
        'monitoring', 'eric-pm-alert-manager-storage-eric-pm-alert-manager', 'RWO', '', '', 3, True, '', '', PVCRR(100.0))]
    exp_stateful_response = exp_stateful_wl, exp_stateful_pvc
    assert WL.from_manifest('monitoring', m_stateful_set, VALUES_FILE_NAME, errors, bur_config, OPTIONAL_APPS) == exp_stateful_response
    assert 'PVC name not set.' in errors['eric-pm-alert-manager']
    assert 'No affinity value set.' in errors['eric-pm-alert-manager']
    assert 'Node selector is not defined.' in errors['eric-pm-alert-manager']


def test_wl_from_manifest_daemon_set():
    m_daemon_set = {'kind': 'DaemonSet',
                    'metadata': {'name': 'eric-pm-node-exporter'},
                    'spec': {'replicas': -1,
                             'updateStrategy': {
                                 'type': 'RollingUpdate',
                                 'rollingUpdate': {
                                     'maxUnavailable': 1,
                                     'maxSurge': 0
                                 }
                             },
                             'template': {
                                 'spec': {
                                     'containers': [{
                                         'name': 'eric-pm-node-exporter',
                                         'image': 'armdocker.rnd.ericsson.se/proj_kds/erikube/node-exporter:v0.18.1',
                                         'resources': {
                                             'limits': {'cpu': '200m', 'memory': '150Mi'},
                                             'requests': {'cpu': '100m', 'memory': '100Mi'}}}]}},
                             'serviceName': 'eric-pm-node-exporter-headless'}}
    exp_daemon_set_wl = WL('monitoring', 'eric-pm-node-exporter', 'DaemonSet', '', -1,
                           [Container('monitoring', 'eric-pm-node-exporter', 'node-exporter:v0.18.1',
                                      ContainerRR(100, 200, 100.0, 150.0, 0, 0))], [], set(), {
                               'type': 'RollingUpdate',
                               'rollingUpdate': {
                                   'maxUnavailable': 1,
                                   'maxSurge': 0
                               }
                           }, WLRR(100, 200, 100.0, 150.0, 0, 0), True, None, NA_STRING)
    exp_daemon_set_response = exp_daemon_set_wl, []
    assert WL.from_manifest(
        'monitoring', m_daemon_set, VALUES_FILE_NAME, {}, {}, OPTIONAL_APPS) == exp_daemon_set_response


def test_wl_from_manifest_exception():
    m = {'kind': 'DaemonSet',
         'metadata': {'name': 'eric-pm-node-exporter'},
         'spec': {'replicas': -1}}
    with pytest.raises(SystemExit):
        WL.from_manifest('monitoring', m, VALUES_FILE_NAME, {}, {}, OPTIONAL_APPS)


def test_wl_ser():
    wl = WL('monitoring', 'eric-pm-node-exporter', 'DaemonSet', '', -1,
            [Container('pre-deploy', 'eric-enm-symlink-creation', 'SLESimage',
                       ContainerRR(1000, 5000, 128.0, 640.0, 1.171875, 2.0))], [], set(), {
                'type': 'RollingUpdate',
                'rollingUpdate': {
                    'maxUnavailable': 1,
                    'maxSurge': 0
                }
            }, WLRR, True, None)
    exp_result = {
        'chart': 'monitoring',
        'name': 'eric-pm-node-exporter',
        'kind': 'DaemonSet',
        'sg': '',
        'replicas': -1,
        'containers': [{
            'name': 'eric-enm-symlink-creation',
            'image': 'SLESimage',
            'cpu_req': 1000,
            'cpu_lim': 5000,
            'mem_req': 128.0,
            'mem_lim': 640.0,
            'eps_req': 1.171875,
            'eps_lim': 2.0}],
        'pvcs': [],
        'affinity': NA_STRING,
        'update_strategy': {
            'type': 'RollingUpdate',
            'rollingUpdate': {
                'maxUnavailable': 1,
                'maxSurge': 0
            }
        },
        'pdb': NA_STRING,
        'cpu_req': 0,
        'cpu_lim': 0,
        'mem_req': 0,
        'mem_lim': 0,
        'eps_req': 0,
        'eps_lim': 0,
        'app_enabled': True}
    assert wl.ser() == exp_result

def test_validate_node_selector():
    errors = {}
    spec = {'nodeSelector': {'testSelectorKey': ''}}
    validate_node_selector(APP_NAME, {}, errors)
    assert 'Node selector is not defined.' in errors[APP_NAME]
    spec = {'nodeSelector': {'testSelectorKey': 'wrongSelectorValue'}}
    validate_node_selector(APP_NAME, spec, errors)
    assert 'Node selector not set to correct value.' in errors[APP_NAME]

def test_get_containers_for_kafka_with_resources():
    template = {
        'kafka': {
            'resources': {
                'limits': {
                    'cpu': '2'
                }
            },
            'image': 'kafka:latest'
        }
    }
    name = 'kafka'
    containers_manifest = []

    get_containers_for_kafka(template, name, containers_manifest)

    assert len(containers_manifest) == 1
    assert containers_manifest[0]['name'] == name
    assert containers_manifest[0]['image'] == template['kafka']['image']

def test_get_containers_for_kafka_with_resources_in_one_level_below():
    template = {
        'kafka': {
            'broker': {
                'resources': {
                    'limits': {
                        'cpu': '2'
                    }
                },
                'image': 'broker:latest'
            }
        }
    }
    name = 'kafka'
    containers_manifest = []

    get_containers_for_kafka(template, name, containers_manifest)

    assert len(containers_manifest) == 1
    assert containers_manifest[0]['name'] == 'broker'
    assert containers_manifest[0]['image'] == 'broker:latest'

def test_get_containers_for_kafka_no_dict():
    template = {'kafka': 'not_a_dict'}
    name = 'kafka'
    containers_manifest = []

    get_containers_for_kafka(template, name, containers_manifest)

    assert len(containers_manifest) == 0

def test_get_containers_for_kafka__with_resources_in_different_levels():
    template = {
        'kafka': {
            'broker1': {
                'resources': {
                    'limits': {
                        'cpu': '2'
                    }
                },
                'image': 'broker1:latest'
            },
            'broker2': {
                'resources': {
                    'limits': {
                        'cpu': '3'
                    }
                },
                'image': 'broker2:latest'
            }
        }
    }
    name = 'kafka'
    containers_manifest = []

    get_containers_for_kafka(template, name, containers_manifest)

    assert len(containers_manifest) == 2
    assert containers_manifest[0]['name'] == 'broker1'
    assert containers_manifest[0]['image'] == 'broker1:latest'
    assert containers_manifest[1]['name'] == 'broker2'
    assert containers_manifest[1]['image'] == 'broker2:latest'

