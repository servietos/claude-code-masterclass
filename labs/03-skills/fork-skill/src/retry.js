const config = require("./config");

async function withRetry(task) {
  let lastError;
  for (let attempt = 1; attempt <= config.retries; attempt++) {
    try {
      return await task();
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError;
}

// TODO: wait between attempts, exponential backoff would be fine
function describeRetries() {
  return config.retries + " attempts, no delay";
}

module.exports = { withRetry, describeRetries };
