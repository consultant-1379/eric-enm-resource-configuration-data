'''
This file contains methods for accessing data from CI portal.
'''
from typing import Any, Dict
import logging
import requests
from utils.cache import cached

log = logging.getLogger('ci-portal-api')


CI_API_BASE = 'https://ci-portal.seli.wh.rnd.internal.ericsson.com'


def get_latest_green_product_set_version(drop: str) -> str:
    '''
    The method retrieves latest green product set version for a particular drop.
    '''
    response = requests.get(f"{CI_API_BASE}/api/cloudNative/getGreenProductSetVersion/{drop}/")
    return response.text


@cached
def get_drop_content(drop: str, product_set_version: str) -> Dict[str, Any]:
    '''
    Fetches the product set content from CI portal api.
    '''
    get_cloud_ps_endpoint = '/api/cloudnative/getCloudNativeProductSetContent/'
    response = requests.get(f"{CI_API_BASE}{get_cloud_ps_endpoint}{drop}/{product_set_version}/")
    content = response.json()

    # Normalize response for the sake of more convenient access
    return {list(e.keys())[0]: list(e.values())[0] for e in content}


@cached
def get_drop_rstate(drop: str):
    '''
    Fetches the R-state value for a given drop number.
    '''
    response = requests.get(f"{CI_API_BASE}/getAOMRstate/", params={'product': 'ENM', 'drop': drop})
    return response.text.split()[-1]
