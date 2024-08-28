// Test for the Compare enm versions page
const { test, expect } = require('@playwright/test');

async function goToCompare(page){
  await page.goto('http://localhost:5001/#/');
  await page.goto('http://localhost:5001/#/compare');
}

async function selectSmallEnm(page){
  await page.click('text=Please select...');
  await page.locator('text=Small Cloud Native ENM').click();
}

async function selectEnmReleasesWithPositiveDifference(page){
  await page.locator('text=Please select...').first().click();
  await page.locator('text=R1ER').first().click();
  await page.locator('text=Please select...').click();
  await page.locator('text=R1ES').first().click();
  await page.locator('button:has-text("Compare Releases")').click();
}

async function selectEnmReleasesWithPositiveDifferenceWithIPv6Version(page){
  await page.locator('text=Please select...').first().click();
  await page.locator('text=R1EX').first().click();
  await page.locator('text=Please select...').click();
  await page.locator('text=R1EP').nth(1).click();
  await page.locator('text=Please select...').click();
  await page.locator('text=IPv6 EXT').first().click();
  await page.locator('button:has-text("Compare Releases")').click();
}

const applicationTotalRequirementsSection = 'Application Total Requirements:'
const applicationTotalRequirementsTests = [
  {index: 1, name: 'CPU total', expectedHeading: 'CPU: ', expectedDelta: "+11 vCPU"},
  {index: 2, name: 'Memory total', expectedHeading: 'Memory: ', expectedDelta: "+1 GiB"}
]

applicationTotalRequirementsTests.forEach(function (item) {
  test(applicationTotalRequirementsSection + ' Check for plus value at ' + item.name, async ({ page }) => {
    await goToCompare(page);
    await selectSmallEnm(page);
    await selectEnmReleasesWithPositiveDifference(page);
    await page.click('text=' + applicationTotalRequirementsSection);
    const heading = await page.innerText('.row .row:nth-child(1) div:nth-child(2) .content div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row .row:nth-child(1) div:nth-child(2) .content > :nth-child(' + item.index + ') .val');
    expect(heading).toEqual(item.expectedHeading);
    expect(value).toContain(item.expectedDelta);
  });
});

const persistentStorageRequirementsSection = 'Storage Requirements:'
const persistentStorageRequirementsTests = [
  {index: 1, name: 'RWO', expectedHeading: 'RWO (ReadWriteOnce):', expectedDelta: "-25 GiB"},
  {index: 2, name: 'RWX', expectedHeading: 'RWX (ReadWriteMany):', expectedDelta: "-20 GiB"},
  {index: 3, name: 'Ephemeral Storage:', expectedHeading: 'Ephemeral Storage:', expectedDelta: "+8001 GiB"}
]

