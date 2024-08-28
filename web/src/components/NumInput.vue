<template>
  <div class="spinner">
    <label :for="id">{{label}}</label>
    <div class="nirow">
      <input
        type="number"
        v-model="v"
        :min="min"
        :id="id"
        @keypress="kp"
        @blur="reset"
        @wheel.prevent="v = parseInt(v) + ($event.deltaY < 0 ? 1 : -1)"
      >
      <span class="unit">{{unit}}</span>
      <i
        class="icon icon-check"
        :style="{'visibility': v !== modelValue ? 'visible' : 'hidden'}"
        @mousedown="submit()"
      ></i>
      <div class="controls">
        <i @click="inc()" class="icon icon-chevron-up"></i>
        <i @click="dec()" class="icon icon-chevron-down"></i>
      </div>
      <!-- <div class="controls">
        <i @click="exp2next()" class="icon icon-chevron-up two">2</i>
        <i @click="exp2prev()" class="icon icon-chevron-down two">2</i>
      </div> -->
    </div>
  </div>
</template>

<script>
let nextId = 0;

export default {
  name: 'numinput',
  props: ['modelValue', 'min', 'label', 'unit'],
  emits: ['update:modelValue'],
  data(){
    return {
      id: null,
      v: this.modelValue
    };
  },
  mounted(){
    this.id = 'ni' + nextId.toString();
    nextId++;
  },
  watch: {
    modelValue(nv){
      this.v = nv;
    }
  },
  methods: {
    inc(){
      let t = this.modelValue + 1;
      this.$emit('update:modelValue', t);
    },
    dec(){
      let t = Math.max(this.modelValue - 1, this.min);
      this.$emit('update:modelValue', t);
    },
    exp2next(){
      let t = 2 ** (Math.floor(Math.log2(this.modelValue)) + 1);
      this.$emit('update:modelValue', t);
    },
    exp2prev(){
      let t = 2 ** (Math.ceil(Math.log2(this.modelValue)) - 1);
      t = Math.max(t, this.min);
      this.$emit('update:modelValue', t);
    },
    kp(e){
      if(e.keyCode == 13){ // Enter key
        this.submit();
      }
    },
    submit(){
      this.v = parseInt(this.v);
      if(this.v === ''){
        this.v = 0;
      }
      if(this.v < this.min){
        this.v = this.min;
      }
      this.$emit('update:modelValue', this.v);
    },
    reset(e){
      this.v = this.modelValue;
    }
  }
}
</script>
<style scoped lang="less">
.light input, .light .spinner .icon {
  margin-right: 0;
}
.nirow {
  display: flex;
  align-items: center;
  gap: 4px;
}
.unit {
  width: 30px;
}
.spinner .controls {
  display: inline-flex;
  flex-direction: column;
  gap: 4px;
  i.two{
    width: 38px;
    padding-right: 2px;
  }
}
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button
{
  -webkit-appearance: none;
  margin: 0;
}
</style>
