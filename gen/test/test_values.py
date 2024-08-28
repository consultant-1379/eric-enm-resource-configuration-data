from model.values import Values


def test_values_prepare():
    v = Values(name='eric-enm-integration-production-values',
               values={'global': {'pullSecret': None,
                                  'registry': {'url': None, 'pullSecret': None},
                                  'vips': {'fm_vip_address': None, 'cm_vip_address': None}}})
    v_exp_res = Values(name='eric-enm-integration-production-values',
                       values={'global': {'pullSecret': None,
                                          'registry': {'url': None, 'pullSecret': None},
                                          'vips': {}}})

    v.prepare(basic_values_preparator)
    assert v == v_exp_res


def test_values_parse():
    yaml_bytes = b"global:\n  persistentVolumeClaim:\n    storageClass: null\n  ingress:\n    enmHost: null\n  nodeSelector: null\n"
    exp_response = Values(name='eric-enm-integration-production-values',
                          values={'global': {'persistentVolumeClaim': {'storageClass': None},
                                             'ingress': {'enmHost': None},
                                             'nodeSelector': None}})
    assert Values.parse(
        'eric-enm-integration-production-values', yaml_bytes) == exp_response


def basic_values_preparator(values):
    values['global']['vips'] = {}
