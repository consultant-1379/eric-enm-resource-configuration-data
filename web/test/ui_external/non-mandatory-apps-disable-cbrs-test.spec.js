// Test for the Resource overview page with CBRS disabled
const { test, expect } = require('@playwright/test');
async function goToDeploymentSetup(page) {
  await page.goto('http://localhost:5001/#/');
  await page.goto('http://localhost:5001/#/deploymentsetup');
}

async function selectExtraLargeLoad(page) {
  await page.click('text=Please select...');
  await page.getByText('cENM', { exact: true }).click();
  await page.click('text=Please select...');
  await page.click('text=Extra-Large Cloud Native ENM');
  await page.click('text=Please select...');
  await page.click('text=R1GJ');
  await page.click('text=Please select...');
  await page.click('text=IPv4');
  await page.click('text=CBRS Cell Management >> i');
  await page.click('text=Setup Deployment');
}

async function selectExtraLargeLoadOpenResourceOverview(page) {
  await selectExtraLargeLoad(page)
}

async function selectExtraLargeLoadOpenWorkloads(page) {
  await selectExtraLargeLoad(page)
  await page.click('text=Workloads');
}

// Application Total Requirements Tests
const applicationTotalRequirementsSection = 'Application Total Requirements:'
const applicationTotalRequirementsTests = [
  { index: 1, name: 'CPU Requests', expectedHeading: 'CPU:', expectedValue: 'Requests: 434 vCPU (+ 0.10 vCPU/worker)' },
  { index: 2, name: 'Memory Requests', expectedHeading: 'Memory:', expectedValue: 'Requests: 2996 GiB (+ 0.10 GiB/worker)' }
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
  { index: 1, name: 'Total Pods', expectedValue: 'Total Pods: 486' },
  { index: 2, name: 'Total ConfigMaps', expectedValue: 'Total ConfigMaps: 300' },
  { index: 3, name: 'Total Secrets', expectedValue: 'Total Secrets: 292' },
  { index: 4, name: 'Total Services', expectedValue: 'Total Services: 172' },
  { index: 5, name: 'Total Ingresses', expectedValue: 'Total Ingresses: 52' },
  { index: 6, name: 'Total EricIngresses', expectedValue: 'Total EricIngresses: 27' },
  { index: 7, name: 'Total RWO', expectedValue: 'Total RWO: 41' },
  { index: 8, name: 'Total RWX', expectedValue: 'Total RWX: 35' },
]

clusterResourceOverviewTests.forEach(function (item) {
  test(clusterResourceOverviewSection + ': Check ' + item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceOverview(page);
    await page.click('text=' + clusterResourceOverviewSection);
    const value = await page.innerText('.row div:nth-child(9) .content div:nth-child(' + item.index + ') .val');
    expect(value).toEqual(item.expectedValue);
  });
});

//Workloads Tests
test('Check dc-history and domainproxy not displayed', async ({ page }) => {
  await goToDeploymentSetup(page);
  await selectExtraLargeLoadOpenWorkloads(page);
  const domainproxyCount = await page.locator("text=domainproxy").count();
  expect(domainproxyCount).toEqual(0);
  const dchistoryCount = await page.locator("text=dc-history").count();
  expect(dchistoryCount).toEqual(0);
});