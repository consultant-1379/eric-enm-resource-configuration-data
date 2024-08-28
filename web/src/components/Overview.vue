<template>
  <div class="row">
<!-- EIC Cluster Recommendation:-->
    <div class="tile lg-4 sm-12" v-if= "model.selectedOffering.name === 'EIC'">
      <div class="header">
        <div class="left">
          <div class="title">
            Cluster Recommendation
          </div>
        </div>
      </div>
      <div class="content">
        <div>
          <b class="tooltip" style="font-size: 16px;">CPU:
            <i class="icon icon-info"></i>
            <span class="tooltiptext">
              Calculated by adding 15% to the total CPU requests
            </span>
          </b>
          <div class="val">CPU: {{ (Math.ceil((1.15 * model.overview.requests.wl_cpu) / 1000)) }} vCPU (+ {{ ((1.15 * model.overview.requests.wlds_cpu) / 1000).toFixed(2) }} vCPU/worker)
          </div>
        </div>
        <div>
          <b class="tooltip" style="font-size: 16px;">Memory:
            <i class="icon icon-info"></i>
            <span class="tooltiptext">
              Calculated from 2/3 of the total memory limits
            </span>
          </b>
          <div class="val">Memory: {{ Math.ceil(model.overview.limits.wl_mem / (1024*1.5)).toFixed(2) }} GiB (+ {{ (model.overview.limits.wlds_mem / (1024*1.5)).toFixed(2) }} GiB/worker)
          </div>
        </div>
    </div>
  </div>

<!-- cENM Cluster Recommendation:-->
    <div class="tile lg-4 sm-12" v-if= "model.selectedOffering.name === 'cENM'">
      <div class="header">
        <div class="left">
          <div class="title">
            Cluster Recommendation
          </div>
        </div>
      </div>
      <div class="content">
        <div>
          <b class="tooltip" style="font-size: 16px;">CPU:
            <i class="icon icon-info"></i>
            <span class="tooltiptext">
              Calculated by adding 15% to the total CPU requests
            </span>
          </b>
          <div class="val">CPU: {{ (Math.ceil((1.15 * model.overview.requests.wl_cpu) / 1000)) }} vCPU (+ {{ ((1.15 * model.overview.requests.wlds_cpu) / 1000).toFixed(2) }} vCPU/worker)
          </div>
        </div>
        <div>
          <b class="tooltip" style="font-size: 16px;">Memory:
            <i class="icon icon-info"></i>
            <span class="tooltiptext">
              Calculated by adding 15% to the total memory limits
            </span>
          </b>
          <div class="val">Memory: {{ Math.ceil(1.15 * model.overview.limits.wl_mem / 1024).toFixed(2) }} GiB (+ {{ (1.15 * model.overview.limits.wlds_mem / 1024).toFixed(2) }} GiB/worker)
          </div>
        </div>
    </div>
  </div>

