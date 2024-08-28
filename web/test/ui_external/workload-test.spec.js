// Test for the Workloads page with no optional apps enabled
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
  await page.click('text=Setup Deployment');
}

async function goToWorkloads(page){
  await page.click('text=Workloads');
  await expect(page).toHaveURL('http://localhost:5001/#/workloads');
}

async function selectFilter(page, sgToSearch){
  await page.click('button');
  await page.click('input[type="text"]');
  await page.fill('input[type="text"]', sgToSearch);
  await page.click('text=Apply');
}

test('check cmserv workload resources', async ({ page }) => {
  await goToDeploymentSetup(page);
  await selectExtraLargeLoad(page);
  await goToWorkloads(page);
  await page.click('text=cmserv');
  const result = await page.innerText('tr:below(:text("cmserv"))');
  var resultToBe = 'Affinity Rule\nhard pod anti affinity: {\'app\': \'cmserv\'}\nUpdate Strategy\n{ "rollingUpdate": { "maxSurge": 0, "maxUnavailable": 1 }, "type": "RollingUpdate" }\nPod Disruption Budget\n{ "type": "maxUnavailable", "value": 1 }\nContainer Name\tImage\tCPU Requests\tCPU Limits\tMemory Requests\tMemory Limits\ncmserv\teric-enmsg-cmservice:1.15.0-30\t1200 m\t4000 m\t6144 MiB\t6144 MiB\ncmserv-monitoring\teric-enm-monitoring-eap7:1.15.0-28\t50 m\t200 m\t200 MiB\t300 MiB\ncmserv-httpd\teric-enmsg-cmservice-httpd:1.15.0-30\t250 m\t500 m\t400 MiB\t1000 MiB\n';
  await expect(result).toEqual(resultToBe);
});


test('check expand all functionality in workload resources', async ({ page }) => {
  await goToDeploymentSetup(page);
  await selectExtraLargeLoad(page);
  await goToWorkloads(page);
  await page.click('text=Expand All');
  const x = await page.locator("text=Container Name").count();
  await expect(x).toBeGreaterThan(0n)
});


test('check collapse all functionality in workload resources', async ({ page }) => {
  await goToDeploymentSetup(page);
  await selectExtraLargeLoad(page);
  await goToWorkloads(page);
  expect(page.url()).toBe('http://localhost:5001/#/workloads');
  await page.click('text=Collapse All');
  const locator = page.locator("text=Container Name");
  await expect(locator).toBeHidden();
});


test('test filter', async ({ page }) => {
  await goToDeploymentSetup(page);
  await selectExtraLargeLoad(page);
  await goToWorkloads(page);
  await selectFilter(page, 'lcmserv')
  const locator = page.locator("text=lcmserv");
  await expect(locator).toBeVisible();
});

test('test filter no results found', async ({ page }) => {
  await goToDeploymentSetup(page);
  await selectExtraLargeLoad(page);
  await goToWorkloads(page);
  await selectFilter(page, 'deliverance')
  const deliverance_locate = page.locator("text=deliverance");
  await expect(deliverance_locate).toBeHidden();
});

test('check workload record with pdb and affinity rule is na', async ({ page }) => {
  await goToDeploymentSetup(page);
  await selectExtraLargeLoad(page);
  await goToWorkloads(page);
  await page.click('text=eric-pm-node-exporter');
  const result = await page.innerText('tr:below(:text("eric-pm-node-exporter"))');
  await expect(result.split('N/A').length-1).toEqual(2);
});

test('Check ebs optional workloads not displayed', async ({ page }) => {
  await goToDeploymentSetup(page);
  await selectExtraLargeLoad(page);
  await goToWorkloads(page);
  const ebscontrollerCount = await page.locator("text=ebscontroller").count();
  expect(ebscontrollerCount).toEqual(0);
  const ebsflowCount = await page.locator("text=ebsflow").count();
  expect(ebsflowCount).toEqual(0);
  const ebstopologyCount = await page.locator("text=ebstopology").count();
  expect(ebstopologyCount).toEqual(0);
  const ebsJobCount = await page.locator("text=eric-enm-models-ebs-job").count();
  expect(ebsJobCount).toEqual(0);
});
