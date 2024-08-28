// Test for the Node Calculator page for XL ENM variant on internal RCD
const { test, expect } = require('@playwright/test');
async function goToDeploymentSetup(page){
  await page.goto('http://localhost:5001/#/');
  await page.goto('http://localhost:5001/#/deploymentsetup');
}

async function selectFilter(page, sgToSearch){
  await page.click('button');
  await page.click('input[type="text"]');
  await page.fill('input[type="text"]', sgToSearch);
  await page.click('text=Apply');
}

async function selectSmallLoad(page){
  await page.click('text=Please select...');
  await page.getByText('cENM', { exact: true }).click();
  await page.click('text=Please select...');
  await page.click('text=Small Cloud Native ENM');
  await page.click('text=Please select...');
  await page.click('text=21.14.84 (R1ES)');
  await page.click('text=Setup Deployment');
  await expect(page).toHaveURL('http://localhost:5001/#/overview');
}

async function selectExtraLoad(page){
    await page.click('text=Please select...');
    await page.getByText('cENM', { exact: true }).click();
    await page.click('text=Please select...');
    await page.click('text=Extra-Large Cloud Native ENM');
    await page.click('text=Please select...');
    await page.click('text=21.14.84 (R1ES)');
    await page.click('text=Setup Deployment');
    await expect(page).toHaveURL('http://localhost:5001/#/overview');
}

async function goToWorkloadValidator(page){
  await page.click('text=Workload Validator');
  await expect(page).toHaveURL('http://localhost:5001/#/workloadconfigvalid');
}

test('test WorkloadValidator With Validation Errors', async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectSmallLoad(page);
    await goToWorkloadValidator(page);
    await selectFilter(page, 'remotewriter')
    const locator = page.locator("text=remotewriter");
    await expect(locator).toBeVisible();
  });

  test('test WorkloadValidator Without Validation Errors', async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLoad(page);
    await goToWorkloadValidator(page);
    const locator = page.locator("text=No validation issues found for product set: 21.14.84 (R1ES)");
    await expect(locator).toBeVisible();
  });