<!--    ENM Application Total Requirements:-->
    <div class="tile lg-4 sm-12">
      <div class="header">
        <div class="left">
          <div class="title">
            Application Total Requirements:
          </div>
        </div>
      </div>
      <div class="content">
        <div>
          <b class="tooltip">CPU:
            <i class="icon icon-info"></i>
            <span class="tooltiptext">
              Calculated by adding all CPU required by the workloads excluding jobs (plus CPU for DaemonSets).
          </span>
          </b>
          <div class="val">Requests: {{ Math.ceil(model.overview.requests.wl_cpu / 1000) }} vCPU (+ {{ (model.overview.requests.wlds_cpu / 1000).toFixed(2) }} vCPU/worker)
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.requests.wl_cpu != 0)">
              <p :style="{color: model.version_comparison_delta.requests.wl_cpu > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.requests.wl_cpu) }} vCPU</p>
            </div>
          </div>
          <div  class="val">Limits: {{ Math.ceil(model.overview.limits.wl_cpu / 1000) }} vCPU (+ {{ (model.overview.limits.wlds_cpu / 1000).toFixed(2) }} vCPU/worker)
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.requests.wl_cpu != 0)">
              <p :style="{color: model.version_comparison_delta.limits.wl_cpu > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.limits.wl_cpu) }} vCPU</p>
            </div>
          </div>
        </div>
        <div>
          <b class="tooltip">Memory:
            <i class="icon icon-info"></i>
            <span class="tooltiptext">
              Calculated by adding all memory required by the workloads excluding jobs (plus memory for DaemonSets).
            </span>
          </b>
          <div class="val">Requests: {{ Math.ceil(model.overview.requests.wl_mem / 1024) }} GiB (+ {{ (model.overview.requests.wlds_mem / 1024).toFixed(2) }} GiB/worker)
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.limits.wl_mem != 0)">
              <p :style="{color: model.version_comparison_delta.requests.wl_mem > 0 ? 'red': 'green'}">{{ checkNumber(Math.ceil(model.version_comparison_delta.requests.wl_mem / 1024)) }} GiB</p>
            </div>
          </div>
          <div class="val">Limits: {{ Math.ceil(model.overview.limits.wl_mem / 1024) }} GiB (+ {{ (model.overview.limits.wlds_mem / 1024).toFixed(2) }} GiB/worker)
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.limits.wl_mem != 0)">
              <p :style="{color: model.version_comparison_delta.limits.wl_mem > 0 ? 'red': 'green'}">{{ checkNumber(Math.ceil(model.version_comparison_delta.limits.wl_mem / 1024)) }} GiB</p>
            </div>
          </div>
        </div>
      </div>
      <div class="header" v-if="model.targetAudience == 'pdu'">
        <div class="left">
          <div class="title">
            Jobs Total Requirements:
          </div>
        </div>
      </div>
      <div class="content" v-if="model.targetAudience == 'pdu'">
        <div>
          <b class="tooltip">CPU:
            <i class="icon icon-info"></i>
            <span class="tooltiptext">
              Calculated by adding all CPU requests required by jobs in the workloads.
          </span>
          </b>
          <div class="val">{{ Math.ceil(model.overview.requests.wl_jobs_cpu / 1000) }} vCPU
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.requests.wl_jobs_cpu != 0)">
              <p :style="{color: model.version_comparison_delta.requests.wl_jobs_cpu > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.requests.wl_jobs_cpu) }} vCPU</p>
            </div>
          </div>
        </div>
        <div>
          <b class="tooltip">Memory:
            <i class="icon icon-info"></i>
            <span class="tooltiptext">
              Calculated by adding all memory limits required by jobs in the workloads.
            </span>
          </b>
          <div class="val">{{ Math.ceil(model.overview.limits.wl_jobs_mem / 1024) }} GiB
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.limits.wl_jobs_mem != 0)">
              <p :style="{color: model.version_comparison_delta.limits.wl_jobs_mem > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.limits.wl_jobs_mem) }} GiB</p>
            </div>
          </div>
        </div>
      </div>
    </div>

<!-- Storage Requirements:-->
    <div class="tile lg-4 sm-12">
      <div class="header">
        <div class="left">
          <div class="title">Storage Requirements:</div>
        </div>
      </div>
      <div class="content">
        <div>
          <b class="tooltip">RWO (ReadWriteOnce):
            <i class="icon icon-info"></i>
            <span class="tooltiptext">
              Calculated by adding all RWO Persistent Volume Claims sizes required
            </span>
          </b>
          <div class="val">
            {{ Math.ceil(model.overview.sum.rwo) }} GiB
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.sum.rwo != 0)">
              <p :style="{color: model.version_comparison_delta.sum.rwo > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.sum.rwo) }} GiB</p>
            </div>
          </div>
        </div>
        <div v-if= "model.selectedOffering.name === 'cENM'">
          <b class="tooltip">RWX (ReadWriteMany):
            <i class="icon icon-info"></i>
            <span class="tooltiptext">
              Calculated by adding all RWX Persistent Volume Claims sizes required
            </span>
          </b>
          <div class="val">
            {{ Math.ceil(model.overview.sum.rwx) }} GiB
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.sum.rwx != 0)">
              <p :style="{color: model.version_comparison_delta.sum.rwx > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.sum.rwx) }} GiB</p>
            </div>
          </div>
        </div>
          <div>
            <b class="tooltip">Ephemeral Storage:
              <i class="icon icon-info"></i>
              <span class="tooltiptext">
                Calculated by adding all ephemeral storage limits required by the workloads.
              </span>
            </b>
          <div class="val">{{ Math.ceil(model.overview.limits.wl_disk) }} GiB (+ {{ model.overview.limits.wlds_disk }} GiB/worker)
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.limits.wl_disk != 0)">
              <p :style="{color: model.version_comparison_delta.limits.wl_disk > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.limits.wl_disk) }} GiB</p>
            </div>
          </div>
        </div>
      </div>
    </div>

