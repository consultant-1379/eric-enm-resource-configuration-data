'''
This file holds variant config information.
'''
from dataclasses import dataclass
from typing import Dict, Tuple, Union
from .version import Version


@dataclass
class CVersion:
    '''
    Contains Product set version information.
    '''
    psv: Version
    release: Union[int, bool, None]
    present: bool

    @classmethod
    def parse(cls, product_set_version) -> 'CVersion':
        '''
        Parses the product set version string and returns CVersion instance.
        '''
        return cls(
            Version.parse(product_set_version['psv']),
            product_set_version.get('release'),
            False
        )


@dataclass
class Config:
    '''
    Holds variant config file information.
    '''
    output_folder: str
    variants: Dict[str, Tuple[str, str]]

    @classmethod
    def parse(cls, variant_config) -> 'Config':
        '''
        Parses the variant config and initialies instance attributes.
        '''
        return cls(
            variant_config['output_folder'],
            {
                variant['id']:(variant['name'], variant['short_name']) \
                    for variant in variant_config['variants'] if variant['offering'] == 'cENM'
            }
        )

    def get_variant(self, variant: str) -> Tuple[str, str]:
        '''
        Returns variant information.
        '''
        return self.variants.get(variant, ('', ''))
