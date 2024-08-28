'''
This file is the complete implementation of Version and version comparisions.
'''
from dataclasses import dataclass
import logging
from typing import Tuple
from datasrc.ciportal import get_latest_green_product_set_version

log = logging.getLogger('model.version')


@dataclass
class Version:
    '''
    This class stores the version information.
    '''
    drop: str
    version: str
    raw: Tuple[int, int, int, int]

    @classmethod
    def parse(cls, drop_or_version: str) -> 'Version':
        '''
        Parses a version string to Version object.
        '''
        dov = drop_or_version.split('.')
        if len(dov) == 2:
            drop = '.'.join(dov)
            version = get_latest_green_product_set_version(drop)
        elif len(dov) == 3:
            drop = '.'.join(dov[:2])
            version = '.'.join(dov)
        else:
            log.error('Bad Drop format. (Must be X.Y or X.Y.Z or X.Y.Z-V)')
            raise SystemExit(1)
        major, minor, build = version.split('.')
        rev = 0
        build_rev = build.split('-')
        if len(build_rev) > 1:
            build = build_rev[0]
            rev = build_rev[1]
        return cls(
            drop,
            version,
            (int(major), int(minor), int(build), int(rev))
        )

    @staticmethod
    def compare(version1: Tuple[int, int, int, int], version2: Tuple[int, int, int, int]) -> int:
        '''
        Compares two Version objecs and returns the difference.
        '''
        for i in range(4):
            version_difference = version1[i] - version2[i]
            if version_difference != 0:
                return version_difference
        return 0

    def __lt__(self, version):
        '''
        Implementation of less than method.
        '''
        return Version.compare(self.raw, version.raw) < 0

    def __gt__(self, version):
        '''
        Implementation of greater than method.
        '''
        return Version.compare(self.raw, version.raw) > 0

    def __eq__(self, version):
        '''
        Implementation of equal method.
        '''
        return Version.compare(self.raw, version.raw) == 0

    def __le__(self, version):
        '''
        Implementation of less than or equal method.
        '''
        return Version.compare(self.raw, version.raw) <= 0

    def __ge__(self, version):
        '''
        Implementation of greater than or equal method.
        '''
        return Version.compare(self.raw, version.raw) >= 0

    def __ne__(self, version):
        '''
        Implementation of not equal method.
        '''
        return Version.compare(self.raw, version.raw) != 0