<!--    EIC Application Worker Node Requirements:-->
    <div class="tile lg-4 sm-12" v-if= "model.selectedOffering.name === 'EIC'">
        <div class="header">
          <div class="left">
            <div class="title">Application Worker Node Requirements:</div>
          </div>
        </div>
        <div class="content">
          <div>
            <b class="tooltip">
              Minimum number of Worker Nodes:
              <i class="icon icon-info"></i>
              <span class="tooltiptext">
                Calculated from the workload with the highest number of replicas and hard anti-affinity setting.
              </span>
            </b>
            <div class="val">{{ model.overview.min.worker_nodes }}
              <div  v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.min.worker_nodes != 0)">
                <p :style="{color: model.version_comparison_delta.min.worker_nodes > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.min.worker_nodes) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

<!--   EIC Container Registry Requirements:-->
    <div class="tile lg-4 sm-12" v-if= "model.selectedOffering.name === 'EIC'">
      <div class="header">
        <div class="left">
          <div class="title">Container Registry Requirements:</div>
        </div>
      </div>
      <div class="content">
        <div>
          <b class="tooltip">Minimum required disk storage space:
          </b>
          <div class="val">
            {{ model.overview.registry.disk_storage_space }}
            <div v-if= "model.is_to_model_ready_to_state && model.version_comparison_delta.min.worker_disk != ''">
              <p :style="{color: 'red'}">{{ checkNumber(model.version_comparison_delta.registry.disk_storage_space) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

<!-- BUR information-->
    <div class="tile lg-4 sm-12" >
      <div class="header">
        <div class="left">
          <div v-if= "model.selectedOffering.name === 'cENM'" class="title">Estimated Storage Requirements For Backups:</div>
          <div v-if= "model.selectedOffering.name === 'EIC'" class="title">Storage Requirements For Backups:</div>
        </div>
      </div>
      <div class="content" v-if= "model.selectedOffering.name === 'EIC'">
        <div>
          <b class="tooltip">BRO PVC Storage:
          </b>
          <div class="val">
            {{ model.overview.bur.bro_pvc_storage_requirement }} GiB
          </div>
        </div>
        <div>
          <b class="tooltip">External Backup Storage:
          </b>
          <div class="val">
            {{ model.overview.bur.external_storage_requirement }} GiB
          </div>
        </div>
         <div>
          <b class="tooltip">Full Backup:
          </b>
          <div class="val">
            {{ model.overview.bur.storage_requirement_full_backups }} GiB
          </div>
        </div>
      </div>
      <div class="content" v-if= "model.selectedOffering.name === 'cENM'">
        <div>
          <b class="tooltip">BRO PVC Storage:
            <i class="icon icon-info"></i>
            <span class="tooltiptext">
              Required for: <br /> {{ model.overview.bur.number_of_full_backups_on_bro_pvc }} x Full Backup and <br /> {{ model.overview.bur.number_of_rollbacks_on_bro_pvc }} x Pre-Upgrade Backup
              <br />( {{ model.overview.bur.number_of_full_backups_on_bro_pvc }} x {{ model.overview.bur.storage_requirement_full_backups_compressed }} GiB +
              {{ model.overview.bur.number_of_rollbacks_on_bro_pvc }} x {{ model.overview.bur.storage_requirement_rollbacks_compressed }} GiB )
            </span>
          </b>
          <div class="val">
            {{ model.overview.bur.bro_pvc_storage_requirement }} GiB
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.bur.bro_pvc_storage_requirement != 0)">
              <p :style="{color: model.version_comparison_delta.bur.bro_pvc_storage_requirement > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.bur.bro_pvc_storage_requirement) }} GiB</p>
            </div>
          </div>
        </div>
        <div>
          <b class="tooltip">External Backup Storage (SFTP):
            <i class="icon icon-info"></i>
            <span class="tooltiptext">
              Required for: <br /> {{ model.overview.bur.number_of_full_backups_on_external_storage }} x Full Backup
              <br />( {{ model.overview.bur.number_of_full_backups_on_external_storage }} x {{ model.overview.bur.storage_requirement_full_backups_compressed }} GiB )
            </span>
          </b>
          <div class="val">
            {{ model.overview.bur.external_storage_requirement }} GiB
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.bur.external_storage_requirement != 0)">
              <p :style="{color: model.version_comparison_delta.bur.external_storage_requirement > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.bur.external_storage_requirement) }} GiB</p>
            </div>
          </div>
        </div>
      </div>
      <div class="header" v-if= "model.selectedOffering.name === 'cENM'">
        <div class="left">
          <div class="title">Estimated Backup Sizes:</div>
        </div>
      </div>
      <div class="content" v-if= "model.selectedOffering.name === 'cENM'">
        <div>
          <b class="tooltip">Full Backup:
          </b>
          <div class="val">
            {{ model.overview.bur.storage_requirement_full_backups_compressed }} GiB ({{ model.overview.bur.storage_requirement_full_backups }} GiB Uncompressed)
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.bur.storage_requirement_full_backups != 0)">
              <p :style="{color: model.version_comparison_delta.bur.storage_requirement_full_backups > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.bur.storage_requirement_full_backups_compressed) }} GiB ({{ checkNumber(model.version_comparison_delta.bur.storage_requirement_full_backups) }} GiB Uncompressed)</p>
            </div>
          </div>
        </div>
        <div>
          <b class="tooltip">Pre-Upgrade Backup:
          </b>
          <div class="val">
            {{ model.overview.bur.storage_requirement_rollbacks_compressed }} GiB ({{ model.overview.bur.storage_requirement_rollbacks }} GiB Uncompressed)
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.bur.storage_requirement_rollbacks != 0)">
              <p :style="{color: model.version_comparison_delta.bur.storage_requirement_rollbacks > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.bur.storage_requirement_rollbacks_compressed) }} GiB ({{ checkNumber(model.version_comparison_delta.bur.storage_requirement_rollbacks) }} GiB Uncompressed)</p>
            </div>
          </div>
        </div>
      </div>
    </div>

