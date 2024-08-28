'''
This file implements storing versions and variants for csar product sets in index.json file.
'''
import json
import dataclasses
from os import makedirs, path
import os
import logging
from model.config import CVersion, Config
from model.version import Version
from model.summary import Summary
from datasrc.ciportal import get_drop_rstate


log = logging.getLogger('output.json')
ENCODING_ASCII= "ascii"


class MyEncoder(json.JSONEncoder):
    '''
    Custom JSON encoder implementation.
    '''
    def default(self, o):
        '''
        it returns a serializable object for o.
        '''
        if hasattr(o, 'ser'):
            return o.ser()
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, Summary):
            return o.__dict__
        return super().default(o)


class Storage:
    '''
    This class stores the variants and versions in index.json file.
    '''
    def __init__(self, config: Config):
        '''
        Initializes all variants and versions in the index.json file if present.
        '''
        self.config = config
        self.folder_path = config.output_folder
        makedirs(self.folder_path, exist_ok=True)
        self.variants = {}
        for variant_name in os.listdir(self.folder_path):
            variant_path = os.path.join(self.folder_path, variant_name)
            if os.path.isdir(variant_path):
                vvset = set()
                for version_name in os.listdir(variant_path):
                    version_path = os.path.join(variant_path, version_name)
                    if os.path.isfile(version_path):
                        vnse = os.path.splitext(version_name)
                        if vnse[1] == '.json':
                            vvset.add(vnse[0])
                    elif os.path.isdir(version_path):
                        vvset.add(version_name)

                self.variants[variant_name] = vvset

    # pylint: disable=too-many-arguments
    def store(self, summary: Summary, variant: str, version: str,
              eic_product = False, eic_app_name = None):
        '''
        Store the version for a variant in index.json file.
        '''
        folder = path.join(self.folder_path, variant)
        makedirs(folder, exist_ok=True)

        if eic_product:
            sub_folder = folder + "/" + version
            makedirs(sub_folder, exist_ok=True)
            folder = sub_folder
            file_name = eic_app_name
        else:
            file_name = version
            self.variants[variant].add(version)

        with open(path.join(folder, file_name + '.json'), 'w',
                                    encoding=ENCODING_ASCII) as index_json_file:
            json.dump(summary, index_json_file, cls=MyEncoder, indent=2)


    def add_version_in_variants(self, version, variant):
        '''
        Adds product set version to the variant
        '''
        if version not in self.variants[variant]:
            self.variants[variant].add(version)


    def store_apps(self, apps, variant: str, version: str):
        '''
        Store the version for a variant in index.json file.
        '''
        folder = path.join(self.folder_path, variant)
        makedirs(folder, exist_ok=True)
        sub_folder = os.path.join(folder, version)
        makedirs(sub_folder, exist_ok=True)

        with open(path.join(sub_folder, 'apps.json'), 'w',
            encoding=ENCODING_ASCII) as apps_json_file:
            json.dump(apps, apps_json_file, cls=MyEncoder, indent=2)


    def load_index_json_if_exists(self):
        '''
        Reading index_json file.
        '''
        if os.path.exists(os.path.join(self.folder_path, 'index.json')):
            with open(os.path.join(self.folder_path, 'index.json'), 'r',
                                    encoding=ENCODING_ASCII) as index_json_file:
                return json.loads(index_json_file.read())
        return []


    def delete_version_if_exists_in_index_json(self, index_json, version, variant):
        '''
        Deletes version if user tries to over-ride with same product set version.
        '''
        if index_json:
            for index in range(len(index_json)):
                if variant == index_json[index]['datapath']:
                    versions = index_json[index]['versions']
                    other_versions = list(filter(lambda version_obj: version_obj['file'] !=version,
                                                                                         versions))
                    index_json[index]['versions'] = other_versions


    def sort_product_sets(self, index_json):
        '''
        Sorting the Product sets from latest to oldest
        '''
        if index_json:
            for variant in index_json:
                variant['versions'] = sorted(variant['versions'],
                                            key = lambda x: Version.parse(x['file']), reverse=True)


    def add_index_json(self, index_json, appending_object):
        '''
        Adding product set version to index json file.
        '''
        if index_json:
            datapaths = list(map(lambda x: x['datapath'], index_json))
            if appending_object['datapath'] in datapaths:
                for index in range(len(index_json)):
                    if index_json[index]['datapath'] == appending_object['datapath']:
                        index_json[index]['versions'].extend(appending_object['versions'][:])
            else:
                index_json.append(appending_object)
        else:
            index_json.append(appending_object)


    def store_index(self, version: CVersion, eic_product = False):
        '''
        Stores the product sets version in index.json file.
        '''
        index_json = self.load_index_json_if_exists()
        for variant, versions in self.variants.items():
            variants = []
            if version.psv.version not in versions:
                continue
            self.delete_version_if_exists_in_index_json(index_json, version.psv.version, variant)
            version_release = version.release
            if version_release is not None and \
                                        (type(version_release) == int or version_release):
                rstate = get_drop_rstate(version.psv.drop)
                if type(version_release) == int and version_release > 0:
                    rstate += f" IP{version_release}"
                variants.append({
                    'name': version.psv.version if eic_product else rstate,
                    'file': version.psv.version,
                    'targetAudience': 'cu'
                })
                variants.append({
                    'name': version.psv.version if eic_product else f"{version.psv.version} ({rstate})",
                    'file': version.psv.version,
                    'targetAudience': 'pdu'
                })
            else:
                variants.append({
                    'name': f"{version.psv.version}",
                    'file': version.psv.version,
                    'targetAudience': 'pdu'
                })
            name, short_name = self.config.get_variant(variant)
            appending_object = {
                'name': name,
                'shortName': short_name,
                'offering': 'EIC' if eic_product else 'cENM',
                'datapath': variant,
                'versions': variants[:]
            }
            self.add_index_json(index_json, appending_object)
        self.sort_product_sets(index_json)
        with open(os.path.join(self.folder_path, 'index.json'), 'w',
                                     encoding=ENCODING_ASCII) as index_json_file:
            json.dump(index_json, index_json_file, indent=2)
