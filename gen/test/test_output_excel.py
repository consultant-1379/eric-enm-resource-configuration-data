import os

import yaml
from model.config import Config
from model.summary import Summary
from output.output_excel import Storage

data_resources_folder_path = 'test/resources/data/eric-enm-integration-production-values'
eic_data_resources_folder_path = 'test/resources/data/eric-eic-integration-fixed-size-production-values'
cenm_21_10_90 = '21.10.90.xlsx'
cenm_21_13_18 = '21.13.18.xlsx'
config_file_path = 'gen/test/resources/config.test.yaml'
index_json_path = 'test/resources/data/index.json'
test_resources_data_path = 'gen/test/resources/data'
cenm_21_13_18_path = os.path.join(data_resources_folder_path, cenm_21_13_18)
eic_version = '2.90.0'
eic_xl_output = 'EIC Application.xlsx'
eic_xl_output_dir_path = os.path.join(eic_data_resources_folder_path, eic_version)
eic_xl_output_file_path = os.path.join(eic_xl_output_dir_path, eic_xl_output)

def test_excel_file_created():
    try:
        os.makedirs(data_resources_folder_path, exist_ok=True)
        variant = 'eric-enm-integration-production-values'
        version = '21.13.18'
        s = Summary()
        wl = {'chart': 'pre-deploy',
              'name': 'rwxpvc-bragent',
              'kind': 'Deployment',
              'sg': '',
              'replicas': 1,
              'chart': 'Chart1',
              'containers': [
                  {'name': 'cname1', 'image': 'img1', 'cpu_req': 10.0, 'cpu_lim': 50.0, 'mem_req': 128.0, 'mem_lim': 640.0, 'eps_req': 0, 'eps_lim': 0},
                  {'name': 'cname2', 'image': 'img2', 'cpu_req': 50.0, 'cpu_lim': 100.0, 'mem_req': 50.0, 'mem_lim': 100.0, 'eps_req': 0, 'eps_lim': 0}
                  ],
              'cpu_req': 1050.0,
              'cpu_lim': 5100.0,
              'mem_req': 178.0,
              'mem_lim': 740.0,
              'pvcs': [],
              'app_enabled': True,
              'update_strategy': '',
              'pdb': ''}
        s.workloads = [wl]
        pvc = {'chart': 'pre-deploy',
               'name': 'eric-enm-rwxpvc-amos',
               'type': 'RWX',
               'appName': 'rwxpvc',
               'instances': 1,
               'app_enabled': True,
               'fullBackup': '✓',
               'rollback': '',
               'size': 100.0,
               'storageClass': ''}
        s.pvcs = [pvc]
        config = Config.parse(
            yaml.load(open(config_file_path, 'r', encoding='utf-8').read(), yaml.Loader))
        exstorage = Storage(config)
        workbook = exstorage.generate_workbook(s, variant, version)
        workbook.save(cenm_21_13_18_path)
        assert os.path.isfile(cenm_21_13_18_path)
    finally:
        if os.path.isfile(cenm_21_13_18_path):
            os.remove(cenm_21_13_18_path)
