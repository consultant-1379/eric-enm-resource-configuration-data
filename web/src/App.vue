<template>
<header class="sysbar">
  <div class="items-container">
    <div class="item" @click="$router.push('/')">
      <i class="icon icon-econ" />
      <span class="product" v-if="model.targetAudience == 'cu'">Cloud Native Resource Configuration Data</span>
      <span class="product" v-else>Internal Cloud Native Resource Configuration Data</span>
      <span class="acronym">cENM RCD</span>
    </div>
  </div>
</header>
<main>
  <aside class="syspanel hidden" />
  <div class="app slide-right">
    <nav class="appbar">
      <div class="actions-left">
        <div class="item">
          <i class="navigation-toggle closed" />
        </div>
        <div class="menu-anchor open-menu">Menu</div>
        <div class="title open-menu">
          <span class="title-name">{{ $route.name }}</span>
          <span class="subtitle" v-if="model.isModelReady">{{ model.selectedVariant.shortName }}:{{ model.selectedVersion.name }}</span>
        </div>
      </div>
      <div class="actions-right" />
    </nav>

    <div class="appbody">
      <div class="appnav">
        <div class="tree navigation" ref="nav">
          <ul>
            <li><router-link to="/deploymentsetup" class="item" active-class="active"><i class="icon icon-options"></i>Deployment Setup</router-link></li>
            <li>
              <router-link to="/overview" class="item" active-class="active" v-if="model.isModelReady"><i class="icon icon-dashboard"></i>Resource Overview</router-link>
              <router-link to="/" class="item link-disabled" active-class="active" v-else><i class="icon icon-dashboard"></i>Resource Overview</router-link>
            </li>
            <li>
              <span class="title opened item">Resource Details</span>
              <ul>
                <li>
                  <router-link to="/applications" class="item" active-class="active" v-if="model.isModelReady && model.selectedOffering.name === 'EIC'"><i class="icon icon-dashboard"></i>Applications</router-link>
                </li>
                <li>
                  <router-link to="/workloads" class="item" active-class="active" v-if="model.isModelReady"><i class="icon icon-cpu"></i>Workloads</router-link>
                  <router-link to="/" class="item link-disabled" active-class="active" v-else><i class="icon icon-dashboard"></i>Workloads</router-link>
                </li>
                <li>
                  <router-link to="/storage" class="item" active-class="active" v-if="model.isModelReady"><i class="icon icon-database"></i>Storage</router-link>
                  <router-link to="/" class="item link-disabled" active-class="active" v-else><i class="icon icon-dashboard"></i>Storage</router-link>
                </li>
                <li>
                  <router-link to="/images" class="item" active-class="active" v-if="model.isModelReady"><i class="icon icon-layers"></i>Images</router-link>
                  <router-link to="/" class="item link-disabled" active-class="active" v-else><i class="icon icon-dashboard"></i>Images</router-link>
                </li>
              </ul>
            </li>
            <li v-if="model.targetAudience == 'pdu'">
                  <router-link to="/workloadconfigvalid" class="item" active-class="active" v-if="model.isModelReady"><i class="icon icon-server"></i>Workload Validator</router-link>
                  <router-link to="/" class="item link-disabled" active-class="active" v-else><i class="icon icon-dashboard"></i>Workload Validator</router-link>
            </li>
            <li v-if="model.targetAudience == 'pdu' && model.selectedOffering.name === 'cENM'">
              <router-link to="/nodecalc" class="item" active-class="active" v-if="model.isModelReady"><i class="icon icon-server"></i>Node Calculator</router-link>
              <router-link to="/" class="item link-disabled" active-class="active" v-else><i class="icon icon-dashboard"></i>Node Calculator</router-link>
            </li>
            <li>
              <router-link to="/compare" class="item" active-class="active" v-if="model.isModelReady && model.selectedOffering.name === 'cENM'"><i class="icon icon-options"></i>Compare Releases</router-link>
            </li>
          </ul>
          <div class="appversion" @click="showVersionModal = true" v-if="model.targetAudience == 'pdu'">v{{versionHistory.currentVersion}}</div>
        </div>
      </div>

      <div class="appcontent">
        <router-view></router-view>
      </div>
    </div>
  </div>
</main>


<transition name="dialog">
  <div class="dialog" v-if="showVersionModal" @click.self="showVersionModal = false">
    <div class="content">
      <div class="top">
        <div class="title">Version history</div>
        <div class="right"><i class="icon icon-cross" @click="showVersionModal = false"></i></div>
      </div>
      <div class="body">
        <div class="timeline">
          <ul class="main-list">
            <li class="entry" v-for="v in versionHistory.history">
              <div class="target">
                <h4 class="title">v{{v.version}}</h4>
                <div class="content">
                  <p v-for="c in v.changes">{{c}}</p>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</transition>

</template>

<script>
import { Layout } from "@eds/vanilla/common/scripts/Layout";
import { Tree } from "@eds/vanilla/tree/Tree";
import model from "./model";
import { resetDeploymentSetup } from "./model";
import versionHistory from "./model/versionHistory";

export default {
  name: 'app',
  data: ()=>({
    model,
    versionHistory,
    showVersionModal: false,
    resetDeploymentSetup
  }),
  mounted(){
    const layout = new Layout(document.body);
    layout.init();
    const tree = new Tree(this.$refs.nav);
    tree.init();
  }
}
</script>

<style lang="less">
@import "global.less";
</style>

<style scoped lang="less">

.appversion {
  position: absolute;
  bottom: 0px;
  margin: 8px 16px;
  cursor: pointer;
}

.dialog > .content > .top > .right {
  font-size: 20px;
}

.light .switch input:checked + .ball,
.light .sysbar .switch input:checked + .ball,
.light .syspanel .switch input:checked + .ball
{
  background-color: #181818 !important;
  border: solid 1px #767676 !important;
}

.link-disabled {
  opacity: 0.5;
  pointer-events: none;
}

</style>

<style>
.tooltip {
  position: relative;
  display: inline-block;
}
.tooltip .tooltiptext {
  visibility: hidden;
  width: 120px;
  background-color: black;
  color: #fff;
  text-align: center;
  padding: 5px 0;
  position: absolute;
  z-index: 1;
  top: -5px;
  left: 110%;
}
.tooltip .tooltiptext::after {
  content: "";
  position: absolute;
  top: 15%;
  right: 100%;
  margin-top: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: transparent black transparent transparent;
}
.tooltip:hover .tooltiptext {
  visibility: visible;
}
</style>