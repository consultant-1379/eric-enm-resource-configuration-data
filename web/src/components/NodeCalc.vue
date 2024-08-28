<template>
  <div class="row">
    <div class="tile sm-12">
      <div class="header">
        <div class="left">
          <div class="title">Hardware Resource Sizing</div>
        </div>
      </div>
      <div class="content">
        <div class="row">
          <div class="column lg-6 sm-12">
            <num-input v-model="model.calc.cpu" :min="model.overview.min.worker_cpu" :label="resources.cpu.name" :unit="resources.cpu.unit"></num-input>
            <num-input v-model="model.calc.mem" :min="model.overview.min.worker_mem" :label="resources.mem.name" :unit="resources.mem.unit"></num-input>
            <num-input v-model="model.calc.disk" :min="model.overview.min.worker_disk" :label="resources.disk.name" :unit="resources.disk.unit"></num-input>
            <num-input v-model="model.calc.node_count" :min="1" label="Worker Nodes"></num-input>
            <button class="btn" @click="model.calc.node_count = optimal_node_count + 1">Set Optimal Node Count</button>
          </div>
          <div class="column lg-6 sm-12 pbars">
            <res-checker :res="resources.cpu" target="requests"></res-checker>
            <res-checker :res="resources.mem" target="limits"></res-checker>
            <res-checker :res="resources.disk" target="limits"></res-checker>
            <!-- <req-lim-bar :res="resources.cpu"></req-lim-bar> -->
            <!-- <req-lim-bar :res="resources.mem"></req-lim-bar> -->
            <!-- <req-lim-bar :res="resources.disk"></req-lim-bar> -->
            <!-- <div class="notes">
              However Kubernetes scheduler uses only "reqests" values, not considering "limits" here in this calculator would make pods unable to reach their "limits".
              It is highly recommended to have a cluster where no pods are limited in resources.
              Therefore, this tool calculates the required worker node count by "limits" values.
            </div> -->
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="row">
    <div class="tile sm-12">
      <div class="header">
        <div class="left">
          <div class="title">Simulated ENM Deployment</div>
        </div>
        <div class="right">
          <span class="ds"></span>DaemonSet Pod
          <span class="wl"></span>Regular Pod
        </div>
      </div>
      <div class="content">
        <div class="msg error" :style="{display: unschedulable.length > 0 ? '' : 'none'}">
          <i class="icon icon-triangle-warning"></i>
          Cannot schedule {{ unschedulable.length }} pods
        </div>
        <div class="msg" :style="{display: unschedulable.length > 0 ? 'none' : ''}">
          <i class="icon icon-heart"></i>
          This cluster is {{ Math.max(0, model.calc.node_count - optimal_node_count) }} node failure tolerant
        </div>
        <div class="visual" :style="{display: unschedulable.length > 0 ? '' : 'none'}">
          <div class="node unschedulable">
            <div class="node-inner">
              <div class="name">
                Unschedulable
              </div>
              <div class="resname">CPU</div>
              <div class="wls">
                <div
                  v-for="(wl) in unschedulable"
                  :class="['tooltip', 'wl', wl.highlight ? 'highlight' : '']"
                  :style="{width: (100 / 1000 / 8) * wl.cpu_req / model.calc.cpu + '%'}"
                  @mouseenter="wl.highlight = true"
                  @mouseleave="wl.highlight = false"
                  @click="navToWL(wl)"
                >
                  <span class="message">
                    {{ wl.name }}
                    <br>
                    {{ wl.cpu_req / 1000 }} CPU
                  </span>
                </div>
              </div>
              <div class="resname">Memory</div>
              <div class="wls">
                <div
                  v-for="(wl) in unschedulable"
                  :class="['tooltip', 'wl', wl.highlight ? 'highlight' : '']"
                  :style="{width: (100 / 1024 / 8) * wl.mem_req / model.calc.mem + '%'}"
                  @mouseenter="wl.highlight = true"
                  @mouseleave="wl.highlight = false"
                  @click="navToWL(wl)"
                >
                  <span class="message">
                    {{ wl.name }}
                    <br>
                    {{ (wl.mem_req / 1024).toFixed(2) }} GiB
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="visual">
          <div v-for="i in 3" class="node">
            <div class="node-inner">
              <div class="name">Master {{ i }}</div>
              <div class="wls">
              </div>
            </div>
          </div>
        </div>
        <div class="visual">
          <div v-for="node in nodes" class="node">
            <div class="node-inner">
              <div class="name">
                Worker {{ node.id }}
                <!-- <br>
                ({{node.remaining}}) -->
              </div>
              <div class="resname">CPU</div>
              <div class="wls">
                <div
                  v-for="(wl) in node.pods"
                  :class="['tooltip', wl.replicas == 'NC' ? 'ds' : 'wl', wl.highlight ? 'highlight' : '']"
                  :style="{width: 100 * wl.cpu_req / 1000 / model.calc.cpu + '%'}"
                  @mouseenter="wl.highlight = true"
                  @mouseleave="wl.highlight = false"
                  @click="navToWL(wl)"
                >
                  <span class="message">
                    {{ wl.name }}
                    <br>
                    {{ wl.cpu_req / 1000 }} CPU
                  </span>
                </div>
              </div>
              <div class="resname">Memory</div>
              <div class="wls">
                <div
                  v-for="(wl) in node.pods"
                  :class="['tooltip', wl.replicas == 'NC' ? 'ds' : 'wl', wl.highlight ? 'highlight' : '']"
                  :style="{width: 100 * wl.mem_req / 1024 / model.calc.mem + '%'}"
                  @mouseenter="wl.highlight = true"
                  @mouseleave="wl.highlight = false"
                  @click="navToWL(wl)"
                >
                  <span class="message">
                    {{ wl.name }}
                    <br>
                    {{ (wl.mem_req / 1024).toFixed(2) }} GiB
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import model from '../model';
import { resources } from "../model/fields";
import Cluster from '../model/simulator';

