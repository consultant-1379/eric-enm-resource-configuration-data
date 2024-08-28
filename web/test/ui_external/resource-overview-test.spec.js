// Test for the Resource overview page with no optional apps enabled
const { test, expect } = require('@playwright/test');
async function goToDeploymentSetup(page){
  await page.goto('http://localhost:5001/#/');
  await page.goto('http://localhost:5001/#/deploymentsetup');
}

async function selectExtraLargeLoadOpenResourceOverview(page){
  await page.click('text=Please select...');
  await page.getByText('cENM', { exact: true }).click();
  await page.click('text=Please select...');
  await page.click('text=Extra-Large Cloud Native ENM');
  await page.click('text=Please select...');
  await page.click('text=R1ES');
  await page.click('text=Setup Deployment');
}

async function selectExtraLargeLoadOpenResourceOverviewNoSoftwareRequirements(page){
  await page.click('text=Please select...');
  await page.getByText('cENM', { exact: true }).click();
  await page.click('text=Please select...');
  await page.click('text=Extra-Large Cloud Native ENM');
  await page.click('text=Please select...');
  await page.click('text=R1EQ');
  await page.click('text=Please select...');
  await page.click('text=IPv4');
  await page.click('text=Setup Deployment');
}

async function selectExtraLargeLoadOpenResourceWithIpVersionsOverview(page){
  await page.click('text=Please select...');
  await page.getByText('cENM', { exact: true }).click();
  await page.click('text=Please select...');
  await page.click('text=Extra-Large Cloud Native ENM');
  await page.click('text=Please select...');
  await page.click('text=R1EQ');
  await page.click('text=Please select...');
  await page.click('text=IPv6 EXT');
  await page.click('text=Setup Deployment');
}

/// Cluster Recommendation Tests
 const clusterRecommendationSection = 'Cluster Recommendation:'
 const clusterRecommendationTests = [
   {index: 1, name: 'CPU Recommendation', expectedHeading: 'CPU:', expectedValue: 'CPU: 18 vCPU (+ 0.11 vCPU/worker)'},
   {index: 2, name: 'Memory Recommendation', expectedHeading: 'Memory:', expectedValue: 'Memory: 94.00 GiB (+ 0.17 GiB/worker)'}
 ]

 clusterRecommendationTests.forEach(function (item) {
   test(clusterRecommendationSection + ': Check ' + item.name, async ({ page }) => {
     await goToDeploymentSetup(page);
     await selectExtraLargeLoadOpenResourceOverviewNoSoftwareRequirements(page);
     await page.click('text=' + applicationTotalRequirementsSection);
     const heading = await page.innerText('.row div:nth-child(1) .content div:nth-child(' + item.index + ') .tooltip');
     const value = await page.innerText('.row div:nth-child(1) .content > :nth-child(' + item.index + ') .val');
     expect(heading).toContain(item.expectedHeading);
     expect(value).toEqual(item.expectedValue);
   });
 });

// Application Total Requirements Tests
const applicationTotalRequirementsSection = 'Application Total Requirements:'
const applicationTotalRequirementsRequestsTests = [
  {index: 1, name: 'CPU Requests', expectedHeading: 'CPU:', expectedValue: 'Requests: 16 vCPU (+ 0.10 vCPU/worker)'},
  {index: 2, name: 'Memory Requests', expectedHeading: 'Memory:', expectedValue: 'Requests: 67 GiB (+ 0.10 GiB/worker)'}
]

