# Model

The application has a single central model, which is explicitly made reactive.

Upon changing cENM variant or version, a new JSON file gets downloaded, processed and loaded into the previously created model. Due to the reactive manner of the model, after changing any value in it, all the components which are using that specific data get updated.

Here is an overview on the definition of data-model using typescript syntax.

## Top level model
```ts
{
  isModelReady: Boolean,
  variants: Array<Variant>,
  versions: Array<Version>,
  selectedVariant: Variant,
  selectedVariant: Version,
  workloads: Array<Workload>,
  pvcs: Array<PVC>,
  config_maps: Array<ConfigMap>,
  secrets: Array<Secret>,
  services: Array<Service>,
  ingresses: Array<Ingress>,
  eric_ingresses: Array<EricIngress>,
  overview: Overview ,
  csar: {}
}
```

## ConfigMap
```ts
{
  chart: string,
  name: string,
  app_enabled: boolean
}
```

## Secret
```ts
{
  chart: string,
  name: string,
  app_enabled: boolean
}
```

## Service
```ts
{
  chart: string,
  name: string,
  app_enabled: boolean
}
```

## Ingress
```ts
{
  chart: string,
  name: string,
  app_enabled: boolean
}
```

## EricIngress
```ts
{
  chart: string,
  name: string,
  app_enabled: boolean
}
```

## Variant
```ts
{
  name: string,
  datapath: string,
  versions: Array<string>
}
```

## Version
```ts
{
  name: string,
  file: string,
  targetAudience: string
}
```

## Workload
```ts
{
  chart: string,
  name: string,
  kind: string,
  sg: string | null,
  replicas: number | "NC",
  containers: Array<Container>,
  pvcs: Array<string>,
  affinity: string | null,
  update_strategy: {} | null,
  pdb: {type: string, value: number} | null,
  id: number,
  cpu_req: number,
  cpu_lim: number,
  mem_req: number,
  mem_lim: number,
  eps_req: number,
  eps_lim: number,
  expanded: boolean,
  hover: boolean,
  app_enabled: boolean
}
```

## Container
```ts
{
  name: string,
  image: string,
  cpu_req: number,
  cpu_lim: number,
  mem_req: number,
  mem_lim: number,
  eps_req: number,
  eps_lim: number
}
```

## PVC
```ts
{
  chart: string,
  name: string,
  type: "RWX" | "RWO",
  storageClass: string | null,
  appName: string | null,
  instances: number,
  size: number,
  id: number,
  app_enabled: boolean
}
```

## Overview
```ts
{
    total {
        pods: number | 0
        rwo: number | 0
        rwx: number | 0
    }
    sum {
        rwo: number | 0
        rwx: number | 0
    }
    requests {
        wl_cpu: number | 0
        wl_mem: number | 0
        wl_disk: number | 0
        wlds_cpu: number | 0
        wlds_mem: number | 0
        wlds_disk: number | 0
    }
    limits {
        wl_cpu: number | 0
        wl_mem: number | 0
        wl_disk: number | 0
        wlds_cpu: number | 0
        wlds_mem: number | 0
        wlds_disk: number | 0
    }
    max {
        replica_count: number | 0
        cpu_req: number | 0
        cpu_lim: number | 0
        mem_req: number | 0
        mem_lim: number | 0
        eps_req: number | 0
        eps_lim: number | 0
    }
    min {
        worker_nodes: number | 0
        worker_cpu: number | 0
        worker_mem: number | 0
        worker_disk: number | 0
        hot_spare_workers: number | 1
    }
}
```

## Resources
```ts
{
  cpu: number,
  mem: number,
  eps: number
}
```

## Image
```ts
{
  prefix: string,
  name: string,
  tag: string,
  app_enabled: boolean
}
```
