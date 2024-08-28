'''
This file deals with calculating the storage_requirements for EIC.
'''

import math

def set_storage_requirements(tot_sum, pvcs):
    '''
    set BRO PVC storage requirement from PVCs
    '''
    bro_pvc =  [pvc for pvc in pvcs if 'name' in pvc and pvc['name'] == 'backup-data-eric-ctrl-bro']
    if len(bro_pvc) > 0:
        tot_sum.overview.bur['bro_pvc_storage_requirement'] = math.ceil(bro_pvc[0]['size'])
    tot_sum.overview.bur['storage_requirement_full_backups'] = 5
    tot_sum.overview.bur['external_storage_requirement'] =  tot_sum.overview.bur[
        'storage_requirement_full_backups'] * 3
