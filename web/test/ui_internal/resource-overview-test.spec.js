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
  await page.click('text=22.12.84 (R1EX)');
}

// Jobs Total Requirements Tests
const jobsTotalRequirementsSection = 'Jobs Total Requirements:'
const jobsTotalRequirementsTests = [
  {index: 1, name: 'CPU total', expectedHeading: 'CPU:', expectedValue: '1 vCPU'},
  {index: 2, name: 'Memory total', expectedHeading: 'Memory:', expectedValue: '1 GiB'}
]

jobsTotalRequirementsTests.forEach(function (item) {
  test(jobsTotalRequirementsSection + ': Check ' + item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceOverview(page);
    await page.click('text=Please select...');
    await page.click('text=IPv6 EXT');
    await page.click('text=Setup Deployment');
    await page.click('text=' + jobsTotalRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(2) div:nth-child(4) div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(2) div:nth-child(4) div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});

// Ipv6 - Other Requirements Tests
const otherRequirementsSection = 'Networking Requirements:'
const otherRequirementsIPv6Tests = [
  {index: 1, name: 'Site Specific IPv6 Addresses', expectedHeading: 'IP Address Requirements:', expectedValue: 'Site Specific IPv6 Addresses: 3'}
]

otherRequirementsIPv6Tests.forEach(function (item) {
  test(otherRequirementsSection + ': Check ' +  item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceOverview(page);
    await page.click('text=Please select...');
    await page.click('text=IPv6 EXT');
    await page.click('text=Setup Deployment');
    await page.click('text=' + otherRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(9) div:nth-child(2) div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row div:nth-child(9) div:nth-child(2) div:nth-child(' + item.index + ') .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});

const otherRequirementsDualTests = [
  {index: 2, name: 'Dualstack: Site Specific IPv4 Addresses', expectedHeading: 'IP Address Requirements:', expectedValue: 'Site Specific IPv4 Addresses: 3'},
  {index: 3, name: 'Dualstack: Site Specific IPv6 Addresses', expectedHeading: 'IP Address Requirements:', expectedValue: 'Site Specific IPv6 Addresses: 3'}
]

otherRequirementsDualTests.forEach(function (item) {
  test(otherRequirementsSection + ': Check ' +  item.name, async ({ page }) => {
    await goToDeploymentSetup(page);
    await selectExtraLargeLoadOpenResourceOverview(page);
    await page.click('text=Please select...');
    await page.click('text=Dual Stack');
    await page.click('text=Setup Deployment');
    await page.click('text=' + otherRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(9) div:nth-child(2) div:nth-child(1) .tooltip');
    const value = await page.innerText('.row div:nth-child(9) div:nth-child(2) div:nth-child(1) div:nth-child(' + item.index + ')');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toEqual(item.expectedValue);
  });
});