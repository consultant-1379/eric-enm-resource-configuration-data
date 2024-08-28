<template>
  <div class="sector">
    <label class="switch">
      <input type="checkbox" v-model="valuePack.app_enabled" v-on:click="(check_vp_enabled(valuePack.name))?disableApp(valuePack):enableApp(valuePack)">
      <i class="ball"></i>
      <span class="message left" data-enabled="&#8205" data-disabled="&#8205"></span>
    </label>
    {{ valuePack.name }}
    <b class="tooltip">
      <i class="icon icon-info"></i>
      <span class="tooltiptext">
         {{ valuePack.description }}
      </span>
    </b>
  </div>
</template>

<script>
import model from "../model";
export default {
  name: "optionalapps",
  props: {
    valuePack: {
      required: true
    },
    optionalApps: {
      required: true
    },
  },
  data: () => ({ model }),
  methods: {
    check_vp_enabled(vpName) {
      this.model.isModelReady=false
      const index = this.optionalApps.findIndex(
      (item) => item.name === vpName
      );
      return this.optionalApps[index].app_enabled;
    },
    enableApp(vp) {
      const index = this.optionalApps.findIndex(
        (item) => item.name === vp.name
      );
      this.optionalApps[index].app_enabled = true;
    },
    disableApp(vp) {
      const index = this.optionalApps.findIndex(
      (item) => item.name === vp.name
      );
      this.optionalApps[index].app_enabled = false;
    },
  },
};
</script>

<style scoped>
.sector {
  margin-top: 1%;
}

.ball {
  padding: 2px 0px 0px 2px;
}
</style>