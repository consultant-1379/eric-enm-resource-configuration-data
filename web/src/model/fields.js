export const wl = Object.freeze([
  {
    name: 'Name',
    key: 'name',
    type: 'text',
    sortable: true,
    filterable: true
  },
  {
    name: 'Kind',
    key: 'kind',
    type: 'oneOf',
    options: ['Deployment', 'StatefulSet', 'DaemonSet', 'Job', 'CronJob', 'RedisCluster', 'CassandraCluster', 'Kafka'],
    sortable: true,
    filterable: true
  },
  {
    name: 'Integration Chart',
    key: 'chart',
    sortable: true,
    filterable: false
  },
  {
    name: 'Replicas',
    key: 'replicas',
    type: 'num',
    sortable: true,
    filterable: false,
    align: 'center',
    map: v=>(v == -1 ? 'NodeCount' : v)
  },
  {
    name: 'CPU Requests',
    key: 'cpu_req',
    type: 'num',
    sortable: true,
    filterable: false,
    unit: 'm',
    align: 'right',
    humanScale: 1000,
    humanUnit: 'vCPU',
  },
  {
    name: 'CPU Limits',
    key: 'cpu_lim',
    type: 'num',
    sortable: true,
    filterable: false,
    unit: 'm',
    align: 'right',
    humanScale: 1000,
    humanUnit: 'vCPU',
  },
  {
    name: 'Memory Requests',
    key: 'mem_req',
    type: 'num',
    sortable: true,
    filterable: false,
    unit: 'MiB',
    align: 'right',
    humanScale: 1024,
    humanUnit: 'GiB',
  },
  {
    name: 'Memory Limits',
    key: 'mem_lim',
    type: 'num',
    sortable: true,
    filterable: false,
    unit: 'MiB',
    align: 'right',
    humanScale: 1024,
    humanUnit: 'GiB',
  }
]);

export const pvc = Object.freeze([
  {
    name: 'Name',
    key: 'name',
    type: 'text',
    sortable: true,
    filterable: true
  },
  {
    name: 'Chart',
    key: 'chart',
    type: 'text',
    sortable: true,
    filterable: true
  },
  {
    name: 'Replicas',
    key: 'instances',
    type: 'num',
    sortable: true,
    filterable: false
  },
  {
    name: 'Access Mode',
    key: 'type',
    type: 'oneOf',
    options: ['RWX', 'RWO'],
    sortable: true,
    filterable: true
  },
  {
    name: 'Size',
    key: 'size',
    type: 'num',
    sortable: true,
    align: 'right',
    filterable: false,
    unit: 'GiB'
  },
  {
    name: 'Total Size',
    key: 'total',
    type: 'num',
    sortable: true,
    align: 'right',
    filterable: false,
    unit: 'GiB'
  },
  {
    name: 'Restore-Backup',
    key: 'fullBackup',
    type: 'text',
    align: 'center',
    sortable: true,
  },
  {
    name: 'Rollback-Backup',
    key: 'rollback',
    type: 'text',
    align: 'center',
    sortable: true,
  }
]);

export const image = Object.freeze([
  {
    name: 'Name',
    key: 'name',
    type: 'text',
    sortable: true,
    filterable: true
  },
  {
    name: 'Tag',
    key: 'tag',
    type: 'text',
    sortable: false,
    filterable: false
  }
]);

export const filterFuncs = Object.freeze({
  text(query){
    if(query == ''){
      return (field)=>(true);
    }
    if(query[0] == '!'){
      return (field)=>(field ? !field.includes(query.substr(1)) : true);
    }else{
      return (field)=>(field ? field.includes(query) : false);
    }
  },
  oneOf(selected){
    return (field)=>(selected.includes(field));
  }
});


export const resources = Object.freeze({
  cpu: {
    name: 'CPU',
    unit: 'vCPU',
    sumscale: 1000,
    wlkey: 'cpu'
  },
  mem: {
    name: 'Memory',
    unit: 'GiB',
    sumscale: 1024,
    wlkey: 'mem'
  },
  disk: {
    name: 'Disk',
    unit: 'GiB',
    sumscale: 1,
    wlkey: 'disk'
  }
});

export const validation_errors = Object.freeze([
  {
    name: 'Name',
    key: 'name',
    type: 'text',
    sortable: true,
    filterable: true
  },
  {
    name: 'Integration Chart',
    key: 'chart',
    type: 'text',
    sortable: true,
    filterable: false
  },
  {
    name: 'Errors',
    key: 'error',
    type: 'text',
    sortable: false,
    filterable: false
  }
]);

export const app = Object.freeze([
  {
    name: 'Name',
    key: 'name',
    type: 'text',
    sortable: false,
    filterable: false
  },
  {
    name: 'CPU Requests',
    key: 'cpu_req',
    type: 'num',
    sortable: true,
    filterable: false,
    unit: 'm',
    align: 'right',
    humanScale: 1000,
    humanUnit: 'vCPU',
  },
  {
    name: 'CPU Limits',
    key: 'cpu_lim',
    type: 'num',
    sortable: true,
    filterable: false,
    unit: 'm',
    align: 'right',
    humanScale: 1000,
    humanUnit: 'vCPU',
  },
  {
    name: 'Memory Requests',
    key: 'mem_req',
    type: 'num',
    sortable: true,
    filterable: false,
    unit: 'MiB',
    align: 'right',
    humanScale: 1024,
    humanUnit: 'GiB',
  },
  {
    name: 'Memory Limits',
    key: 'mem_lim',
    type: 'num',
    sortable: true,
    filterable: false,
    unit: 'MiB',
    align: 'right',
    humanScale: 1024,
    humanUnit: 'GiB',
  }
]);

