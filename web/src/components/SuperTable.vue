<template>
  <div class="table-top">
    <div class="table-top-left">
      <button class="btn" @click="showFilterModal = true"><i class="icon icon-filter"></i></button>
    </div>
    <div class="table-top-right">
      <slot name="top-right"></slot>
    </div>
  </div>
  <table class="table compact sortable">
    <thead>
      <tr>
        <!-- <th>ID</th> -->
        <th
          v-for="f in fields"
          :class="[
            f.sortable ? 'is-sortable' : '',
            f.sortable ? (sort.key == f.key ? (sort.asc ? 'asc' : 'desc') : '') : '',
            f.align ? f.align : ''
          ]"
          @click="f.sortable ? sortBy(f.key) : null"
        >{{f.name}}</th>
      </tr>
    </thead>
    <tbody
      v-for="r in sortedRecords"
      :key="r.id"
    >
      <tr
        :id="id + r.id"
        :class="[
          'rectr',
          (expandable && r.expanded) ? 'expanded' : '',
          expandable ? 'expandable' : '',
          r.highlight ? 'highlight' : ''
        ]"
        @click="expandable ? (r.expanded = !r.expanded) : null"
        @click.middle="r.highlight = !r.highlight"
      >
        <!-- <td>{{r.id}}</td> -->
        <td
          v-for="f in fields"
          :class="[f.align ? f.align : '']"
          v-html="genTd(r, f)"
        ></td>
      </tr>
      <tr v-if="r.expanded" class="exp">
        <td :colspan="fields.length">
          <slot name="expand" :r="r"></slot>
        </td>
      </tr>
    </tbody>
  </table>

  <transition name="dialog">
  <div class="dialog" v-if="showFilterModal" @click.self="showFilterModal = false">
    <div class="content">
      <div class="top">
        <div class="title">Filter</div>
      </div>
      <div class="body">
        <div class="help">
          Start search-term with <code>!</code> to exclude all matches.
        </div>
        <div class="fgroup" v-for="f in filterableFields">
          <div>{{f.name}}</div>
          <input type="text" class="fullwidth" v-if="f.type == 'text'" v-model="filterInputs[f.key]">
          <div class="cbrow" v-else-if="f.type == 'oneOf'">
            <span v-for="o in f.options">
              <input type="checkbox" :id="'cmf' + o.toLowerCase()" :value="o" v-model="filterInputs[f.key]">
              <label :for="'cmf' + o.toLowerCase()">{{o}}</label>
            </span>
          </div>
        </div>
      </div>
      <div class="bottom">
        <button class="btn" @click="resetFilters()"><i class="icon icon-reload"></i>Reset</button>
        <button class="btn" @click="showFilterModal = false">Cancel</button>
        <button class="btn primary" @click="applyFilters()">Apply</button>
      </div>
    </div>
  </div>
</transition>

</template>

<script>
import {filterFuncs} from "../model/fields";

let nextId = 0; // Next available unique ID for a new SuperTable component

export default {
  name: 'supertable',
  props: ['records', 'fields', 'expandable'],
  data: ()=>({
    sort:{
      key: '',
      asc: true
    },
    showFilterModal: false,
    filterInputs: {},
    appliedFilters: {}
  }),
  beforeCreate(){
    // Injecting a Unique ID for this new SuperTable component
    this.id = 'st' + nextId.toString();
    nextId++;
  },
  mounted(){
    let selected = this.records.find(wl=>wl.highlight);
    if(selected){
      // Each record has an application unique id (SuperTable.id + record.id), which can be used to jump to
      document.getElementById(this.id + selected.id).scrollIntoView({
        behavior: 'auto',
        block: 'center',
        inline: 'center'
      });
    }
    this.resetFilters();
    this.applyFilters();
  },
  methods: {
    sortBy(key){
      // Switch order on two consecutive select
      this.sort.asc = this.sort.key === key ? !this.sort.asc : true;
      this.sort.key = key;
    },
    applyFilters(){
      // Applying default filters by generating the corresponding filter functions
      this.showFilterModal = false;
      this.filterableFields.forEach((f)=>{
        this.appliedFilters[f.key] = filterFuncs[f.type](this.filterInputs[f.key]);
      });
    },
    resetFilters(){
      // Setting initial values for filters
      this.filterableFields.forEach((f)=>{
        if(f.type == 'text'){
          this.filterInputs[f.key] = '';
        }else if(f.type == 'oneOf'){
          this.filterInputs[f.key] = f.options.slice();
        }
      });
    },
    genTd(r, f){
      let v = r[f.key];
      if('map' in f){
        v = f.map(v);
      }
      if(f.type == 'has'){
        return v != null ? '<i class="icon icon-check"></i>' : '';
      }else{
        return v ? `${f.prefix || ''}${v} ${f.unit || ''}`: '';
      }
    }
  },
  computed: {
    filterableFields(){
      return this.fields.filter((f)=>(f.filterable));
    },
    sortedRecords(){
      // Shallow copying source list, in order to not change its order
      let records = this.records.slice();
      // Remove any apps that are not enabled
      records = records.filter(function( obj ) {
        return obj.app_enabled;
      });
      // Applying filter functions
      records = records.filter((r)=>{
        let b = true;
        this.filterableFields.forEach((f)=>{
          if(f.key in this.appliedFilters){
            let x = this.appliedFilters[f.key](r[f.key]);
            b &&= x;
          }
        });
        return b;
      });
      // Sorting
      if(!!this.sort.key){
        records.sort((a, b)=>{
          a = a[this.sort.key]
          b = b[this.sort.key]
          return (a === b ? a.id - b.id : a > b ? 1 : -1) * (this.sort.asc ? 1 : -1);
        });
      }
      return records;
    }
  }
};
</script>

<style scoped lang="less">
@import (reference) "@eds/vanilla/variables/light";

@highlight: #fad22d;

.light .table tbody:hover {
  background-color: #dcdcdc;
}
.light .table tr {
  td {
    border-bottom: none;
    border-top: 1px solid #878787;
  }
  &:hover {
    background-color: initial;
  }
  &.expandable {
    cursor: pointer;
  }
  &.expanded {
    font-weight: 700;
  }
  &.highlight {
    background-color: @highlight;
    &:hover{
      background-color: shade(@highlight, 12%);
    }
  }
  &.exp > td{
    border: none;
    padding-left: 32px;
  }
}

.light .dialog > .content {
  max-width: 30%;
}
.dialog .help {
  font-size: 12px;
  margin-bottom: 32px;
}

.fgroup {
  margin-bottom: 32px;
  &>div {
    margin-bottom: 8px;
  }
}
.cbrow {
  display: flex;
  &>*{
    flex-grow: 1;
  }
  label {
    margin-left: 2px;
  }
}
</style>
