
<template>
    <div v-if="model.validation_errors.length == 0">
        <div class="header">
            <div class="left">
                <div class="title"></div>
            </div>
        </div>
        <div class="content">
            <div>
                <div class="val">
                    No validation issues found for product set: {{model.selectedVersion.name}}
                </div>
            </div>
       </div>
    </div>
   <div class="row" v-else>
    <div class="tile">
      <div class="header">
        <div class="left">
          <div class="title">Helm Chart Validation Errors</div>
        </div>
      </div>
      <div class="content">
        <super-table :records="model.validation_errors" :fields="errors"></super-table>
      </div>
    </div>
  </div>
</template>

<script>
import model from "../model";
import {validation_errors as errors} from "../model/fields";

import SuperTable from "./SuperTable.vue";

export default {
  name: "validation_errors",
  components: {SuperTable},
  data: () => ({ model, errors }),
}
</script>

<style scoped>
tbody span {
  color: #929292;
}
tbody b {
  font-weight: 700;
}
.val {
  font-size: medium;
  margin: 20px;
}
</style>