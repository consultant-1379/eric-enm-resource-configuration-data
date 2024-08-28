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
  await page.locator('text=22.12.84 (R1EX)').first().click();
  await page.locator('text=Please select...').click();
  await page.locator('text=22.13.10 (R1EP)').first().click();
}


const jobsTotalRequirementsSection = 'Jobs Total Requirements:'
const jobsTotalRequirementsTests = [
  {index: 1, name: 'CPU total', expectedHeading: 'CPU: ', expectedDelta: "+1 vCPU"},
  {index: 2, name: 'Memory total', expectedHeading: 'Memory: ', expectedDelta: "+1 GiB"}
]

jobsTotalRequirementsTests.forEach(function (item) {
  test(jobsTotalRequirementsSection + ' Check for plus value at ' + item.name, async ({ page }) => {
    await goToCompare(page);
    await selectSmallEnm(page);
    await selectEnmReleasesWithPositiveDifference(page);
    await page.locator('text=Please select...').click();
    await page.locator('text=IPv6 EXT').first().click();
    await page.locator('button:has-text("Compare Releases")').click();
    await page.click('text=' + jobsTotalRequirementsSection);
    const heading = await page.innerText('.row .row:nth-child(1) div:nth-child(2) div:nth-child(4) div:nth-child(' + item.index + ') .tooltip');
    const value = await page.innerText('.row .row:nth-child(1) div:nth-child(2) div:nth-child(4) div:nth-child(' + item.index + ') .val');
    expect(heading).toEqual(item.expectedHeading);
    expect(value).toContain(item.expectedDelta);
  });
});


const otherRequirementsSection = 'Networking Requirements:'
const otherRequirementsIPv6Test = [
  {index: 1, name: 'Site Specific IPv6 Addresses', expectedHeading: 'IP Address Requirements:', expectedDelta: "+1"},
]

otherRequirementsIPv6Test.forEach(function (item) {
  test(otherRequirementsSection + ': Check ' +  item.name, async ({ page }) => {
    await goToCompare(page);
    await selectSmallEnm(page);
    await selectEnmReleasesWithPositiveDifference(page);
    await page.locator('text=Please select...').click();
    await page.locator('text=IPv6 EXT').first().click();
    await page.locator('button:has-text("Compare Releases")').click();
    await page.click('text=' + otherRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(9) div:nth-child(2) div:nth-child(1) .tooltip');
    const value = await page.innerText('.row div:nth-child(9) div:nth-child(2) div:nth-child(1) .val');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toContain(item.expectedDelta);
  });
});

const otherRequirementsDualTests = [
  {index: 2, name: 'Dualstack: Site Specific IPv4 Addresses', expectedHeading: 'IP Address Requirements:', expectedDelta: "+1"},
  {index: 3, name: 'Dualstack: Site Specific IPv6 Addresses', expectedHeading: 'IP Address Requirements:', expectedDelta: "+1"}
]

otherRequirementsDualTests.forEach(function (item) {
  test(otherRequirementsSection + ': Check Multiple compare release button presses' +  item.name, async ({ page }) => {
    await goToCompare(page);
    await selectSmallEnm(page);
    await selectEnmReleasesWithPositiveDifference(page);
    await page.locator('text=Please select...').click();
    await page.locator('text=Dual Stack').first().click();
    await page.locator('button:has-text("Compare Releases")').click();
    await page.click('text=' + otherRequirementsSection);
    const heading = await page.innerText('.row div:nth-child(9) div:nth-child(2) div:nth-child(1) .tooltip');
    const value = await page.innerText('.row div:nth-child(9) div:nth-child(2) div:nth-child(1) div:nth-child(' + item.index + ') div:nth-child(1)');
    expect(heading).toContain(item.expectedHeading);
    expect(value).toContain(item.expectedDelta);
  });
});