persistentStorageRequirementsTests.forEach(function (item) {
  test(persistentStorageRequirementsSection + ': Check ' + item.name, async ({ page }) => {
    await goToCompare(page);
    await selectSmallEnm(page);
    await selectEnmReleasesWithPositiveDifference(page);
    await page.click('text=' + persistentStorageRequirementsSection);
    const heading = await page.innerText('.row .row:nth-child(2) div:nth-child(3) .content div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row .row:nth-child(2) div:nth-child(3) .content div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toContain(item.expectedDelta)
  });
});

const estimatedStoragerequirments = 'Estimated Storage Requirements For Backups:'
const estimatedStoragerequirmentsTests = [
  {index: 1, name: 'BRO PVC Storage', expectedHeading: 'BRO PVC Storage:', expectedDelta: "-1 GiB"},
  {index: 2, name: 'External Backup Storage', expectedHeading: 'External Backup Storage (SFTP):', expectedDelta: "-1 GiB"}
];

estimatedStoragerequirmentsTests.forEach(function (item) {
  test(estimatedStoragerequirments + ': Check ' + item.name, async ({ page }) => {
    await goToCompare(page);
    await selectSmallEnm(page);
    await selectEnmReleasesWithPositiveDifference(page);
    await page.click('text=' + estimatedStoragerequirments);
    const heading = await page.innerText('.row .row:nth-child(2) div:nth-child(4) .content div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row .row:nth-child(2) div:nth-child(4) .content div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toContain(item.expectedDelta)
  });
});

const estimatedBackupsizes = 'Estimated Backup Sizes:'
const estimatedBackupsizesTests = [
  {index: 1, name: 'Full Backup', expectedHeading: 'Full Backup:', expectedDelta: "-100 GiB (-1 GiB Uncompressed)"},
  {index: 2, name: 'Pre-Upgrade Backup', expectedHeading: 'Pre-Upgrade Backup:', expectedDelta: "-1 GiB (-2 GiB Uncompressed)"}
];

estimatedBackupsizesTests.forEach(function (item) {
  test(estimatedBackupsizes + ': Check ' + item.name, async ({ page }) => {
    await goToCompare(page);
    await selectSmallEnm(page);
    await selectEnmReleasesWithPositiveDifference(page);
    await page.click('text=' + estimatedBackupsizes);
    const heading = await page.innerText('div:nth-child(4) div:nth-child(4) div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('div:nth-child(4) div:nth-child(4) div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toContain(item.expectedDelta)
  });
});

const containerRegistryRequirementsSection = 'Container Registry Requirements:'
const containerRegistryRequirementsTests = [
  {index: 1, name: 'Disk storage space', expectedHeading: 'Disk storage space:', expectedDelta: "200 GiB"},
  {index: 2, name: 'Ports', expectedHeading: 'Ports:', expectedDelta: "80, 443"}
]

containerRegistryRequirementsTests.forEach(function (item) {
  test(containerRegistryRequirementsSection + ': Check ' +  item.name, async ({ page }) => {
    await goToCompare(page);
    await selectSmallEnm(page);
    await selectEnmReleasesWithPositiveDifference(page);
    await page.click('text=' + containerRegistryRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(6) .content div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(6) .content div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toContain(item.expectedDelta)
  });
});

const clientResourceRequirementsSection = 'Client Resource Requirements:'
const clientResourceRequirementsTests = [
  {index: 1, name: 'Ports', expectedHeading: 'Ports:',  expectedDelta: "7001"},
  {index: 2, name: 'CPU', expectedHeading: 'CPU:', expectedDelta: "2vCPU"},
  {index: 3, name: 'Memory', expectedHeading: 'Memory:', expectedDelta: "8 GiB"},
  {index: 4, name: 'Storage', expectedHeading: 'Storage:', expectedDelta: "200 GiB"}
]

clientResourceRequirementsTests.forEach(function (item) {
  test(clientResourceRequirementsSection + ': Check ' +  item.name, async ({ page }) => {
    await goToCompare(page);
    await selectSmallEnm(page);
    await selectEnmReleasesWithPositiveDifference(page);
    await page.click('text=' + clientResourceRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(7) .content div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(7) .content div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toContain(item.expectedDelta)
  });
});

const softwareRequirementsSection = 'Software Requirements:'
const clientSoftwareRequirementsTests = [
  {index: 2, name: 'Client Docker version', expectedHeading: 'Client:', expectedDelta: "20.10.6-ce"},
  {index: 3, name: 'Client Helm version', expectedHeading: 'Client:', expectedDelta: "3.6.0"},
  {index: 4, name: 'Client Kubectl version', expectedHeading: 'Client:', expectedDelta: "1.21.1"},
  {index: 5, name: 'Client Python version', expectedHeading: 'Client:', expectedDelta: "3.6"},
  {index: 6, name: 'Client Screen', expectedHeading: 'Client:', expectedDelta: "Screen"},
  {index: 7, name: 'Client Unzip', expectedHeading: 'Client:', expectedDelta: "Unzip"}
];

clientSoftwareRequirementsTests.forEach(function (item) {
  test(softwareRequirementsSection + ': Check ' + item.name, async ({ page }) => {
    await goToCompare(page);
    await selectSmallEnm(page);
    await selectEnmReleasesWithPositiveDifference(page);
    await page.click('text=' + softwareRequirementsSection);
    const heading = await page.innerText('div:nth-child(8) div:nth-child(2) div:nth-child(1) .tooltip');
    const value = await page.innerText('div:nth-child(8) div:nth-child(2) div:nth-child(1) div:nth-child(' + item.index + ')');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toContain(item.expectedDelta)
  });
});

const clusterSoftwareRequirementsTests = [
  {index: 2, name: 'Cluster Kubernetes version', expectedHeading: 'Cluster:', expectedDelta: "1.22.1"}
];

clusterSoftwareRequirementsTests.forEach(function (item) {
  test(softwareRequirementsSection + ': Check ' + item.name, async ({ page }) => {
    await goToCompare(page);
    await selectSmallEnm(page);
    await selectEnmReleasesWithPositiveDifference(page);
    await page.click('text=' + softwareRequirementsSection);
    const heading = await page.innerText('div:nth-child(8) div:nth-child(2) div:nth-child(2) .tooltip');
    const value = await page.innerText('div:nth-child(8) div:nth-child(2) div:nth-child(2) div:nth-child(' + item.index + ')');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toContain(item.expectedDelta);
  });
});

const networkingRequirementsSection = 'Networking Requirements:'
const networkingRequirementsTests = [
  {index: 1, name: 'Site Specific IPv4 Addresses', expectedHeading: 'IP Address Requirements:', expectedDelta: "-2"},
]

networkingRequirementsTests.forEach(function (item) {
  test(networkingRequirementsSection + ': Check ' +  item.name, async ({ page }) => {
    await goToCompare(page);
    await selectSmallEnm(page);
    await selectEnmReleasesWithPositiveDifference(page);
    await page.click('text=' + networkingRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(9) div:nth-child(2) div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(9) div:nth-child(2) div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toContain(item.expectedDelta);
  });
});

networkingRequirementsTests.forEach(function (item) {
  test(networkingRequirementsSection + ': Check Multiple compare release button presses' +  item.name, async ({ page }) => {
    await goToCompare(page);
    await selectSmallEnm(page);
    await selectEnmReleasesWithPositiveDifference(page);
    await page.locator('button:has-text("Compare Releases")').click();
    await page.click('text=' + networkingRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(9) div:nth-child(2) div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(9) div:nth-child(2) div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toContain(item.expectedDelta);
  });
});

const networkingRequirementsIPv6Section = 'Networking Requirements:'
const networkingRequirementsIPv6Tests = [
  {index: 1, name: 'Site Specific IPv6 Addresses', expectedHeading: 'IP Address Requirements:', expectedDelta: "+1"},
]

networkingRequirementsIPv6Tests.forEach(function (item) {
  test(networkingRequirementsIPv6Section + ': Check ' +  item.name, async ({ page }) => {
    await goToCompare(page);
    await selectSmallEnm(page);
    await selectEnmReleasesWithPositiveDifferenceWithIPv6Version(page);
    await page.click('text=' + networkingRequirementsIPv6Section);
    const heading = await page.innerText('.row div:nth-child(9) div:nth-child(2) div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(9) div:nth-child(2) div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toContain(item.expectedDelta);
  });
});

const otherRequirementsSection = 'Other Requirements:'
const otherRequirementsTests = [
  {index: 1, name: 'PIDs', expectedHeading: 'PIDs:', expectedDelta: "-1"}
]

otherRequirementsTests.forEach(function (item) {
  test(otherRequirementsSection + ': Check ' +  item.name, async ({ page }) => {
    await goToCompare(page);
    await selectSmallEnm(page);
    await selectEnmReleasesWithPositiveDifference(page);
    await page.click('text=' + otherRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(9) div:nth-child(4) div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(9) div:nth-child(4) div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toContain(item.expectedDelta);
  });
});

otherRequirementsTests.forEach(function (item) {
  test(otherRequirementsSection + ': Check Multiple compare release button presses' +  item.name, async ({ page }) => {
    await goToCompare(page);
    await selectSmallEnm(page);
    await selectEnmReleasesWithPositiveDifference(page);
    await page.locator('button:has-text("Compare Releases")').click();
    await page.click('text=' + otherRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(9) div:nth-child(4) div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(9) div:nth-child(4) div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toContain(item.expectedDelta);
  });
});

const clusterResourceOverviewSection = 'K8s Resources Overview:'
const clusterResourceOverviewTests = [
  {index: 1, name: 'Total Pods', expectedDelta: "+1"},
  {index: 2, name: 'Total ConfigMaps', expectedDelta: "+1"},
  {index: 3, name: 'Total Secrets', expectedDelta: "+1"},
  {index: 4, name: 'Total Services', expectedDelta: "+1"},
  {index: 5, name: 'Total Ingresses', expectedDelta: "-1"},
  {index: 6, name: 'Total EricIngresses', expectedDelta: "-1"},
  {index: 7, name: 'Total RWO', expectedDelta: "-1"},
  {index: 8, name: 'Total RWX', expectedDelta: "-1"},
]

clusterResourceOverviewTests.forEach(function (item) {
  test(clusterResourceOverviewSection + ': Check plus value for ' +  item.name, async ({ page }) => {
    await goToCompare(page);
    await selectSmallEnm(page);
    await selectEnmReleasesWithPositiveDifference(page);
    await page.click('text=' + clusterResourceOverviewSection);
    const value = await page.innerText('.row div:nth-child(10) .content div:nth-child(' + item.index + ') .val');
    expect(value).toContain(item.expectedDelta);
  });
});

const clusterResourceOverviewIPv6Section = 'K8s Resources Overview:'
const clusterResourceOverviewIPv6Tests = [
  {index: 4, name: 'IPv6: Total Services', expectedDelta: "+1"},
  {index: 6, name: 'IPv6: Total EricIngresses', expectedDelta: "+1"},
]

clusterResourceOverviewIPv6Tests.forEach(function (item) {
  test(clusterResourceOverviewIPv6Section + ': Check plus value for ' +  item.name, async ({ page }) => {
    await goToCompare(page);
    await selectSmallEnm(page);
    await selectEnmReleasesWithPositiveDifferenceWithIPv6Version(page);
    await page.click('text=' + clusterResourceOverviewIPv6Section);
    const value = await page.innerText('.row div:nth-child(10) .content div:nth-child(' + item.index + ') .val');
    expect(value).toContain(item.expectedDelta);
  });
});