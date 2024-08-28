'''
This file holds drop content implementations.
'''
from dataclasses import dataclass
from typing import Dict, List
import logging
from .chart import Chart


log = logging.getLogger('model.drop_content')


def production_or_dev_url(urls: Dict[str, str], key: str) -> str:
    '''
    Returns the production URL if present else the development URL.
    '''
    prd_key = key + '_production_url'
    dev_key = key + '_dev_url'
    if prd_key in urls and urls[prd_key]:
        return urls[prd_key]
    log.warning('Using DEV URL for "%s"', key)
    return urls[dev_key]


@dataclass
class DropContent:
    '''
    Contains drop content information.
    '''
    charts: List[Chart]
    csar: str
    values_file: str

    @classmethod
    def parse(cls, content) -> 'DropContent':
        '''
        This method parses the content and initializes instance attributes and
        returns a drop content.
        '''
        # CI Portal does not consistently return data
        csar_data = content['csar_data']
        if isinstance(csar_data, list):
            for csar in csar_data:
                if 'lite' not in csar['csar_name']:
                    csar_data = csar
        integration_values_file_data = content['integration_values_file_data']
        if isinstance(integration_values_file_data, list):
            integration_values_file_data = integration_values_file_data[0]
        return DropContent(
            charts=[Chart(c['chart_name'], production_or_dev_url(c, 'chart'))
                                        for c in content['integration_charts_data']],
            csar=production_or_dev_url(csar_data, 'csar'),
            values_file=production_or_dev_url(integration_values_file_data, 'values_file')
        )
