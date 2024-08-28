from api.eic_storage_requirements import set_storage_requirements
from model.summary import Summary

def test_set_storage_requirements():
    pvcs = [
        {
            "chart": "eric-cloud-native-base",
            "name": "pg-data-eric-cm-mediator-db-pg",
            "type": "RWO",
            "size": 4.0,
        },
        {
            "chart": "eric-cloud-native-base",
            "name": "backup-data-eric-ctrl-bro",
            "type": "RWO",
            "size": 15.0
        }
    ]

    total_summary = Summary()
    set_storage_requirements(total_summary, pvcs)
    assert total_summary.overview.bur['bro_pvc_storage_requirement'] == 15
    assert total_summary.overview.bur['storage_requirement_full_backups'] == 5
    assert total_summary.overview.bur['external_storage_requirement'] == 15
