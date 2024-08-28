'''
This file contains definitions of Image, CSARInfo and RangeClient.
'''
from dataclasses import dataclass
from typing import List
import logging
import struct
import zlib
import requests
from utils.cache import cached
from model.values import Values
from model.chart import Chart
from requests.auth import HTTPBasicAuth


log = logging.getLogger('csar-parser')


@dataclass
class Image:
    '''
    This class has the informaiton about the image.
    '''
    prefix: str
    name: str
    tag: str
    app_enabled: bool = True

    @classmethod
    def parse(cls, line: str) -> 'Image':
        '''
        This method parses the complete image values from helm chart and initializes
        instance attributes.
        '''
        image = line.split(':')
        repo_name = image[0].split('/')
        name = repo_name.pop()
        return cls('/'.join(repo_name) + '/', name, image[1])

    @classmethod
    def parse_list(cls, lines: List[str]) -> List['Image']:
        '''
        This method gets a list of images from the lines of the images.txt file.
        '''
        return list(map(Image.parse, lines))


@dataclass
class CSARInfo:
    '''
    This class holds CSAR Information.
    '''
    images: List[Image]
    total_images_size: int
    values_files: List[Values]
    charts: List[Chart]


class RangeClient:
    '''
    This class holds the methods used for retrieval of specific parts of a CSAR.
    '''
    def __init__(self, csar_url: str, username: str = None, password: str = None) -> None:
        '''
        This method initializes csar_url, response of csar_url, total_bytes of the csar.
        '''
        self.csar_url = csar_url
        if username and password:
            response = requests.head(csar_url, auth=HTTPBasicAuth(username, password))
        else:
            response = requests.head(csar_url)

        if 'Content-Length' in response.headers:
            self.total_bytes = int(response.headers['Content-Length'])
        else:
            self.total_bytes = 0


    def get_range(self, offset: int, length: int = None,
                  username: str = None, password: str = None) -> bytes:
        '''
        Requests offset, length and returns a range of bytes of the CSAR package.
        '''
        range_from = self.total_bytes + offset if offset < 0 else offset
        range_to = self.total_bytes - 1 if length is None else range_from + length - 1
        log.debug('GET Range: %d - %d', range_from, range_to)

        if username and password:
            response = requests.get(self.csar_url, auth=HTTPBasicAuth(username, password),
                                        headers={'Range': f'bytes={range_from}-{range_to}' })
        else:
            response = requests.get(self.csar_url,
                                    headers={'Range': f'bytes={range_from}-{range_to}' })

        return response.content


def _extract_file(range_client: RangeClient, offset: int,
                  username: str = None, password: str = None) -> bytes:
    '''
    Extracts the contents of csar file from a offset.
    '''
    if username and password:
        data = range_client.get_range(offset, 30, username, password)
    else:
        data = range_client.get_range(offset, 30)

    if data[0:4] != b'\x50\x4b\x03\x04':  # Local file header signature
        raise SystemExit(2)

    if data[8:10] != b'\x08\x00':  # Compression method DEFLATE
        raise SystemExit(3)

    flen = struct.unpack('<L', data[18:22])[0]  # File length
    fnlen = struct.unpack('<H', data[26:28])[0]  # Filename length
    extralen = struct.unpack('<H', data[28:30])[0]  # Extra length
    fileoffset = 30 + fnlen + extralen  # Skip local file header
    if username and password:
        data = range_client.get_range(offset + fileoffset, flen, username, password)
    else:
        data = range_client.get_range(offset + fileoffset, flen)
    return zlib.decompress(data, -15)

@cached
def get_csar_info(csar_url, username: str = None, password: str = None) -> CSARInfo:
    '''
    This function retrieves information from a CSAR.
    '''

    ret = CSARInfo([], 0, [], [])

    # Implementation details about ZIP:
    # https://en.wikipedia.org/wiki/ZIP_(file_format)
    # All number fields ara little-endian and unsigned.
    # H: 2 Bytes, L: 4 Bytes, Q: 8 Bytes

    # Get last 1 MB of CSAR (ZIP archive)
    log.debug('Loading header of the CSAR archive')
    if not username or not password:
        range_client = RangeClient(csar_url)
        data = range_client.get_range(-1_000_000)
    else:
        range_client = RangeClient(csar_url, username, password)
        data = range_client.get_range(-1_000_000, None, username, password)

    cdfh: int = 0  # Offset of the current central directory file header
    lfoffset: int = 0  # Relative offset of local file header

    log.debug('Finding files in archive')
    while True:
        cdfh = data.find(b'\x50\x4b\x01\x02', cdfh + 1)  # Central directory file header signature
        if cdfh == -1:
            break
        fnlen = struct.unpack('<H', data[cdfh + 28: cdfh + 30])[0]  # Filename length
        file_name = data[cdfh + 46: cdfh + 46 + fnlen].decode('ascii')  # Filename

        if file_name == 'Files/images.txt':
            lfoffset = struct.unpack('<L', data[cdfh + 42: cdfh + 46])[0]
            log.debug('Extracting image list')
            if not username or not password:
                file = _extract_file(range_client, lfoffset).decode('ascii')
            else:
                file = _extract_file(range_client, lfoffset, username, password).decode('ascii')
            ret.images = Image.parse_list(file.splitlines())

        elif file_name == 'Files/images/docker.tar':
            # Filelength is bigger than 4GiB, its size must be stored in more than 4 bytes,
            #  ZIP64 extra header is used
            # extralen = struct.unpack('<H', data[cdfh + 30: cdfh + 32])[0]
            z64hoffset = cdfh + 46 + fnlen

            # For cENM
            if not username or not password:
                ret.total_images_size = struct.unpack('<Q', data[z64hoffset + 4: z64hoffset + 12])[0]
            # For EIC
            else:
                ret.total_images_size = struct.unpack('<I', data[cdfh + 24: cdfh + 28])[0]

    return ret
