// Test for the Resource overview page with EBS-M enabled
const { test, expect } = require('@playwright/test');
async function goToDeploymentSetup(page){
  await page.goto('http://localhost:5001/#/');
  await page.goto('http://localhost:5001/#/deploymentsetup');
}

async function selectExtraLargeLoad(page){
  await page.click('text=Please select...');
  await page.getByText('cENM', { exact: true }).click();
  await page.click('text=Please select...');
  await page.click('text=Extra-Large Cloud Native ENM');
  await page.click('text=Please select...');
  await page.click('text=R1ES');
  await page.click('text=Event Based Statistics for MME (EBS-M) Event Based Statistics for MME contains ebs-controller, ebs-flow and ebs-t >> i');
  await page.click('text=Setup Deployment');
}

async function selectExtraLargeLoadOpenResourceOverview(page){
  await selectExtraLargeLoad(page)
}

async function selectExtraLargeLoadOpenWorkloads(page){
  await selectExtraLargeLoad(page)
  await page.click('text=Workloads');
}

// Application Total Requirements Tests
const applicationTotalRequirementsSection = 'Application Total Requirements:'
const applicationTotalRequirementsTests = [
  {index: 1, name: 'CPU Requests', expectedHeading: 'CPU:', expectedValue: 'Requests: 19 vCPU (+ 0.10 vCPU/worker)'},
  {index: 2, name: 'Memory Requests', expectedHeading: 'Memory:', expectedValue: 'Requests: 82 GiB (+ 0.10 GiB/worker)'}
]

applicationTotalRequirementsTests.forEach(function (item) {
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

// Cluster Resource Overview Tests
const clusterResourceOverviewSection = 'K8s Resources Overview:'
const clusterResourceOverviewTests = [
  {index: 1, name: 'Total Pods', expectedValue: 'Total Pods: 25'},
  {index: 2, name: 'Total ConfigMaps', expectedValue: 'Total ConfigMaps: 3'},
  {index: 3, name: 'Total Secrets', expectedValue: 'Total Secrets: 3'},
  {index: 4, name: 'Total Services', expectedValue: 'Total Services: 3'},
  {index: 5, name: 'Total Ingresses', expectedValue: 'Total Ingresses: 5'},
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

// Workloads Tests
test('Check ebs workloads displayed', async ({ page }) => {
  await goToDeploymentSetup(page);
  await selectExtraLargeLoadOpenWorkloads(page);
  const ebscontrollerCount = await page.locator("text=ebscontroller").count();
  expect(ebscontrollerCount).toEqual(1);
  const ebsflowCount = await page.locator("text=ebsflow").count();
  expect(ebsflowCount).toEqual(1);
  const ebsJobCount = await page.locator("text=eric-enm-models-ebs-job").count();
  expect(ebsJobCount).toEqual(1);
});
