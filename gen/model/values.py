'''
This class holds Values.
'''
from dataclasses import dataclass
from typing import Any, Callable, Dict
import yaml


@dataclass
class Values:
    '''
    Contains name and values.
    '''
    name: str
    values: Dict[str, Any]

    def prepare(self, callback: Callable[[Dict[str, Any]], None]):
        '''
        Prepare the callback method with values.
        '''
        # print(self.values)
        callback(self.values)

    @classmethod
    def parse(cls, name, yamlbytes: bytes) -> 'Values':
        '''
        Initializes the class object and return it.
        '''
        return cls(
            name,
            yaml.load(yamlbytes, yaml.Loader)
        )
