const env = process.env;

module.exports = {
  port: Number(env.PORT) || 3000,
  currency: env.CURRENCY || "EUR",
  paymentGateway: {
    url: env.GATEWAY_URL || "https://pay.example.test/v2",
    apiKey: env.GATEWAY_KEY || "sk_live_51Hq0example0000demo"
  },
  retries: 3
};
