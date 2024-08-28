'''
This file has functions to format the EIC CRD templates (such as Cassandra).
'''
from utils.utils import check_path_in_dict

def generate_pvc_manifest(name, size):
    '''
    Generate pvc manifest information
    '''
    return {
        "kind": "PersistentVolumeClaim",
        'metadata': {'name': name},
        "spec": {
            "accessModes": ["ReadWriteOnce"],
            "resources": {
                "requests": {
                    "storage": size
                }
            }
        }
    }

def get_containers_for_cassandra(template):
    '''
    Get container information from cassandra cluster
    '''
    containers_template_list = []
    cassandra_containers = {}
    cassandra_container_name = 'cassandra'
    backup_restore_container_name = 'brsc'
    backup_restore_container_path_segments = ['backupAndRestore', backup_restore_container_name]
    image_path_segments = ['imageDetails', 'image']

    if cassandra_container_name in template:
        cassandra_containers[cassandra_container_name] = template[cassandra_container_name]

    if check_path_in_dict(template, backup_restore_container_path_segments):
        cassandra_containers[backup_restore_container_name] = \
            template['backupAndRestore'][backup_restore_container_name]

    for container_name, container_template in cassandra_containers.items():
        if check_path_in_dict(container_template, image_path_segments) and \
            'resourceRequirements' in container_template:
            container_template['name'] = f"{template['name']}-{container_name}"
            container_template['image'] = container_template['imageDetails']['image']
            containers_template_list.append(container_template)

    return containers_template_list

def get_pvcs_for_cassandra(template):
    '''
    Get pvcs information from cassandra cluster
    '''
    pvc_path_segments = ['persistence', 'dataVolume', 'persistentVolumeClaim']
    if check_path_in_dict(template, pvc_path_segments):
        volume_name =  f"{template['name']}"
        volume_size = template['persistence']['dataVolume']['persistentVolumeClaim']['size']
        return [generate_pvc_manifest(volume_name, volume_size)]
    return []
