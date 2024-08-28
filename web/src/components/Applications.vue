<template>
  <div class="row">
    <div class="tile">
      <div class="header">
        <div class="left">
          <div class="title">Applications</div>
        </div>
      </div>
      <div class="content">
        <super-table :records="model.apps" :fields="appFields"></super-table>
      </div>
    </div>
  </div>
</template>

<script>
import model from "../model";
import {app as appFields} from "../model/fields";
import SuperTable from "./SuperTable.vue";

export default {
  name: "applications",
  components: {SuperTable},
  data: () => ({
    model,
    appFields
    })
};
</script>
