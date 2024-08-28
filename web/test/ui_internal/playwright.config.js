const config = {
  use: {
    launchOptions: {
      executablePath: '/usr/bin/chromium-browser',
      // executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
      args: ['--ignore-certificate-errors'],
      timeout: 6000
    }
  },
};

module.exports = config;
