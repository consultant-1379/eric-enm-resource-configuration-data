<template>
<div>
  <label>{{res.name}}</label>
  <div class="c">
    <transition name="fade">
      <i class="icon icon-check" v-if="val > targetVal"></i>
      <i class="icon icon-triangle-warning" v-else></i>
    </transition>
  </div>
  {{val}} > {{targetVal}}
</div>
</template>

<script>
import model from '../model';

export default {
  name: 'reschecker',
  props: ['res', 'target'],
  computed: {
    targetVal(){
      return Math.ceil((model.overview[this.target]["wl_" + this.res.wlkey] +
      model.overview[this.target]["wlds_" + this.res.wlkey] * model.calc.node_count) / this.res.sumscale);
    },
    val(){
      return model.calc[this.res.wlkey] * model.calc.node_count;
    }
  }
}
</script>

<style scoped>
.c{
  display: inline-block;
  height: 68px;
  width: 68px;
  position: relative;
}
.icon{
  font-size: 68px;
  position: absolute;
}
.fade-enter-active,
.fade-leave-active
{
  transition: all .3s ease;
}
.fade-enter-from,
.fade-leave-to
{
  opacity: 0;
  -webkit-transform: scale(1.5);
          transform: scale(1.5);
}
</style>