<!--    ENM Application Worker Node Requirements:-->
    <div class="tile lg-4 sm-12" v-if= "model.selectedOffering.name === 'cENM'">
      <div class="header">
        <div class="left">
          <div class="title">Application Worker Node Requirements:</div>
        </div>
      </div>
      <div class="content">
        <div>
          <b class="tooltip">
            Minimum number of Worker Nodes:
            <i class="icon icon-info"></i>
            <span v-if="model.selectedVariant.shortName === 'Small cENM'" class="tooltiptext">
              Calculated from the workload with the highest number of replicas and hard anti-affinity setting plus 1 for node failure.
            </span>
            <span v-else class="tooltiptext">
              Calculated from the workload with the highest number of replicas and hard anti-affinity setting.
            </span>
          </b>
          <div class="val">{{ model.overview.min.worker_nodes }}
            <div  v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.min.worker_nodes != 0)">
              <p :style="{color: model.version_comparison_delta.min.worker_nodes > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.min.worker_nodes) }}</p>
            </div>
          </div>
        </div>
        <div>
          <b class="tooltip">
            Minimum required worker node CPU:
            <i class="icon icon-info"></i>
            <span class="tooltiptext">
              Calculated by adding the highest CPU limit required by a workload and the CPU limits required by  DaemonSets.
            </span>
          </b>
          <div class="val">{{ model.overview.min.worker_cpu }} vCPU
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.min.worker_cpu !=0)">
              <p :style="{color: model.version_comparison_delta.min.worker_cpu > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.min.worker_cpu) }} vCPU</p>
            </div>
          </div>
        </div>
        <div>
          <b class="tooltip">
            Minimum required worker node Memory:
            <i class="icon icon-info"></i>
            <span class="tooltiptext">
              Calculated by adding the highest memory limit required by a workload and the memory limits required by  DaemonSets.
            </span>
          </b>
          <div class="val">{{ model.overview.min.worker_mem }} GiB
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.min.worker_mem != 0)">
              <p :style="{color: model.version_comparison_delta.min.worker_mem > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.min.worker_mem) }} GiB</p>
            </div>
          </div>
        </div>
        <div>
          <b class="tooltip">
            Minimum required worker node Disk:
            <i class="icon icon-info"></i>
            <span class="tooltiptext">
              Calculated by selecting the highest ephemeral storage limit required by a workload.
            </span>
          </b>
          <div class="val">{{ model.overview.min.worker_disk }} GiB
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.min.worker_disk !=0)">
              <p :style="{color: model.version_comparison_delta.min.worker_disk > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.min.worker_disk) }} GiB</p>
            </div>
          </div>
        </div>
      </div>
    </div>

