"""Module for handling helmfile."""
import subprocess
import os
import io
import logging
from utils import utils
import yaml
import rcd_exceptions
from .helm_template import HelmTemplate

log = logging.getLogger(__name__)
HELM = "/eic_helm/helm"
HELMFILE = "/usr/local/bin/helmfile"
HELMFILE_BUILD_OUTPUT_FILE_NAME = "helmfile_build_output.txt"
MANIFEST_FILE_NAME = "manifest.yaml"

if not os.path.exists(HELM):
    HELM = "/usr/local/bin/helm"

def run_helmfile_command(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
    """
    Execute a helmfile command.

    Args:
        helmfile_path: File path to helmfile
        site_values_file_path: File path to site-values Yaml to use for rendering helmfile templates
        config_file_path: Optional kube config file.  Set to None if not required (default context)
        *helmfile_args: List of arguments to pass to helmfile command

    Returns
    -------
        Helmfile command object (after running command)

    """
    command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                             '--file', helmfile_path,
                             '--state-values-file', site_values_file_path]
    command_and_args_list.extend(helmfile_args)
    logging.info("Running HELMFILE command %s", ' '.join(command_and_args_list))
    env = {'KUBECONFIG': config_file_path} if config_file_path else {}
    return utils.run_cli_command(command_and_args_list,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 env=env)


def download_helmfile(chart_name, chart_version, chart_repo, username, password):
    """
    Download the project helmfile tar file given.

    Args:
        chart_name: name of the helmfile chart to download
        chart_version: version of the helmfile to download
        chart_repo: repository where the chart is stored
        username: username to access the repo
        password: password to access the repo
    """

    full_chart_name = f"{chart_name}-{chart_version}.tgz"
    full_url = f"{chart_repo}/{chart_name}/{full_chart_name}"
    logging.debug("Read the repositories file")
    utils.download_file(full_url, full_chart_name, username, password, 'wb')


def execute_helmfile_command(state_values_file,
                             path_to_helmfile,
                             helmfile_build_output_file,
                             command_name):
    """
    Execute the helmfile command.

    Args:
        state_values_file: State values file
        path_to_helmfile: Path to the helmfile to test against
        path_to_build_output: Path to the helm build output file
        command_name: name of the command (either 'build or 'template')
    """
    helmfile_build_output = run_helmfile_command(path_to_helmfile,
                                                 state_values_file,
                                                 None,
                                                 '--environment',
                                                 'build',
                                                 command_name)

    if helmfile_build_output.returncode != 0:
        logging.error(helmfile_build_output.stderr.decode('utf-8'))
        raise rcd_exceptions.HelmfileTemplateBuildError(
            "The helmfile build returned an error")

    helmfile_build_output = io.StringIO(helmfile_build_output.stdout.decode('utf-8'))

    with open(helmfile_build_output_file, "w", encoding="utf-8") as helmfile_build_file:
        helmfile_build_file.write(helmfile_build_output.getvalue())


def clean_up_file(helmfile_build_output_file):
    """
    Ensure all created files are removed if not needed.

    Args:
        helmfile_build_output_file: The HELM file build output file
    """
    if os.path.exists(helmfile_build_output_file):
        os.remove(helmfile_build_output_file)


def split_content_from_helmfile_build_file(helmfile_build_output_file):
    """
    Split content of helmfile build into two files, one for CRD and one for the main helmfile.

    Args:
        helmfile_build_output_file: The HELM file build output file
    """
    filename = ""
    output_files = {}
    with open(helmfile_build_output_file, "r", encoding="utf-8") as helmfile_build_output:
        for line in helmfile_build_output:
            if "Source" in line:
                filename = line.split('Source: ')[1].rstrip("\n").rsplit('/', 1)[-1]
                output_files[filename] = []
            elif '---' == line.strip():
                filename = None
            elif filename is not None:
                output_files[filename].append(line)

    for filename, content in output_files.items():
        output_file_path = f"compiledContent_{filename}"
        with open(output_file_path, "w", encoding="utf-8") as file_content:
            file_content.writelines(content)


