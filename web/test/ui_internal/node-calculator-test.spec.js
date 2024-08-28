// Test for the Node Calculator page for XL ENM variant on internal RCD
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
  await page.click('text=21.14.84 (R1ES)');
  await page.click('text=Setup Deployment');
}

async function goToNodeCalculator(page){
  await page.click('text=Node Calculator');
  await expect(page).toHaveURL('http://localhost:5001/#/nodecalc');
}

test('test node calculator set optimal node count checkmark', async ({ page }) => {
  await goToDeploymentSetup(page);
  await selectExtraLargeLoad(page);
  await goToNodeCalculator(page);
  await page.click('text=Set Optimal Node Count');
  await page.click('div:text(" > "):has-text("CPU") i.icon-check');
  await page.click('div:text(" > "):has-text("Memory") i.icon-check');
  await page.click('div:text(" > "):has-text("Disk") i.icon-check');
});

test('test node calculator set optimal node count node failure tolerant message', async ({ page }) => {
  await goToDeploymentSetup(page);
  await selectExtraLargeLoad(page);
  await goToNodeCalculator(page);
  await page.click('text=Set Optimal Node Count')
  await page.click('text=This cluster is 1 node failure tolerant')
});

test('test node calculator simulated app click opens app in workload page', async ({ page }) => {
  await goToDeploymentSetup(page);
  await selectExtraLargeLoad(page);
  await goToNodeCalculator(page);
  await page.click('div.wl:has-text("cmserv")');
  await expect(page).toHaveURL('http://localhost:5001/#/workloads');
  await page.click('tr.highlight:has-text("cmserv")');
});

test('test node calculator number of simulated nodes equals node counter', async ({ page }) => {
  await goToDeploymentSetup(page);
  await selectExtraLargeLoad(page);
  await goToNodeCalculator(page);
  var worker_nodes=1
  do {
    const simulated_worker_nodes = await page.locator('div.node:has-text("Worker")').count();
    await expect(simulated_worker_nodes).toEqual(worker_nodes);
    await page.click('div:nth-child(4) .nirow .controls .icon.icon-chevron-up');
    worker_nodes+=1;
  } while (worker_nodes < 4)
});

test('test node calculator resource available < resource required', async ({ page }) => {
  await goToDeploymentSetup(page);
  await selectExtraLargeLoad(page);
  await goToNodeCalculator(page);
  var resources = ["CPU", "Memory", "Disk"];
  var resource_num = 2;
  do{
    const resource_type = resources[resource_num];
    const resource = await page.innerText('div:text(" > "):has-text("'+resource_type+'")');
    const values = resource.split(" ");
    const available = parseInt(values[1]);
    const required = parseInt(values[3]);
    if (available < required) {
      await page.click('div:text(" > "):has-text("'+resource_type+'") i.icon-triangle-warning');
    }
    else {
      await page.click('div:text(" > "):has-text("'+resource_type+'") i.icon-check');
    }
    resource_num--;
  } while(resource_num > 0)
});


test('test node calculator unschedulable pods displayed with lack of resources', async ({ page }) => {
  await goToDeploymentSetup(page);
  await selectExtraLargeLoad(page);
  await goToNodeCalculator(page);
  await expect(page.locator('div.msg-error')).toBeVisible;
  await expect(page.locator('div.unschedulable')).toBeVisible;
});