applicationTotalRequirementsRequestsTests.forEach(function (item) {
  test(applicationTotalRequirementsSection + ': Check ' + item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceOverview(page);
    await page.click('text=' + applicationTotalRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(2) .content div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(2) .content > :nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});

const applicationTotalRequirementsLimitsTests = [
  {index: 1, name: 'CPU Limits', expectedHeading: 'CPU:', expectedValue: 'Limits: 49 vCPU (+ 0.20 vCPU/worker)'},
  {index: 2, name: 'Memory Limits', expectedHeading: 'Memory:', expectedValue: 'Limits: 82 GiB (+ 0.15 GiB/worker)'}
]

applicationTotalRequirementsLimitsTests.forEach(function (item) {
  test(applicationTotalRequirementsSection + ': Check ' + item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceOverview(page);
    await page.click('text=' + applicationTotalRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(2) .content div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(2) .content > :nth-child(' + item.index + ') > :nth-child(3)');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});

// Storage Requirements Tests
const persistentStorageRequirementsSection = 'Storage Requirements:'
const persistentStorageRequirementsTests = [
  {index: 1, name: 'RWO', expectedHeading: 'RWO (ReadWriteOnce):', expectedValue: '31 GiB'},
  {index: 2, name: 'RWX', expectedHeading: 'RWX (ReadWriteMany):', expectedValue: '70 GiB'},
  {index: 3, name: 'Ephemeral Storage:', expectedHeading: 'Ephemeral Storage:', expectedValue: '3 GiB (+ 0 GiB/worker)'}
]

persistentStorageRequirementsTests.forEach(function (item) {
  test(persistentStorageRequirementsSection + ': Check ' + item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceOverview(page);
    await page.click('text=' + persistentStorageRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(3) .content div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(3) .content div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});

const estimatedStoragerequirments = 'Estimated Storage Requirements For Backups:'
const estimatedStoragerequirmentsTests = [
  {index: 1, name: 'BRO PVC Storage', expectedHeading: 'BRO PVC Storage:', expectedValue: '3541 GiB'},
  {index: 2, name: 'External Backup Storage', expectedHeading: 'External Backup Storage (SFTP):', expectedValue: '6396 GiB'}
];

estimatedStoragerequirmentsTests.forEach(function (item) {
  test(estimatedStoragerequirments + ': Check ' + item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceOverview(page);
    await page.click('text=' + estimatedStoragerequirments);
    const heading = await page.innerText('div:nth-child(4) div:nth-child(2) div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('div:nth-child(4) div:nth-child(2) div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});

const estimatedBackupsizes = 'Estimated Backup Sizes:'
const estimatedBackupsizesTests = [
  {index: 1, name: 'Full Backup', expectedHeading: 'Full Backup:', expectedValue: '1599 GiB (3198 GiB Uncompressed)'},
  {index: 2, name: 'Pre-Upgrade Backup', expectedHeading: 'Pre-Upgrade Backup:', expectedValue: '343 GiB (686 GiB Uncompressed)'}
];

estimatedBackupsizesTests.forEach(function (item) {
  test(estimatedBackupsizes + ': Check ' + item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceOverview(page);
    await page.click('text=' + estimatedBackupsizes);
    const heading = await page.innerText('div:nth-child(4) div:nth-child(4) div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('div:nth-child(4) div:nth-child(4) div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});

// ENM Application Worker Node Requirements Tests
const workerNodeRequirementsSection = 'Application Worker Node Requirements:';
const workerNodeRequirementsTests = [
  {index: 1, name: 'Minimum number of worker nodes', expectedHeading: 'Minimum number of Worker Nodes:', expectedValue: '8'},
  {index: 2, name: 'Minimum recommended worker node CPU', expectedHeading: 'Minimum required worker node CPU:', expectedValue: '5 vCPU'},
  {index: 3, name: 'Minimum recommended worker node memory', expectedHeading: 'Minimum required worker node Memory:', expectedValue: '11 GiB'},
  {index: 4, name: 'Minimum recommended worker node Disk', expectedHeading: 'Minimum required worker node Disk:', expectedValue: '1 GiB'}
];

workerNodeRequirementsTests.forEach(function (item) {
  test(workerNodeRequirementsSection + ': ' + item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceOverview(page);
    await page.click('text=' + workerNodeRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(5) .content div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(5) .content div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});


// Container Registry Requirements Tests
const containerRegistryRequirementsSection = 'Container Registry Requirements:'
const containerRegistryRequirementsTests = [
  {index: 1, name: 'Disk storage space', expectedHeading: 'Disk storage space:', expectedValue: '200 GiB'},
  {index: 2, name: 'Ports', expectedHeading: 'Ports:', expectedValue: '80, 443'}
]

containerRegistryRequirementsTests.forEach(function (item) {
  test(containerRegistryRequirementsSection + ': Check ' +  item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceOverview(page);
    await page.click('text=' + containerRegistryRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(6) .content div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(6) .content div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});


// Client Resource Requirements Tests
const clientResourceRequirementsSection = 'Client Resource Requirements:'
const clientResourceRequirementsTests = [
  {index: 1, name: 'Ports', expectedHeading: 'Ports:',  expectedValue: '7001'},
  {index: 2, name: 'CPU', expectedHeading: 'CPU:', expectedValue: '2vCPU'},
  {index: 3, name: 'Memory', expectedHeading: 'Memory:', expectedValue: '8 GiB'},
  {index: 4, name: 'Storage', expectedHeading: 'Storage:', expectedValue: '200 GiB'}
]

clientResourceRequirementsTests.forEach(function (item) {
  test(clientResourceRequirementsSection + ': Check ' +  item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceOverview(page);
    await page.click('text=' + clientResourceRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(7) .content div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(7) .content div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});


// Software Requirements Tests
const softwareRequirementsSection = 'Software Requirements:'
const clientSoftwareRequirementsTests = [
  {index: 2, name: 'Client Docker version', expectedHeading: 'Client:', expectedValue: 'Docker version: 20.10.6-ce'},
  {index: 3, name: 'Client Helm version', expectedHeading: 'Client:', expectedValue: 'Helm version: 3.6.0'},
  {index: 4, name: 'Client Kubectl version', expectedHeading: 'Client:', expectedValue: 'Kubectl version: 1.21.1'},
  {index: 5, name: 'Client Python version', expectedHeading: 'Client:', expectedValue: 'Python version: 3.6'},
  {index: 6, name: 'Client Screen', expectedHeading: 'Client:', expectedValue: 'Screen'},
  {index: 7, name: 'Client Unzip', expectedHeading: 'Client:', expectedValue: 'Unzip'},
];

clientSoftwareRequirementsTests.forEach(function (item) {
  test(softwareRequirementsSection + ': Check ' + item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceOverview(page);
    await page.click('text=' + softwareRequirementsSection);
    const heading = await page.innerText('div:nth-child(8) div:nth-child(2) div:nth-child(1) .tooltip');
    const value = await page.innerText('div:nth-child(8) div:nth-child(2) div:nth-child(1) div:nth-child(' + item.index + ')');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});

const clusterSoftwareRequirementsTests = [
  {index: 2, name: 'Cluster Kubernetes version', expectedHeading: 'Cluster:', expectedValue: 'Kubernetes version: 1.21.1'}
];

clusterSoftwareRequirementsTests.forEach(function (item) {
  test(softwareRequirementsSection + ': Check ' + item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceOverview(page);
    await page.click('text=' + softwareRequirementsSection);
    const heading = await page.innerText('div:nth-child(8) div:nth-child(2) div:nth-child(2) .tooltip');
    const value = await page.innerText('div:nth-child(8) div:nth-child(2) div:nth-child(2) div:nth-child(' + item.index + ')');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});

// Other Requirements Tests
const networkingRequirementsSection = 'Networking Requirements:'
const networkingRequirementsTests = [
  {index: 1, name: 'Site Specific IPv4 Addresses', expectedHeading: 'IP Address Requirements:', expectedValue: 'Site Specific IPv4 Addresses: 3'},
]

networkingRequirementsTests.forEach(function (item) {
  test(networkingRequirementsSection + ': Check ' +  item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceOverview(page);
    await page.click('text=' + networkingRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(9) div:nth-child(2) div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(9) div:nth-child(2) div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});

const networkingRequirementsIPv6Section = 'Networking Requirements:'
const networkingRequirementsIPv6Tests = [
  {index: 1, name: 'Site Specific IPv6 Addresses', expectedHeading: 'IP Address Requirements:', expectedValue: 'Site Specific IPv6 Addresses: 3'},
]

networkingRequirementsIPv6Tests.forEach(function (item) {
  test(networkingRequirementsIPv6Section + ': Check ' +  item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceWithIpVersionsOverview(page);
    await page.click('text=' + networkingRequirementsIPv6Section);
    const heading = await page.innerText('.row div:nth-child(8) div:nth-child(2) div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(8) div:nth-child(2) div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});

networkingRequirementsTests.forEach(function (item) {
  test(softwareRequirementsSection + ': Not Present ', async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceOverviewNoSoftwareRequirements(page);
    await page.click('text=' + networkingRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(8) div:nth-child(2) div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(8) div:nth-child(2) div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});

const otherRequirementsSection = 'Other Requirements:'
const otherRequirementsTests = [
  {index: 1, name: 'PIDs', expectedHeading: 'PIDs:', expectedValue: '10240'}
]

otherRequirementsTests.forEach(function (item) {
  test(otherRequirementsSection + ': Check ' +  item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceOverview(page);
    await page.click('text=' + otherRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(9) div:nth-child(4) div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(9) div:nth-child(4) div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});

// Cluster Resource Overview Tests
const clusterResourceOverviewSection = 'K8s Resources Overview:'
const clusterResourceOverviewTests = [
  {index: 1, name: 'Total Pods', expectedValue: 'Total Pods: 20'},
  {index: 2, name: 'Total ConfigMaps', expectedValue: 'Total ConfigMaps: 3'},
  {index: 3, name: 'Total Secrets', expectedValue: 'Total Secrets: 3'},
  {index: 4, name: 'Total Services', expectedValue: 'Total Services: 3'},
  {index: 5, name: 'Total Ingresses', expectedValue: 'Total Ingresses: 4'},
  {index: 6, name: 'Total EricIngresses', expectedValue: 'Total EricIngresses: 3'},
  {index: 7, name: 'Total RWO', expectedValue: 'Total RWO: 4'},
  {index: 8, name: 'Total RWX', expectedValue: 'Total RWX: 2'},
]

clusterResourceOverviewTests.forEach(function (item) {
  test(clusterResourceOverviewSection + ': Check ' +  item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceOverview(page);
    await page.click('text=' + clusterResourceOverviewSection);
    const value = await page.innerText('.row div:nth-child(10) .content div:nth-child(' + item.index + ') .val');
    expect(value).toEqual(item.expectedValue);
  });
});

const clusterResourceIPv6OverviewSection = 'K8s Resources Overview:'
const clusterResourceIPv6OverviewTests = [
  {index: 4, name: 'IPv6: Total Services', expectedValue: 'Total Services: 3'},
  {index: 6, name: 'IPv6: Total EricIngresses', expectedValue: 'Total EricIngresses: 1'}
]

clusterResourceIPv6OverviewTests.forEach(function (item) {
  test(clusterResourceIPv6OverviewSection + ': Check ' +  item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceWithIpVersionsOverview(page);
    await page.click('text=' + clusterResourceIPv6OverviewSection);
    const value = await page.innerText('.row div:nth-child(9) .content div:nth-child(' + item.index + ') .val');
    expect(value).toEqual(item.expectedValue);
  });
});