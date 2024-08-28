from model.eic_custom_resources import get_containers_for_cassandra, get_pvcs_for_cassandra, generate_pvc_manifest

def test_get_containers_for_cassandra():
    template = {
        "name":"datacenter1",
        "replicas":1,
        "cassandra":{
            "imageDetails":{
                "image":"dummy_cassandra_image"
            },
            "resourceRequirements":{
                "limits":{
                    "cpu":"4",
                    "memory":"2Gi"
                },
                "requests":{
                    "cpu":"1",
                    "memory":"2Gi"
                }
            }
        },
        "backupAndRestore":{
            "brsc":{
                "imageDetails":{
                    "image":"dummy_brsc_image"
                },
                "resourceRequirements":{
                    "requests":{
                        "memory":"512Mi",
                        "cpu":"1"
                    },
                    "limits":{
                        "memory":"512Mi",
                        "cpu":"4"
                    }
                }
            }
        }
    }
    containers_template = get_containers_for_cassandra(template)
    assert len(containers_template) == 2
    if len(containers_template) == 2:
        assert containers_template[0]['name'] == 'datacenter1-cassandra'
        assert containers_template[0]['image'] == 'dummy_cassandra_image'
        assert containers_template[1]['name'] == 'datacenter1-brsc'
        assert containers_template[1]['image'] == 'dummy_brsc_image'


def test_get_pvcs_for_cassandra():
    template = {
        "name":"datacenter1",
        "replicas":1,
        "persistence": {
            "dataVolume": {
                "persistentVolumeClaim": {
                    "size": "500Mi"
                }
            }
        }
    }
    pvcs_template = get_pvcs_for_cassandra(template)
    assert len(pvcs_template) == 1
    if len(pvcs_template) == 1:
        assert pvcs_template[0]['kind'] == 'PersistentVolumeClaim'
        assert pvcs_template[0]['metadata']['name'] == 'datacenter1'

def test_generate_pvc_manifest():
    pvc_template = generate_pvc_manifest("dummy-pvc", "500Mi")
    assert pvc_template['kind'] == 'PersistentVolumeClaim'
    assert pvc_template['metadata']['name'] == 'dummy-pvc'
