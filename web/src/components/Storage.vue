<template>
  <div class="row">
    <div class="tile">
      <div class="header">
        <div class="left">
          <div class="title">Persistent Volume Claims</div>
        </div>
      </div>
      <div class="content">
        <super-table :records="model.pvcs" :fields="pvcFields">
          <template v-slot:top-right>
            <button v-if="model.targetAudience == 'pdu'" class="btn primary" v-on:click="exportExcel()">Export to Excel</button>
          </template>
        </super-table>
      </div>
    </div>
  </div>

  <div class="row">
    <div class="tile">
      <div class="header">
        <div class="left">
          <div class="title">Ephemeral Storage</div>
        </div>
      </div>
      <div class="content">
        <table class="table compact">
          <thead>
            <tr>
              <th>Name</th>
              <th>Chart</th>
              <th class="right">Replicas</th>
              <th class="right">Requests</th>
              <th class="right">Limits</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="wl in wleps">
              <td>{{ wl.name }}</td>
              <td>{{ wl.chart }}</td>
              <td class="right">{{ wl.replicas }}</td>
              <td class="right">{{ wl.eps_req * 1024 }} MiB</td>
              <td class="right">{{ wl.eps_lim * 1024 }} MiB</td>
            </tr>
          </tbody>
        </table>
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
import { exportExcel } from "../model";
import {pvc as pvcFields} from "../model/fields";

import SuperTable from "./SuperTable.vue";

export default {
  name: "storage",
  components: {SuperTable},
  data: () => ({
    model,
    pvcFields,
    exportExcel }),
  computed: {
    wleps(){
      return this.model.workloads.filter(wl=>(wl.app_enabled && (wl.eps_req || wl.eps_lim)));
    }
  }
};
</script>
