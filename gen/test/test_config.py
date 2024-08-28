from model.config import CVersion, Version, Config


def test_cversion_parse_psv():
    exp_result = CVersion(psv=Version(
        drop='21.11', version='21.11.38-3', raw=(21, 11, 38, 3)), release=None, present=False)
    assert CVersion.parse({'psv': '21.11.38-3'}) == exp_result


def test_config_parse():
    m = {'output_folder': 'data',
         'variants': [{'name': 'Small Cloud Native ENM',
                       'short_name': 'Small cENM',
                       'offering': 'cENM',
                       'id': 'eric-enm-integration-production-values'},
                      {'name': 'Extra-Large Cloud Native ENM',
                       'short_name': 'Extra-Large cENM',
                       'offering': 'cENM',
                       'id': 'eric-enm-integration-extra-large-production-values'}]}
    exp_result = Config('data',
                        {'eric-enm-integration-production-values':
                            ('Small Cloud Native ENM', 'Small cENM'),
                            'eric-enm-integration-extra-large-production-values':
                                ('Extra-Large Cloud Native ENM', 'Extra-Large cENM')})
    assert Config.parse(m) == exp_result


def test_config_get_variant():
    cfg = Config('data',
                 {'eric-enm-integration-production-values':
                  ('Small Cloud Native ENM', 'Small cENM'),
                  'eric-enm-integration-extra-large-production-values':
                  ('Extra-Large Cloud Native ENM', 'Extra-Large cENM')})
    assert cfg.get_variant(
        'eric-enm-integration-production-values') == ('Small Cloud Native ENM', 'Small cENM')
