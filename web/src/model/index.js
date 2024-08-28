import { reactive, vModelSelect } from 'vue';

const default_select = {name: "Please select...", alias: "default"}
const rcd_api_url = import.meta.env.VITE_APP_RCD_URL ? import.meta.env.VITE_APP_RCD_URL : "https://resourceconfigurationdata.internal.ericsson.com:5000/api/"

const model = reactive({
  isModelReady: false,
  prepared: false,
  prepared_to_state: false,
  is_model_ready_from_state: false,
  is_to_model_ready_to_state: false,
  default_select: default_select,
  ip_versions: [],
  selected_ip_version: default_select,
  offerings: [],
  filteredVariants: [],
  variants: [],
  versions: [],
  to_versions: [],
  selectedOffering: default_select,
  selectedVariant: default_select,
  selectedVersion: default_select,
  selected_from_version: default_select,
  selected_to_version: default_select,
  targetAudience: import.meta.env.VITE_APP_ENV_TYPE ? import.meta.env.VITE_APP_ENV_TYPE : 'cu',
  selected_optional_apps: [],
  eic_mandatory_apps: [],
  eic_mandatory_app_names: [],
  selected_to_optional_apps: [],
  show_notification: false,
  export_failed_404: false,
});

async function prepareData(offering, deployment_size, file_name, ip_version, optional_apps) {
  const res = await fetch(rcd_api_url + 'getReleaseData?' + new URLSearchParams({
    deployment_size: deployment_size,
    product: offering,
    release_version: file_name,
    ip_version: ip_version.alias,
    optional_apps: optional_apps}),
    { cache: "no-store"});
  const data = (await res.json());
  model.workloads = data.workloads;
  model.pvcs = data.pvcs;
  model.csar = data.csar;
  model.overview = data.overview;
  model.config_maps = data.config_maps;
  model.secrets = data.secrets;
  model.services = data.services;
  model.ingresses = data.ingresses;
  model.eric_ingresses = data.eric_ingresses;
  model.calc = data.calc;
  model.validation_errors = data.validation_errors;
  if ("apps" in data) {
    model.apps = data.apps;
  }
}

async function prepareComparisonData() {
  const res = await fetch(rcd_api_url + 'getReleaseDataComparison?' + new URLSearchParams({
    deployment_size: model.selectedVariant.datapath,
    from_release_version: model.selected_from_version.file,
    to_release_version: model.selected_to_version.file,
    from_optional_apps: model.selected_optional_apps,
    to_optional_apps: model.selected_to_optional_apps,
    ip_version: model.selected_ip_version.alias}),
    { cache: "no-store"});
  model.version_comparison_delta = (await res.json());
}

export async function load() {
  const res = await fetch('/data/index.json', { cache: "no-store"});
  if(model.targetAudience == 'cu') {
    model.variants = (Object.values(await res.json()).filter( v => v.name == 'Extra-Large Cloud Native ENM' || v.name == 'Small Cloud Native ENM' ||  v.name == 'Standard Size Commercial Deployment EIC'));
  } else {
    model.variants = (await res.json());
  }
  var offerings = Array.from(new Set(model.variants.map((item) => item.offering)));
  for (var i = 0; i < offerings.length; ++i) {
    var offering = {name: offerings[i]}
    model.offerings.push(offering)
  }
}

export async function selectOffering(oid){
  model.selectedOffering = model.offerings[oid];
  model.filteredVariants = model.variants.filter((i)=>(i.offering === model.selectedOffering.name));
  await clearVariantSelection();
  await clearVersionSelection();
}

export async function selectVariant(vid){
  model.selectedVariant = model.filteredVariants[vid];
  model.versions = model.selectedVariant.versions.filter((i)=>(i.targetAudience === model.targetAudience));
  await clearVersionSelection();
}

export async function selectVariantToCompare(vid){
  await resetComparison();
  model.selectedVariant = model.variants[vid];
  model.versions = model.selectedVariant.versions.filter((i)=>(i.targetAudience === model.targetAudience));
}

export async function prepareOptions(selected_version, prepared_key, optional_apps_key){
  if (model.selectedOffering.name === 'EIC') {
    const res = await fetch('./data/' + model.selectedVariant.datapath + '/' + selected_version['file'] + '/apps.json', { cache: "no-store"});
    const data = Object.values(await res.json());
    model[optional_apps_key] = data.filter( v => v.optional == true);
    model.eic_mandatory_apps = data.filter( v=> v.optional == false);
    model.eic_mandatory_app_names= Array.from(new Set(model.eic_mandatory_apps.map((item) => item.name)));
  } else {
    const res = await fetch('./data/' + model.selectedVariant.datapath + '/' + selected_version['file'] + '.json', { cache: "no-store"});
    const data = (await res.json());
    model[optional_apps_key] = data.optional_value_packs;
    if (data.overview.other_requirements) {
      if (data.overview.other_requirements.supported_ip_versions) {
        model.ip_versions = data.overview.other_requirements.supported_ip_versions
      }
    }
  }
  model[prepared_key] = true;
}

export async function selectVersion(vid){
  model.selectedVersion = model.versions[vid];
  await clearIpVersionSelection();
  prepareOptions(model.selectedVersion, 'prepared', 'optional_value_packs')
  model.isModelReady = false;
}

