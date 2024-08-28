'''
This module generates a helm template
'''
import os
import sys
import fcntl
import select
import subprocess
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import Dict, Generator, Any
import logging
import yaml
from utils.cache import cached


log = logging.getLogger('chart')


class Spinner:
    '''
    This class writes the helm template command output.
    '''
    WIDTH = 32
    THUMB = 8
    BAR = 32

    def __init__(self) -> None:
        '''
        Initializing the spinner.
        '''
        self.step = 0
        self.steps = []
        for i in range(self.WIDTH + 1):
            self.steps.append((' ' * (self.WIDTH - i) + '=' * self.THUMB + ' ' * i)
                                                [self.THUMB:self.BAR])

    def draw(self):
        '''
        This function prints the Spinner to the console.
        '''
        sys.stderr.write('[')
        sys.stderr.write(self.steps[self.step])
        sys.stderr.write(']\r')
        sys.stderr.flush()
        if self.step == self.WIDTH:
            self.step = 0
        else:
            self.step += 1


def _set_nonblock(file_descriptor):
    '''
    This function manipulates the file descriptor.
    '''
    fcntl.fcntl(file_descriptor, fcntl.F_SETFL, \
                    fcntl.fcntl(file_descriptor, fcntl.F_GETFL) | os.O_NONBLOCK)


def _execute(values, chart, file, username: str = None, password: str  = None):
    '''
    Executes the helm template command.
    '''
    helm_logger = logging.getLogger('helm')
    cmd = [
        'helm', 'template',
        '--debug',
        '--values', values,
        chart
    ]

    if username and password:
        cmd.append('--no-hooks' )
        cmd.append('--username' )
        cmd.append(username)
        cmd.append('--password' )
        cmd.append(password)


    helm_logger.debug("Running: %s",' '.join(cmd))
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as sub_process:
        _set_nonblock(sub_process.stdout)
        _set_nonblock(sub_process.stderr)

        spinner = Spinner()

        while True:
            descriptors, _, _ = select.select([sub_process.stdout, sub_process.stderr], [], [], 0.1)

            if sub_process.stdout in descriptors:
                bytes_data = sub_process.stdout.read()
                if bytes_data:
                    file.write(bytes_data)
                    helm_logger.debug("%d bytes were written",len(bytes_data))

            if sub_process.stderr in descriptors:
                bytes_data = sub_process.stderr.read()
                if bytes_data:
                    helm_logger.debug('STDERR: %s', bytes_data.decode('utf-8').strip())

            spinner.draw()

            return_code = sub_process.poll()
            if return_code is not None:
                break

        if sub_process.returncode != 0:
            raise SystemExit(1)

@cached
def template(values: Dict[str, Any], chart_url: str, username: str = None,
             password: str  = None) -> Generator[Any, None, None]:
    '''
    Perform Helm template command and returns its output.
    '''
    with BytesIO() as bio, NamedTemporaryFile('wt') as values_file:
        yaml.dump(values, values_file, Dumper=yaml.Dumper)

        _execute(values_file.name, chart_url, bio, username, password)
        bio.seek(0)

        for data in yaml.load_all(bio, Loader=yaml.Loader):
            if data is None:
                log.warning('Empty Manifest in chart: %s', chart_url)
                continue
            yield data
