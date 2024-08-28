<template>
  <div class="row">
    <div class="tile">
      <div class="content">
        <p>This tool details the Resource Requirements to deploy Cloud Native ENM & EIC.
           It is imperative for the user of this tool to use the correct setup specific to their deployment.</p>
          <div class="dropdown">
            <div>
              <b class="tooltip">Product Offering:
                <i class="icon icon-info"></i>
                <span class="tooltiptext">
                  This section allows the user to select the Product Offering.
                </span>
              </b>
            </div>
            <DropDownSelect :options="model.offerings" :displaykey="'name'" @select="selectOffering($event)" :default="model.selectedOffering.name"></DropDownSelect>
          </div>
          <div class="dropdown">
            <div>
              <b class="tooltip">Deployment Size:
                <i class="icon icon-info"></i>
                <span class="tooltiptext">
                  This section allows the user to select the Deployment Size.
                </span>
              </b>
            </div>
            <DropDownSelect :options="model.filteredVariants" :displaykey="'name'" @select="selectVariant($event)" :default="model.selectedVariant.name"></DropDownSelect>
          </div>
          <div class="dropdown">
            <div>
              <b class="tooltip">Product Release Version:
                <i class="icon icon-info"></i>
                <span class="tooltiptext">
                  This section allows the user to select the Release Version.
                </span>
              </b>
            </div>
            <DropDownSelect :options="model.versions" :displaykey="'name'" @select="selectVersion($event)" :default="model.selectedVersion.name"></DropDownSelect>
          </div>
          <div class="dropdown" v-if="model.prepared && model.ip_versions.length != 0">
            <div>
              <b class="tooltip">IP Address Version:
                <i class="icon icon-info"></i>
                <span class="tooltiptext">
                  This section allows the user to select IP address type.
                </span>
              </b>
            </div>
            <DropDownSelect :options="model.ip_versions" :displaykey="'name'" @select="selectIpVersion($event)" :default="model.selected_ip_version.name"></DropDownSelect>
          </div>
          <div v-if="model.selectedOffering.name === 'EIC'">
            <div class="additional-inputs" v-if="model.eic_mandatory_apps.length > 1">
              <b class="tooltip">Mandatory applications:
                <i class="icon icon-info"></i>
                <span class="tooltiptext">
                This section lists the mandatatoy applications for information, no selection required.
                </span>
              </b>
            </div>
              <ul style="list-style-type: None">
                <li v-for="value_pack in model.eic_mandatory_apps" :key="value_pack">
                  <div class="sector">
                      <i class="ball"></i>
                      <span class="message left" data-enabled="&#8205" data-disabled="&#8205"></span>
                      {{ value_pack.name }}
                      <b class="tooltip">
                        <i class="icon icon-info"></i>
                        <span class="tooltiptext">
                          {{ value_pack.description }}
                        </span>
                      </b>
                  </div>
                 </li>
              </ul>
          </div>
          <div v-if="model.prepared">
            <div class="additional-inputs" v-if="model.optional_value_packs.length > 0" >
              <b class="tooltip">Select optional applications:
                <i class="icon icon-info"></i>
                <span class="tooltiptext">
                This section allows the user to select optional applications.
                </span>
              </b>
            </div>
            <ul style="list-style-type: None">
              <div v-for="value_pack in model.optional_value_packs" :key="value_pack">
                <OptionalApps :valuePack="value_pack" v-if="!value_pack.non_mandatory" :optionalApps="model.optional_value_packs"></OptionalApps>
              </div>
            </ul>
          </div>
          <div v-if="model.prepared">
            <div class="additional-inputs" v-if="model.optional_value_packs.length > 1" >
              <b class="tooltip" v-if="checkNonMandatoryServices()">Select non-mandatory services:
                <i class="icon icon-info"></i>
                <span class="tooltiptext">
                This section allows the user to select non-mandatory services.
                </span>
              </b>
            </div>
            <ul style="list-style-type: None">
              <li v-for="value_pack in model.optional_value_packs" :key="value_pack">
                <OptionalApps :valuePack="value_pack" v-if="value_pack.non_mandatory" :optionalApps="model.optional_value_packs"></OptionalApps>
              </li>
            </ul>
          </div>
        <div v-show="model.prepared && (model.ip_versions.length == 0 || model.selected_ip_version.name != default_select)" >
          <button class="btn primary" v-on:click="setupDeployment()">Setup Deployment</button>
        </div>
      </div>
    </div>
  </div>

<transition name="dialog">
  <div class="dialog" v-if="model.show_notification" @click.self="model.show_notification = false">
    <div class="content">
      <div class="top">
        <div class="title">Deployment Setup</div>
      </div>
      <div class="body">
        <div v-show="model.selectedVariant.name == default_select">
          <i class="icon icon-cross"></i>
          <span class="message right">
            Please select a Deployment Size and try again.
          </span>
        </div>
        <div v-show="model.selectedVersion.name == default_select">
          <i class="icon icon-cross"></i>
          <span class="message right">
            Please select an ENM Release Version and try again.
          </span>
        </div>
      </div>
      <div>
        <button class="btn" v-on:click="model.show_notification = false">Ok</button>
      </div>
    </div>
  </div>
</transition>

</template>

<script>

import model from "../model";
import { selectVariant, selectVersion, selectIpVersion, setupDeployment, selectOffering } from "../model";
import versionHistory from "../model/versionHistory";
import OptionalApps from "./OptionalApps.vue";
export default {
  name: 'deploymentsetup',

  data: ()=>({
    model,
    selectOffering,
    selectVariant,
    selectVersion,
    selectIpVersion,
    versionHistory,
    setupDeployment,
    default_select: 'Please select...',
  }),

  methods: {
    checkNonMandatoryServices() {
      var non_mandatory_service = false;
      model.optional_value_packs.forEach((item) => {
        if ('non_mandatory' in model.optional_value_packs[model.optional_value_packs.indexOf(item)]) {
          non_mandatory_service = true;
        }
      });
      return non_mandatory_service;
    },
  },

  computed: {
    versions() {
      return model.selectedVariant.versions.filter(
        (i) => i.targetAudience == model.targetAudience
      );
    }
  }
}

</script>

<style scoped>
.content {
  margin-left: 20px;
}
.dropdown {
  padding-top: 20px;
}
.content {
  align-items: center;
}

.additional-inputs {
  padding-bottom: 10px;
}

.sector {
  margin-top: 10px;
}
</style>
