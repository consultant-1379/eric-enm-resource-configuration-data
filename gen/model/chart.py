'''
This file contains Chart information.
'''
from dataclasses import dataclass
import re
import logging


log = logging.getLogger('model.chart')


@dataclass
class Chart:
    '''
    This class holds thar chart information.
    '''
    name: str
    url: str

    @property
    def alias(self) -> str:
        '''
        This method returns the alias name of chart.
        '''
        patch_mattern_object = re.match(r'^eric-enm-(.+)-integration$', self.name)
        if patch_mattern_object is None:
            return self.name
        return patch_mattern_object.group(1)
