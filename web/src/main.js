import { createApp } from 'vue';
import { createRouter, createWebHashHistory } from 'vue-router';
import App from './App.vue';
import Applications from './components/Applications.vue';
import DeploymentSetup from './components/DeploymentSetup.vue';
import Overview from './components/Overview.vue';
import CpuMem from './components/CpuMem.vue';
import Storage from './components/Storage.vue';
import Images from './components/Images.vue';
import NodeCalc from './components/NodeCalc.vue';
import model from './model';
import { load } from './model';
import DropDownSelect from './components/DropDownSelect.vue';
import OptionalApps from './components/OptionalApps.vue';
import WorkloadConfigurationValidator from './components/WorkloadConfigurationValidator.vue'
import ReleaseComparator from './components/ReleaseComparator.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {name: 'Deployment Setup', path: '/deploymentsetup', component: DeploymentSetup},
    {name: 'Resource Overview', path: '/overview', component: Overview},
    {name: 'Applications', path: '/applications', component: Applications},
    {name: 'Workloads', path: '/workloads', component: CpuMem},
    {name: 'Storage', path: '/storage', component: Storage},
    {name: 'Images', path: '/images', component: Images},
    {name: 'Node Calculator', path: '/nodecalc', component: NodeCalc},
    {name: 'Workload Configuration Validator', path: '/workloadconfigvalid', component: WorkloadConfigurationValidator},
    {name: 'Compare Releases', path: '/compare', component: ReleaseComparator},
    {path: '/', redirect: '/deploymentsetup'},
    {path: '/conf', redirect(to){
      if('ta' in to.query){
        model.targetAudience = to.query.ta;
      }
      return {path: '/deploymentsetup', query: {}};
    }}
  ],
});

router.beforeEach((to, from, next) => {
  if (to.name !== 'Deployment Setup' && to.name !== 'Compare Releases' && !model.isModelReady) next({ name: 'Deployment Setup' })
  else next()
});

const app = createApp(App);
app.component("DropDownSelect", DropDownSelect);
app.component("OptionalApps", OptionalApps);
app.component("Overview", Overview);
app.config.devtools = true;
app.use(router);
app.mount('#app');

load();
