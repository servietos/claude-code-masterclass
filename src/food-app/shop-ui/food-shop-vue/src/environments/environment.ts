export interface Environment {
  production: boolean;
  title: string;
  authEnabled: boolean;
  mockCheckout: boolean;
  catalogApi: string;
  ordersApi: string;
  azure: {
    apimSubscriptionKey: string;
    applicationInsights: string;
    appReg: {
      clientId: string;
      authority: string;
      redirectUri: string;
      scopes: [string, string[]][];
    };
  };
  features: {
    logging: boolean;
    remoteCart: boolean;
    persistCart: boolean;
  };
  testuser: string;
}

const env: FoodShopEnv = window.env ?? {};

const production: Environment = {
  production: true,
  title: 'Food Shop',
  authEnabled: false,
  mockCheckout: true,
  catalogApi: env.CATALOG_API_URL || 'http://localhost:5000',
  ordersApi: env.ORDERS_API_URL || 'https://localhost:5002/',
  azure: {
    apimSubscriptionKey: env.APIM_KEY || '39fc8b24086a4346a6317d047869f983',
    applicationInsights: env.APPLICATION_INSIGHTS || '89094b1f-dde1-4c07-8d40-f7d01ef18d55',
    appReg: {
      clientId: env.CLIENT_ID ?? '',
      authority: 'https://login.microsoftonline.com/' + env.AUTHORITY,
      redirectUri: env.REDIRECT_URI ?? '',
      scopes: [
        ['https://graph.microsoft.com/v1.0/me', ['user.read']],
        ['http://localhost:5000/food', ['api://b509d389-361a-447b-afb2-97cc8131dad6/access_as_user']],
      ],
    },
  },
  features: {
    logging: false,
    remoteCart: false,
    persistCart: false,
  },
  testuser: 'alexander.pajer@integrations.at',
};

const development: Environment = {
  production: false,
  title: 'Food Shop',
  authEnabled: false,
  mockCheckout: true,
  catalogApi: 'http://localhost:5000',
  ordersApi: 'http://localhost:5002',
  azure: {
    apimSubscriptionKey: '39fc8b24086a4346a6317d047869f983',
    applicationInsights: 'd1588cb9-4e43-4fdc-9aef-99436565d628',
    appReg: {
      clientId: 'd23642f7-9ccf-4165-92e7-919f625a5acc',
      authority: 'https://login.microsoftonline.com/d92b247e-90e0-4469-a129-6a32866c0d0a/',
      redirectUri: 'http://localhost:4200/',
      scopes: [
        ['https://graph.microsoft.com/v1.0/me', ['user.read']],
        ['http://localhost:5000/food', ['api://b509d389-361a-447b-afb2-97cc8131dad6/access_as_user']],
      ],
    },
  },
  features: {
    logging: false,
    remoteCart: false,
    persistCart: false,
  },
  testuser: 'alexander.pajer@integrations.at',
};

export const environment: Environment = import.meta.env.DEV ? development : production;