def gather_release_and_repo_info(helmfile_build_file,
                                 releases_dict,
                                 csar_dict):
    """
    Read output of helmfile build and append the appropriate info into a dictionary.

    Args:
        helmfile_build_file: File that contains the helmfile build output
        releases_dict: Dictionary for gather all the associated chart details
        csar_dict: Dictionary for gathering the CSAR details
    """
    with open(helmfile_build_file, 'r', encoding="utf-8") as build_file:
        values_yaml = yaml.load(build_file, Loader=yaml.FullLoader)
    for release in values_yaml['releases']:
        name = release.get('name')
        version = release.get('version')
        chart = release.get('chart')
        namespace = release.get('namespace')
        values = release.get('values')
        installed = release.get('installed')
        condition = release.get('condition')
        labels = release.get('labels', {})

        if bool(labels):
            for key, value in labels.items():
                if key == 'csar':
                    csar_dict[name] = value

        releases_dict[name] = {
            'name': name,
            'version': version,
            'chart': chart,
            'labels': labels,
            'installed': installed,
            'condition': condition,
            'namespace': namespace,
            'values': values
        }

    # Append the repository information for the release
    for _, release_info in releases_dict.items():
        if 'repositories' in values_yaml:
            for repo in values_yaml['repositories']:
                release_chart = release_info['chart']
                repo_name = repo.get('name')
                if repo_name in release_chart:
                    repo_url = repo.get('url')
                    release_info['url'] = repo_url


def fetch_helmfile_details(state_values_file, path_to_helmfile):
    """
    Fetch helmfile details (CSAR description and releases).

    Args:
        state_values_file: State values yaml file
        path_to_helmfile: File path to helmfile to load

    Returns:
        Writes several files to describe CSAR and releases from helmfile
    """
    logging.debug('state_values_file: %s path_to_helmfile: %s', state_values_file, path_to_helmfile)
    helmfile_build_output_file_path = os.path.join(os.getcwd(), HELMFILE_BUILD_OUTPUT_FILE_NAME)
    clean_up_file(helmfile_build_output_file_path)
    execute_helmfile_command(state_values_file,
                             path_to_helmfile,
                             helmfile_build_output_file_path,
                             'build')

    split_content_from_helmfile_build_file(helmfile_build_output_file_path)
    releases_dict = {}
    csar_dict = {}

    # Iterate over all the compiledContent_* files and generate a release Dictionary that holds
    # the chart, version, repo etc. info for all the releases within the Helmfiles
    for filename in os.listdir(os.getcwd()):
        if filename.startswith("compiledContent_helmfile"):
            gather_release_and_repo_info(filename, releases_dict, csar_dict)

    return releases_dict, csar_dict


def build_manifest(state_values_file, path_to_helmfile):
    '''
    This function builds the helm manifest.

    Args:
        state_values_file: Site values yaml file
        path_to_helmfile: File path to helmfile to load

    Returns:
        The path of the manifest file built
    '''
    logging.debug('state_values_file: %s', state_values_file)
    logging.debug('path_to_helmfile: %s', path_to_helmfile)
    manifest_file_path = os.path.join(os.getcwd(), MANIFEST_FILE_NAME)
    clean_up_file(manifest_file_path)
    execute_helmfile_command(state_values_file, path_to_helmfile, manifest_file_path, 'template')

    return manifest_file_path


def get_all_templates(manifest_file):
    '''
    This function fetches all the templates in the manifest.

    Args:
        manifest_file: The Manifest file

    Returns:
        The templates in the manifest file
    '''
    helm_template_object = HelmTemplate(manifest_file)
    templates = helm_template_object.get_helm_templates_from_chart()
    return templates


def get_chart_templates(chart_name, templates):
    '''
    This function fetches the templates of the given chart.

    Args:
        chart_name: Name of the application chart
        templates: The templates

    Returns:
        The templates corresponding to the chart
    '''
    chart_templates = []
    for template in templates:
        if template is None:
            continue
        metadata = template.get('metadata', {})
        labels = metadata.get('labels', {})
        instance_label = labels.get('app.kubernetes.io/instance', None)
        if instance_label == chart_name:
            chart_templates.append(template)
    return chart_templates
