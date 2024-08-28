// Test for the Resource overview page with no optional apps enabled
const { test, expect } = require('@playwright/test');
async function goToDeploymentSetup(page){
  await page.goto('http://localhost:5001/#/');
  await page.goto('http://localhost:5001/#/deploymentsetup');
}

async function selectStandardSizeEICResourceOverview(page){
  await page.click('text=Please select...');
  await page.getByText('EIC', { exact: true }).click();
  await page.click('text=Please select...');
  await page.click('text=Standard Size Commercial Deployment EIC');
  await page.click('text=Please select...');
  await page.click('text=2.19.0-102');
  await page.click('text=Setup Deployment');
}

// Application Total Requirements Tests
const eicApplicationTotalRequirementsSection = 'EIC Application Total Requirements:'
const applicationTotalRequirementsSection = 'Application Total Requirements:'
const applicationTotalRequirementsTests = [
  {index: 1, name: 'CPU Requests', expectedHeading: 'CPU: ', expectedValue: 'Requests: 67 vCPU (+ 0.10 vCPU/worker)'},
  {index: 2, name: 'Memory Requests', expectedHeading: 'Memory:', expectedValue: 'Requests: 96 GiB (+ 0.10 GiB/worker)'}
]

applicationTotalRequirementsTests.forEach(function (item) {
  test(eicApplicationTotalRequirementsSection + ': Check ' + item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectStandardSizeEICResourceOverview(page);
    await page.click('text=' + applicationTotalRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(2) .content div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(2) .content > :nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});

// Storage Requirements Tests
const eicPersistentStorageRequirementsSection = 'EIC Storage Requirements:'
const persistentStorageRequirementsSection = 'Storage Requirements:'
const persistentStorageRequirementsTests = [
  {index: 1, name: 'RWO', expectedHeading: 'RWO (ReadWriteOnce):', expectedValue: '427 GiB'},
  {index: 2, name: 'Ephemeral Storage:', expectedHeading: 'Ephemeral Storage:', expectedValue: '105 GiB (+ 0 GiB/worker)'}
]

persistentStorageRequirementsTests.forEach(function (item) {
  test(eicPersistentStorageRequirementsSection + ': Check ' + item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectStandardSizeEICResourceOverview(page);
    await page.click('text=' + persistentStorageRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(3) .content div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(3) .content div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});

// Container Registry Requirements Tests
const eicContainerRegistryRequirementsSection = 'EIC Container Registry Requirements:'
const containerRegistryRequirementsSection = 'Container Registry Requirements:'
const containerRegistryRequirementsTests = [
  {index: 1, name: 'Minimum required disk storage space', expectedHeading: 'Minimum required disk storage space:', expectedValue: '17 GB'}
]

containerRegistryRequirementsTests.forEach(function (item) {
  test(eicContainerRegistryRequirementsSection + ': Check ' +  item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectStandardSizeEICResourceOverview(page);
    await page.click('text=' + containerRegistryRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(5) .content div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(5) .content div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});

// Cluster Resource Overview Tests
const eicClusterResourceOverviewSection = 'EIC K8s Resources Overview:'
const clusterResourceOverviewSection = 'K8s Resources Overview:'
const clusterResourceOverviewTests = [
  {index: 1, name: 'Total Pods', expectedValue: 'Total Pods: 98 '},
  {index: 2, name: 'Total ConfigMaps', expectedValue: 'Total ConfigMaps: 104'},
  {index: 3, name: 'Total Secrets', expectedValue: 'Total Secrets: 43'},
  {index: 4, name: 'Total Services', expectedValue: 'Total Services: 63'},
  {index: 5, name: 'Total Ingresses', expectedValue: 'Total Ingresses: 0'},
  {index: 6, name: 'Total EricIngresses', expectedValue: 'Total EricIngresses: 0'},
  {index: 7, name: 'Total RWO', expectedValue: 'Total RWO: 36'},
  {index: 8, name: 'Total RWX', expectedValue: 'Total RWX: 0'},
]

clusterResourceOverviewTests.forEach(function (item) {
  test(eicClusterResourceOverviewSection + ': Check ' +  item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectStandardSizeEICResourceOverview(page);
    await page.click('text=' + clusterResourceOverviewSection);
    const value = await page.innerText('.row div:nth-child(9) .content div:nth-child(' + item.index + ') .val');
    expect(value).toEqual(item.expectedValue);
  });
});

// Storage Requirements For Backups
const backupStorageRequirementsSection = 'Storage Requirements For Backups:'
const backupStorageRequirementsTests = [
  {index: 1, name: 'BRO PVC Storage', expectedHeading: 'BRO PVC Storage:', expectedValue: '15 GiB'},
  {index: 2, name: 'External Backup Storage', expectedHeading: 'External Backup Storage:', expectedValue: '15 GiB'},
  {index: 3, name: 'Full Backup', expectedHeading: 'Full Backup:', expectedValue: '5 GiB'}
]

backupStorageRequirementsTests.forEach(function (item) {
  test(backupStorageRequirementsSection + ': Check ' + item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectStandardSizeEICResourceOverview(page);
    await page.click('text=' + backupStorageRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(6) .content div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(6) .content div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});