export async function selectFromVersion(vid){
  model.selected_from_version = model.versions[vid];
  prepareOptions(model.selected_from_version, 'prepared', 'optional_value_packs')
  model.to_versions = model.versions.slice(0, vid);
}

export async function selectToVersion(vid){
  model.selected_to_version = model.versions[vid];
  await clearIpVersionSelection();
  prepareOptions(model.selected_to_version, 'prepared_to_state', 'optional_value_packs_to_state')
}

export async function getEnabledOptionalApps(optional_apps){
  var enabled_apps = [];
  optional_apps.forEach((app) => {
    if (app.app_enabled) {
      enabled_apps.push(app.name)
    }
  });
  return enabled_apps;
}

export async function selectIpVersion(vid){
  model.selected_ip_version = model.ip_versions[vid];
}

export async function resetDeploymentSetup() {
  model.selectedVariant = model.default_select;
  await clearVersionSelection();
  model.versions = []
}

export async function clearVersionSelection() {
  model.selectedVersion = model.default_select;
  await clearIpVersionSelection();
  model.isModelReady = false;
}

export async function clearIpVersionSelection() {
  model.selected_ip_version = model.default_select;
  model.ip_versions = [];
}

export async function clearVariantSelection() {
  model.selectedVariant = model.default_select;
  model.isModelReady = false;
}

export async function setupDeployment(){
  var optional_apps = []
  model.selected_optional_apps = (await getEnabledOptionalApps(model.optional_value_packs));
  if (model.selectedOffering.name === 'cENM') {
    optional_apps = model.selected_optional_apps
  }
  else {
    optional_apps = model.selected_optional_apps.concat(model.eic_mandatory_app_names)
  }

  await prepareData(model.selectedOffering.name, model.selectedVariant.datapath, model.selectedVersion.file, model.selected_ip_version, optional_apps);
  model.is_to_model_ready_to_state = false;
  model.isModelReady = model.selectedVersion.name != default_select.name;
  model.display_other_requirements_section = Object.keys(model.overview.other_requirements).length > 1;
  if (model.selectedVariant.name == default_select.name || model.selectedVersion.name == default_select.name) {
    model.show_notification = true;
  } else {
    this.$router.push('/overview');
  }
}

export async function resetComparison() {
  model.selected_from_version = model.default_select;
  model.selected_to_version = model.default_select;
  model.selectedVariant = model.default_select;
  model.selected_ip_version = model.default_select;
  model.ip_versions = [];
  model.isModelReady = false;
  model.is_to_model_ready_to_state =false;
  model.is_model_ready_from_state = false;
}

export async function compareVersions(){
  var optional_apps = []
  var to_optional_apps = []
  model.selected_optional_apps = (await getEnabledOptionalApps(model.optional_value_packs));
  if (model.selectedOffering.name === 'EIC')  {
    optional_apps = model.selected_optional_apps.concat(model.eic_mandatory_app_names)
  }
  else {
    optional_apps = model.selected_optional_apps
  }

  await prepareData(model.selectedOffering.name, model.selectedVariant.datapath, model.selected_from_version.file, model.selected_ip_version, optional_apps);
  model.selected_to_optional_apps = (await getEnabledOptionalApps(model.optional_value_packs_to_state));
  if (model.selectedOffering.name === 'EIC') {
    to_optional_apps = model.selected_to_optional_apps.concat(model.eic_mandatory_app_names)
  }
  else {
    model.selectedOffering.name = 'cENM';
    to_optional_apps = model.selected_to_optional_apps;
  }

  await prepareComparisonData();
  model.isModelReady = false;
  model.display_other_requirements_section = Object.keys(model.version_comparison_delta.other_requirements).length > 1
  model.is_to_model_ready_to_state = model.selected_from_version.name != default_select.name;
  model.is_model_ready_from_state = model.selected_to_version.name != default_select.name;
}

export async function exportExcel(){
  var optional_apps = []
  model.selected_optional_apps = (await getEnabledOptionalApps(model.optional_value_packs));
  if (model.selectedOffering.name === 'cENM') {
    optional_apps = model.selected_optional_apps
  } else {
    optional_apps = model.selected_optional_apps.concat(model.eic_mandatory_app_names)
  }

  const response = await fetchResource(rcd_api_url + 'getExcelData?' + new URLSearchParams({
    deployment_size: model.selectedVariant.datapath,
    product: model.selectedOffering.name,
    release_version: model.selectedVersion.file,
    ip_version: model.selected_ip_version,
    optional_apps: optional_apps}),
    { cache: "no-store"});

  if (response) {
      var url = window.URL.createObjectURL(await response.blob());
      var a = document.createElement('a');
      a.href = url;
      a.download = model.selectedVariant.datapath + '_' + model.selectedVersion.file + '.xlsx';
      document.body.appendChild(a); // we need to append the element to the dom -> otherwise it will not work in firefox
      a.click();
      a.remove();  //afterwards we remove the element again
  }
}

async function fetchResource(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      if (response.status === 404){
        model.export_failed_404 = true
      }
      throw Error(`${response.status} ${response.statusText}`);
    }
    return response;
  } catch (error) {
    console.log(`Error fetching ${url}`, error);
  }
}

export default model;
