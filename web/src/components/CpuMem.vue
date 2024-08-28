<template>
  <div class="row">
    <div class="tile">
      <div class="header">
        <div class="left">
          <div class="title">Workloads</div>
        </div>
      </div>
      <div class="content">
        <super-table :records="model.workloads" :fields="wlFields" :expandable="true">
          <template v-slot:top-right>
            <button class="btn" @click="model.workloads.forEach(wl=>{wl.expanded=true})">Expand All</button>
            <button class="btn" @click="model.workloads.forEach(wl=>{wl.expanded=false})">Collapse All</button>
            <button v-if="model.targetAudience == 'pdu'" class="btn primary" v-on:click="exportExcel()">Export to Excel</button>
          </template>
          <template v-slot:expand="sprops">
            <div class="exp">
              <div class="f">
                <div>Affinity Rule</div>
                {{sprops.r.affinity || '&nbsp;'}}
              </div>
              <div class="f">
                <div>Update Strategy</div>
                {{sprops.r.update_strategy || '&nbsp;'}}
              </div>
              <div class="f">
                <div>Pod Disruption Budget</div>
                {{sprops.r.pdb || '&nbsp;'}}
              </div>
              <table class="table compact">
                <thead>
                  <tr>
                    <th>Container Name</th>
                    <th>Image</th>
                    <th class="right">CPU Requests</th>
                    <th class="right">CPU Limits</th>
                    <th class="right">Memory Requests</th>
                    <th class="right">Memory Limits</th>
                  </tr>
                </thead>
                <tbody>
                  <tr class="cntr" v-for="c in sprops.r.containers">
                    <td>{{ c.name }}</td>
                    <td>{{ c.image }}</td>
                    <td class="right">{{ c.cpu_req }} m</td>
                    <td class="right">{{ c.cpu_lim }} m</td>
                    <td class="right">{{ c.mem_req }} MiB</td>
                    <td class="right">{{ c.mem_lim }} MiB</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>
        </super-table>
      </div>
    </div>
  </div>
  <transition name="dialog">
    <div class="dialog" v-if="model.export_failed_404" @click.self="model.export_failed_404 = false">
      <div class="content">
        <div class="top">
          <div class="title">Export Excel File Failed</div>
        </div>
        <div class="body">
          <i class="icon icon-failed"></i>
          <span class="message right">
            Export is not available for this version.
            Please select a version 22.07.40 or newer.
          </span>
        </div>
        <div>
          <button class="btn" v-on:click="model.export_failed_404 = false">Ok</button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import model from "../model";
import {wl as wlFields} from "../model/fields";
import { exportExcel } from "../model";
import SuperTable from "./SuperTable.vue";

export default {
  name: "cpumem",
  components: {SuperTable},
  data: () => ({
    model,
    wlFields,
    exportExcel
  })
};
</script>

<style scoped lang="less">
.light .table tr td {
  border-bottom: none;
}

.exp {
  padding-bottom: 32px;
  .f {
    margin-left: 16px;
    margin-bottom: 16px;
    div {
      margin-left: -16px;
      margin-bottom: 4px;
      font-size: 12px;
      font-weight: 700;
    }
  }
  table {
    th {
      font-size: 12px;
      font-weight: 700;
    }
    td {
      // border-bottom: none;
    }
  }
}
</style>