import NumInput from './NumInput.vue';
import ResChecker from './ResChecker.vue';

export default {
  name: "nodecalc",
  components: {NumInput, ResChecker},
  data: ()=>({
    model,
    resources,
    unschedulable: []
  }),
  computed: {
    cluster(){
      return new Cluster({
        cpu: this.model.calc.cpu * 1000,
        mem: this.model.calc.mem * 1024,
        disk: this.model.calc.disk
      }, this.model.workloads);
    },
    nodes(){
      let { nodes, unschedulable } = this.cluster.simulate(this.model.calc.node_count);
      this.unschedulable = unschedulable;
      return nodes;
    },
    optimal_node_count(){
      let cpu_nc = Math.ceil(this.model.overview.requests.wl_cpu / (this.model.calc.cpu * 1000 - this.model.overview.requests.wlds_cpu));
      let mem_nc = Math.ceil(this.model.overview.limits.wl_mem / (this.model.calc.mem * 1024 - this.model.overview.limits.wlds_mem));
      let disk_nc = Math.ceil(this.model.overview.requests.wl_disk / (this.model.calc.disk - this.model.overview.requests.wlds_disk));
      let estimation = Math.max(cpu_nc, mem_nc, disk_nc, this.model.overview.min.worker_nodes);
      if(!isNaN(estimation) && isFinite(estimation)){
        estimation = this.cluster.calcOptimalNodeCount(estimation);
      }
      return estimation;
    }
  },
  methods: {
    navToWL(wl){
      this.$router.push('/workloads');
    }
  }
};
</script>

<style scoped lang="less">
.btn{
  margin-top: 16px;
}

.tile{
  overflow: hidden;
}

.column {
  padding: 8px;
}


@color_ds: #0fc274;
@color_wl: #0084f1;


.header .right {
  span {
    display: inline-block;
    height: 10px;
    width: 10px;
    margin: 1px 4px 1px 24px;
  }
  .ds {
    background-color: @color_ds;
  }
  .wl {
    background-color: @color_wl;
  }
}

.content .msg {
  margin: 0 16px 16px 16px;
  font-size: 16px;
  & > i {
    font-size: 20px;
    margin-right: 8px;
  }
  &.error {
    font-weight: 500;
    text-transform: uppercase;
    color: #ed0e00;
  }
}


.visual{
  display: flex;
  flex-wrap: wrap;

  .node {
    flex-basis: 100%;
    padding: 4px;
    text-align: center;
    @media only screen and (min-width: 48em){
      flex-basis: 12.5%;
    }
    &.unschedulable {
      flex-basis: 100%;
    }
  }
  .node-inner {
    background-color: #ebebeb;
    border: 1px solid #242424;
  }
  .name {
    background-color: #0c0c0c;
    color: #fff;
    padding: 8px 0;
    font-size: 15px;
  }
  .resname{
    text-align: left;
    font-size: 12px;
    padding: 2px 2px 0 2px;
  }
  .wls {
    min-height: 24px;
    display: flex;
    // flex-wrap: wrap;
    align-content: flex-start;
    padding: 2px;
    & > div {
      height: 20px;
      /* margin: 1px; */
      border: 1px solid #ebebeb;
      min-width: 4px;
      transition: 200ms width;
      cursor: pointer;

      &.highlight {
        background-color: #fad22d;
      }
    }
    .ds {
      background-color: @color_ds;
    }
    .wl {
      background-color: @color_wl;
    }
  }
  .tooltip .message{
    margin-top: 10px;
  }
}

.notes{
  margin-top: 64px;
}

</style>
