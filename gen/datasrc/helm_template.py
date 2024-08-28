# pylint: disable=too-few-public-methods
"""
This module contains the HelmTemplate class which models the templates
generated using the chart and site values.
"""

import logging
import subprocess
from functools import lru_cache
import yaml
import rcd_exceptions
from utils import utils

LOG = logging.getLogger(__name__)


class HelmTemplate:
    """This class contains methods for retrieving information from a given helm chart."""

    def __init__(self, manifest_file):
        """The constructor."""
        self.manifest_file = manifest_file

    @lru_cache(maxsize=None)
    def get_helm_templates_from_chart(self):
        """Get all helm templates from the helm chart."""
        helm_template_process = utils.run_cli_command(
            ['cat', self.manifest_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False)

        if helm_template_process.returncode != 0:
            raise rcd_exceptions.HelmTemplateFailedError(helm_template_process.stdout.decode('utf-8').rstrip())
        return list(yaml.load_all(helm_template_process.stdout.decode('utf-8'),
                                  Loader=yaml.SafeLoader))