<!--    Container Registry Requirements:-->
    <div class="tile lg-4 sm-12" v-if="model.selectedOffering.name === 'cENM'">
      <div class="header">
        <div class="left">
          <div class="title">Container Registry Requirements:</div>
        </div>
      </div>
      <div class="content">
        <div>
          <b class="tooltip">Disk storage space:
          </b>
          <div class="val">
            {{ model.overview.registry.disk_storage_space }}
            <div v-if= "model.is_to_model_ready_to_state && model.version_comparison_delta.min.worker_disk != ''">
              <p :style="{color: 'red'}">{{ checkNumber(model.version_comparison_delta.registry.disk_storage_space) }}</p>
            </div>
          </div>
        </div>
        <div>
          <b class="tooltip">Ports:
            <i class="icon icon-info"></i>
            <span class="tooltiptext">
              These configurable ports must be enabled on the Registry.
            </span>
          </b>
          <div class="val">
            {{ model.overview.registry.ports }}
            <div v-if= "model.is_to_model_ready_to_state && model.version_comparison_delta.registry.ports != ''">
              <p :style="{color: 'red'}">{{ model.version_comparison_delta.registry.ports }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

<!--    Client Resource Requirements:-->
    <div class="tile lg-4 sm-12">
      <div class="header">
        <div class="left">
          <div class="title">Client Resource Requirements:</div>
        </div>
      </div>
      <div class="content">
        <div v-if= "model.overview.client.ports != 'not_set'">
          <b class="tooltip">Ports:
            <i class="icon icon-info"></i>
            <span class="tooltiptext">
              To configure port-forwarding for BRO service
            </span>
          </b>
          <div class="val">
            {{ model.overview.client.ports }}
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.client.ports != '')">
              <p :style="{color: 'red'}">{{ model.version_comparison_delta.client.ports }}</p>
            </div>
          </div>
        </div>
        <div>
          <b class="tooltip">CPU:
          </b>
          <div class="val">
            {{ model.overview.client.cpu }}
            <div v-if= "model.is_to_model_ready_to_state && model.version_comparison_delta.client.cpu != ''">
              <p :style="{color: 'red'}">{{ model.version_comparison_delta.client.cpu }}</p>
            </div>
          </div>
        </div>
        <div>
          <b class="tooltip">Memory:
          </b>
          <div class="val">
            {{ model.overview.client.memory }}
            <div v-if= "model.is_to_model_ready_to_state && model.version_comparison_delta.client.memory != ''">
              <p :style="{color: 'red'}">{{ model.version_comparison_delta.client.memory }}</p>
            </div>
          </div>
        </div>
        <div>
          <b class="tooltip">Storage:
          </b>
          <div class="val">
            {{ model.overview.client.disk }}
            <div v-if= "model.is_to_model_ready_to_state && model.version_comparison_delta.client.disk != ''">
              <p :style="{color: 'red'}">{{ model.version_comparison_delta.client.disk }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

<!--   Software Requirements:-->
    <div class="tile lg-4 sm-12" v-if= "model.overview.client.docker != 'not_set'">
      <div class="header">
        <div class="left">
          <div class="title">Software Requirements:</div>
        </div>
      </div>
      <div class="content">
        <div>
          <b class="tooltip">Client:
          </b>
          <div class="val" >Docker version: {{ model.overview.client.docker }}
            <div v-if= "model.is_to_model_ready_to_state && model.version_comparison_delta.client.docker != ''">
              <p :style="{color: 'red'}">{{ model.version_comparison_delta.client.docker }}</p>
            </div>
          </div>
          <div class="val" >Helm version: {{ model.overview.client.helm }}
            <div v-if= "model.is_to_model_ready_to_state && model.version_comparison_delta.client.helm != ''">
              <p :style="{color: 'red'}">{{ model.version_comparison_delta.client.helm }}</p>
            </div>
          </div>
          <div class="val" >Kubectl version: {{ model.overview.client.kubectl }}
            <div v-if= "model.is_to_model_ready_to_state && model.version_comparison_delta.client.kubectl != ''">
              <p :style="{color: 'red'}">{{ model.version_comparison_delta.client.kubectl }}</p>
            </div>
          </div>
          <div class="val" >Python version: {{ model.overview.client.python }}
            <div v-if= "model.is_to_model_ready_to_state && model.version_comparison_delta.client.python  != ''">
              <p :style="{color: 'red'}">{{ model.version_comparison_delta.client.python }}</p>
            </div>
          </div>
          <div class="val" >Screen</div>
          <div class="val" >Unzip</div>
        </div>
        <div>
          <b class="tooltip">Cluster:
          </b>
          <div class="val">Kubernetes version: {{ model.overview.cluster.kubernetes }}
            <div v-if= "model.is_to_model_ready_to_state && model.version_comparison_delta.cluster.kubernetes != ''">
              <p :style="{color: 'red'}">{{ model.version_comparison_delta.cluster.kubernetes }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>


<!-- IP Address + Other Requirements:-->
    <div class="tile lg-4 sm-12" v-if="model.display_other_requirements_section">
      <div class="header">
        <div class="left">
          <div class="title">Networking Requirements:</div>
        </div>
      </div>
      <div class="content">
        <div>
          <b class="tooltip">IP Address Requirements:
          </b>
          <div class="val" v-if="model.selected_ip_version.alias != 'ipv6'" >Site Specific IPv4 Addresses: {{ model.overview.other_requirements.ips }}
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.other_requirements && model.version_comparison_delta.other_requirements.ips != 0)">
              <p :style="{color: model.version_comparison_delta.other_requirements.ips > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.other_requirements.ips) }}</p>
            </div>
          </div>
          <div class="val" v-if="model.selected_ip_version.alias != 'ipv4' && model.selected_ip_version.alias != 'default'" >Site Specific IPv6 Addresses: {{ model.overview.other_requirements.ipv6s }}
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.other_requirements && model.version_comparison_delta.other_requirements.ipv6s != 0)">
              <p :style="{color: model.version_comparison_delta.other_requirements.ipv6s > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.other_requirements.ipv6s) }}</p>
            </div>
          </div>
        </div>
      </div>
      <div class="header">
        <div class="left">
          <div class="title">Other Requirements:</div>
        </div>
      </div>
      <div class="content">
        <div>
          <b class="tooltip">Minimum PIDs:
            <i class="icon icon-info"></i>
            <span class="tooltiptext" v-if= "model.overview.other_requirements">
              The PID limit setting for kubelet should be equal to or greater than {{ model.overview.other_requirements.pids }} for cENM.
            </span>
          </b>
          <div class="val">
            <p v-if= "model.overview.other_requirements">{{ model.overview.other_requirements.pids }}</p>
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.other_requirements && model.version_comparison_delta.other_requirements.pids != '')">
              <p :style="{color: model.version_comparison_delta.other_requirements.pids > 0 ? 'red': 'green'}">{{ model.version_comparison_delta.other_requirements.pids }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

<!--    ENM k8s Resources Overview:-->
    <div class="tile lg-4 sm-12">
      <div class="header">
        <div class="left">
          <div class="title">K8s Resources Overview:</div>
        </div>
      </div>
      <div class="content">
        <div>
          <div class="val">Total Pods: {{ model.overview.total.pods }}
            <b class="tooltip" v-if= "model.selectedOffering.name === 'EIC'">
              <i class="icon icon-info"></i>
              <span class="tooltiptext">
              Transient pods due to LCM operations (for example helm hooks) are not considered here.
              </span>
            </b>
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.total.pods != 0)">
              <p :style="{color: model.version_comparison_delta.total.pods > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.total.pods) }}</p>
            </div>
          </div>
        </div>
        <div>
          <div class="val">Total ConfigMaps: {{ model.overview.total.config_maps }}
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.total.config_maps != 0)">
              <p :style="{color: model.version_comparison_delta.total.config_maps > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.total.config_maps) }}</p>
            </div>
          </div>
        </div>
        <div>
          <div class="val">Total Secrets: {{ model.overview.total.secrets }}
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.total.secrets != 0)">
              <p :style="{color: model.version_comparison_delta.total.secrets > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.total.secrets) }}</p>
            </div>
          </div>
        </div>
        <div>
          <div class="val">Total Services: {{ model.overview.total.services }}
            <div v-if= "model.is_to_model_ready_to_state && model.version_comparison_delta.total.services != 0">
              <p :style="{color: model.version_comparison_delta.total.services > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.total.services) }}</p>
            </div>
          </div>
        </div>
        <div>
          <div class="val">Total Ingresses: {{ model.overview.total.ingresses }}
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.total.ingresses != 0)">
              <p :style="{color: model.version_comparison_delta.total.ingresses > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.total.ingresses) }}</p>
            </div>
          </div>
        </div>
        <div>
          <div class="val">Total EricIngresses: {{ model.overview.total.eric_ingresses }}
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.total.eric_ingresses != 0)">
              <p :style="{color: model.version_comparison_delta.total.eric_ingresses > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.total.eric_ingresses) }}</p>
            </div>
          </div>
        </div>
        <div>
          <div class="val">Total RWO: {{ model.overview.total.rwo }}
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.total.rwo != 0)">
              <p :style="{color: model.version_comparison_delta.total.rwo > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.total.rwo) }}</p>
            </div>
          </div>
        </div>
        <div>
          <div class="val">Total RWX: {{ model.overview.total.rwx }}
            <div v-if= "(model.is_to_model_ready_to_state && model.version_comparison_delta.total.rwx != 0)">
              <p :style="{color: model.version_comparison_delta.total.rwx > 0 ? 'red': 'green'}">{{ checkNumber(model.version_comparison_delta.total.rwx) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import model from "../model";

export default {
  name: "overview",
  data: () => ({
    model,
  }),
  methods: {
    checkNumber(theNumber) {
      if(theNumber > 0){
        return "+" + theNumber;
      } else {
        return theNumber;
      }
    }
  }
};
</script>

<style scoped>
.content .val {
  font-size: medium;
  margin: 20px;
}
.content {
  margin-left: 20px;
}

.val.top {
  margin-top: 0%;
}

.title {
  font-size: 18px !important;
}
</style>
