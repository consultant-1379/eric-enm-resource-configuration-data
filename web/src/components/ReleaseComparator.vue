<template>
  <div class="row">
    <div class="tile">
      <div class="content">
        <p>This tool performs comparison between the resource requirements of two different releases.</p>
        <div class="dropdown">
          <div>
            <b class="tooltip">Deployment Size:
              <i class="icon icon-info"></i>
              <span class="tooltiptext">
                This section allows the user to select the Deployment Size.
              </span>
            </b>
          </div>
          <DropDownSelect :options="model.variants" :displaykey="'name'" @select="selectVariantToCompare($event)" :default="model.selectedVariant.name"></DropDownSelect>
        </div>
        <div class="dropdown">
          <div>
            <b class="tooltip">
              <span v-if="model.targetAudience == 'pdu'">From Product Set Version: </span>
              <span v-else>From Release Version: </span>
              <i class="icon icon-info"></i>
              <span class="tooltiptext">
                This section allows the user to select the Release Version.
              </span>
            </b>
          </div>
          <DropDownSelect :options="model.versions.slice(1)" :displaykey="'name'" @select="selectFromVersion($event + 1)" :default="model.selected_from_version.name"></DropDownSelect>
        </div>
        <div v-if="model.prepared">
          <div class="additional-inputs" v-if="model.prepared && model.optional_value_packs.length" >
            <b class="tooltip">Select optional applications for From Release:
              <i class="icon icon-info"></i>
              <span class="tooltiptext">
              This section allows the user to select optional applications.
              </span>
            </b>
          </div>
            <ul style="list-style-type: None">
              <li v-for="value_pack in model.optional_value_packs" :key="value_pack">
                 <OptionalApps :valuePack="value_pack" :optionalApps="model.optional_value_packs"></OptionalApps>
               </li>
            </ul>
        </div>
        <div class="dropdown">
          <div v-if="model.selected_from_version.name != default_select">
            <div>
              <b class="tooltip">
                <span v-if="model.targetAudience == 'pdu'">To Product Set Version: </span>
                <span v-else>To Release Version: </span>
                <i class="icon icon-info"></i>
                <span class="tooltiptext">
                  This section allows the user to select the ENM Release Version.
                </span>
              </b>
            </div>
            <DropDownSelect :options="model.to_versions" :displaykey="'name'" @select="selectToVersion($event)" :default="model.selected_to_version.name"></DropDownSelect>
          </div>
          <div v-if="model.prepared_to_state">
            <div class="additional-inputs" v-if="model.optional_value_packs_to_state.length" >
              <b class="tooltip">Select optional applications for To Release:
                <i class="icon icon-info"></i>
                <span class="tooltiptext">
                This section allows the user to select optional applications.
                </span>
              </b>
            </div>
              <ul style="list-style-type: None">
                <li v-for="value_pack in model.optional_value_packs_to_state" :key="value_pack">
                  <OptionalApps :valuePack="value_pack" :optionalApps="model.optional_value_packs_to_state"></OptionalApps>
                </li>
              </ul>
          </div>
          <div class="dropdown" v-if="model.prepared_to_state && model.ip_versions.length != 0">
            <div>
              <b class="tooltip">IP Address Version:
                <i class="icon icon-info"></i>
                <span class="tooltiptext">
                  This section allows the user to select the IP Address Version.
                </span>
              </b>
            </div>
            <DropDownSelect :options="model.ip_versions" :displaykey="'name'" @select="selectIpVersion($event)" :default="model.selected_ip_version.name"></DropDownSelect>
          </div>
          <div v-show="model.prepared_to_state && (model.ip_versions.length == 0 || model.selected_ip_version.alias != 'default')">
            <button class="btn primary" v-on:click="compareVersions()">Compare Releases</button>
            <button class="btn primary" v-on:click="resetComparison()">Reset Releases</button>
          </div>
        </div>
      </div>
    </div>
  <div class="row" v-if="model.is_to_model_ready_to_state">
     <Overview ></Overview>
  </div>
  </div>
</template>

<script>
import model from "../model";
import { selectVariantToCompare, selectToVersion, selectFromVersion, selectIpVersion, compareVersions, resetComparison } from "../model";

export default {
  data: ()=>({
    model,
    selectVariantToCompare,
    selectToVersion,
    selectFromVersion,
    selectIpVersion,
    compareVersions,
    resetComparison,
    default_select: 'Please select...',
  }),

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
</style>
