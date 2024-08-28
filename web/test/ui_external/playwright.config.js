const config = {
  use: {
    launchOptions: {
      executablePath: '/usr/bin/chromium-browser',
      // executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
      // executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
      args: ['--ignore-certificate-errors'],
      timeout: 6000
    }
  },
};

module.exports = config;
