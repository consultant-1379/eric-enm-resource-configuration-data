'''
This implements a pickle serialization based cache / memoization functionality.
Each result is identified by (the md5 sum of) the name of the called function
and all the arguments converted to strings.
'''
from hashlib import md5
import sys
from os import path, makedirs
import pickle
from types import GeneratorType
from itertools import chain
import logging

log = logging.getLogger('cache')

# This implements a pickle serialization based cache / memoization functionality.
# Each result is identified by (the md5 sum of) the name of the called function
# and all the arguments converted to strings.
CACHE_DIR = '/var/tmp/rcd-cache'
_cache_dir = path.abspath(CACHE_DIR)

# Creates cache folder
def init_cache():
    '''
    Creates cache directory
    '''
    if not path.isdir(_cache_dir):
        if path.exists(_cache_dir):
            print('Cannot create cache directory', file=sys.stderr)
            raise SystemExit(1)
        makedirs(_cache_dir)

init_cache()

# Global flag to disable caching
IGNORE_CACHE = False

# @cached decorator
def cached(func):
    '''
    This is the implementation of cached dectorator.
    '''
    # Iteratively dumps a generator and proxies it
    def gen_dump(contents, file):
        '''
        Iteratively dumps a content into file.
        '''
        for content in contents:
            pickle.dump(content, file)
            yield content
        file.close()

    # Iteratively loads a result and outputs as a generator
    def gen_load(content, file):
        '''
        Iteratively loads a result and outputs as a generator
        '''
        yield content
        while True:
            try:
                pickle_data = pickle.load(file)
                yield pickle_data
            except EOFError:
                break
        file.close()

    def wrapper(*args, **kwargs):
        '''
        Implementation of the wrapper to read from and write to the cache.
        '''
        md5_hash = md5()
        md5_hash.update(' '.join(chain((func.__name__,),
                             (str(a) for a in args),
                             (str(a) for a in kwargs.values()))).encode('utf-8'))
        fname = path.join(CACHE_DIR, md5_hash.hexdigest())

        # Check if result can be retrieved from cache or it must be calculated
        if IGNORE_CACHE or not path.isfile(fname):  # It must be calculated
            res = func(*args, **kwargs)
            file = open(fname, 'wb+')
            if isinstance(res, GeneratorType):
                return gen_dump(res, file)
            pickle.dump(res, file)
            file.close()
            return res
        log.debug('Loading file from cache: %s', fname)
        file = open(fname, 'rb')
        res = pickle.load(file)
        if file.peek():
            return gen_load(res, file)
        file.close()
        return res

    return wrapper
