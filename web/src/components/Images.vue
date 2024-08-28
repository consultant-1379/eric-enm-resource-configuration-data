<template>
  <div class="row">
    <div class="tile">
      <div class="header">
        <div class="left">
          <div class="title">Total required storage for images</div>
        </div>
      </div>
      <div class="content">
        <div class="val">{{ (model.csar.total_images_size / (2**30)).toFixed(1) }} GiB</div>
      </div>
    </div>
  </div>

  <div class="row">
    <div class="tile">
      <div class="header">
        <div class="left">
          <div class="title">Images</div>
        </div>
      </div>
      <div class="content">
        <super-table :records="model.csar.images" :fields="imageFields"></super-table>
      </div>
    </div>
  </div>
</template>

<script>
import model from "../model";
import {image as imageFields} from "../model/fields";

import SuperTable from "./SuperTable.vue";

export default {
  name: "images",
  components: {SuperTable},
  data: () => ({ model, imageFields }),
};
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
