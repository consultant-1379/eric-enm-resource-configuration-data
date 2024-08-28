class Node{
  constructor(id, res){
    this.id = id;
    this.res = res;
    this.pods = [];
    this.remaining = Object.assign({}, res);
    this.podNames = new Set();
  }
  check(pod){
    return (
      this.remaining.cpu >= pod.cpu_req &&
      this.remaining.mem >= pod.mem_req &&
      this.remaining.disk >= pod.eps_req &&
      (!pod.affinity || !pod.affinity.startsWith('hard') || !this.podNames.has(pod.name))
      // If pod has hard affinity rule, then pod WITH THE SAME NAME not yet scheduled on this node.
      // TODO: Checking only matching names is naive approach. The real affinity rule should be evaluated.
    )
  }
  score(pod){
    // Based on
    // https://github.com/kubernetes/kubernetes/blob/9aa6f0bc47c9e545dbe4d6b99a080e9720f1ea3f/pkg/scheduler/algorithmprovider/registry.go#L120
    // https://github.com/kubernetes/kubernetes/blob/master/pkg/scheduler/framework/plugins/noderesources/balanced_allocation.go#L82
    // Other scoring plugins don't seem applicable in this simplified simulation
    let cpuFraction = pod.cpu_req / this.remaining.cpu;
    let memFraction = pod.mem_req / this.remaining.mem;
    let diff = Math.abs(cpuFraction - memFraction);
    let score = 1 - diff;
    if(this.podNames.has(pod.name)){
      score = score / 2;
    }
    if(Boolean(pod.affinity) && pod.affinity.startsWith('soft') && this.podNames.has(pod.name)){
      score = score / 4;
    }
    return score;
  }
  assign(pod){
    this.pods.push(pod);
    this.remaining.cpu -= pod.cpu_req;
    this.remaining.mem -= pod.mem_req;
    this.remaining.disk -= pod.eps_req;
    this.podNames.add(pod.name);
  }
}

class Scheduler{
  constructor(nodes){
    this.nodes = nodes;
  }
  scheduleDS(dss){
    if(this.nodes){
      dss.forEach((ds)=>{
        this.nodes.forEach((node)=>{
          node.assign(ds);
        })
      });
    }
    return [];  // TODO
  }
  schedule(pods){
    let unschedulable = [];
    pods.sort((p1, p2)=>(p2.cpu_req - p1.cpu_req));
    // pods.sort((p1, p2)=>(p2.mem_req - p1.mem_req));
    pods.forEach((pod)=>{
      let candidateNodes = this.nodes.filter((node)=>(node.check(pod)));
      if(candidateNodes.length > 0){
        let bestScore = 0;
        let bestNode = candidateNodes[0];
        candidateNodes.forEach((node)=>{
          let score = node.score(pod);
          if(score > bestScore){
            bestScore = score;
            bestNode = node;
          }
        });
        // let bestNode = candidateNodes[Math.floor(Math.random() * candidateNodes.length)];
        // let bestNode = candidateNodes[0];
        bestNode.assign(pod);
      }else{
        unschedulable.push(pod);
      }
    });
    return unschedulable;
  }
}

const simulatorCache = {};

class Cluster{
  constructor(nodeTemplate, workloads){
    this.nodeTemplate = nodeTemplate;
    this.dss = [];
    this.pods = [];
    workloads.forEach((wl)=>{
      if (wl.app_enabled) {
        if (wl.replicas === 'NC') {
          this.dss.push(wl);
        } else {
          for (let i = 0; i < wl.replicas; i++) {
            this.pods.push(wl);
          }
        }
      }
    });
  }
  calcOptimalNodeCount(initialEstimation){
    let estimation = initialEstimation;
    let unschedulable_prev = -1;
    while(true){
      let { unschedulable } = this.simulate(estimation);
      let unschedulable_len = unschedulable.length
      if(unschedulable_prev == unschedulable_len){
        // Emergency exit, if the problem is unsolvable by just adding additional nodes
        return 0;
      }
      unschedulable_prev = unschedulable_len;
      if(unschedulable_prev == 0){
        return estimation;
      }
      estimation++;
    }
  }
  simulate(nodeCount){
    let nodes = Array(nodeCount);
    for(let i=0; i < nodeCount; i++){
      nodes[i] = new Node(i, {
        cpu: this.nodeTemplate.cpu,
        mem: this.nodeTemplate.mem,
        disk: this.nodeTemplate.disk
      });
    }
    const sch = new Scheduler(nodes);
    let unschedulable = [...sch.scheduleDS(this.dss), ...sch.schedule(this.pods)];
    return {
      nodes,
      unschedulable
    };
  }
}

export default Cluster;
