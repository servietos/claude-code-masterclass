export {};

declare global {
  interface FoodShopEnv {
    CATALOG_API_URL?: string;
    ORDERS_API_URL?: string;
    AUTH_ENABLED?: string;
    CLIENT_ID?: string;
    AUTHORITY?: string;
    REDIRECT_URI?: string;
    APPLICATION_INSIGHTS?: string;
    APIM_KEY?: string;
  }

  interface Window {
    env?: FoodShopEnv;
  }
}
