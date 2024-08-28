<template>

  <div :class="['select', opened ? 'open' : 'closed']" @click="opened = !opened">
    <button class="btn current-options">{{ default }}</button>
    <div class="options-list">
      <div class="item" v-for="(o, i) in options" @click="$emit('select', i)">{{ o[displaykey] }}</div>
    </div>
  </div>

</template>

<script>

export default {
  name: 'dropdownselect',
  props: ['options', 'displaykey', 'default'],
  emits: ['select'],
  data(){
    return {
      opened: false
    };
  }
}

</script>

<style scoped>

.select{
  padding: 11px 22px 11px 22px;
  max-width: 248px;
  width: 248px;
}
.select .options-list{
  max-width: 200px;
}

</style>
