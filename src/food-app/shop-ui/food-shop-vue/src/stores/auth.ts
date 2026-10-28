import {
  BrowserCacheLocation,
  EventType,
  LogLevel,
  PublicClientApplication,
  type AuthenticationResult,
  type EventMessage,
} from '@azure/msal-browser';
import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import { environment } from '@/environments/environment';
import type { MsalAccount, MsalAuthResponse } from '@/models/auth';

const loginRequest = { scopes: ['user.read'] };

let msal: PublicClientApplication | null = null;

function createMsal(): PublicClientApplication {
  return new PublicClientApplication({
    auth: {
      clientId: environment.azure.appReg.clientId,
      authority: environment.azure.appReg.authority,
      redirectUri: '/',
    },
    cache: {
      cacheLocation: BrowserCacheLocation.LocalStorage,
    },
    system: {
      loggerOptions: {
        loggerCallback: (logLevel: LogLevel, message: string) => {
          console.log(logLevel, message);
        },
        logLevel: LogLevel.Info,
        piiLoggingEnabled: false,
      },
    },
  });
}

function toAuthResponse(result: AuthenticationResult): MsalAuthResponse {
  return {
    accessToken: result.accessToken,
    account: result.account as unknown as MsalAccount,
    idToken: result.idToken,
    scopes: result.scopes,
  };
}

export const useAuthStore = defineStore('auth', () => {
  const authEnabled = ref(environment.authEnabled);
  const authResponse = ref<MsalAuthResponse | null>(null);

  const loggedIn = computed(() => authResponse.value !== null);
  const user = computed(() => authResponse.value?.account?.username);
  const token = computed(() => authResponse.value?.accessToken);
  const isAuthenticated = computed(() => !authEnabled.value || loggedIn.value);

  async function init() {
    if (!authEnabled.value || msal) {
      return;
    }
    const instance = createMsal();
    msal = instance;
    await instance.initialize();
    instance.addEventCallback((msg: EventMessage) => {
      console.log('MSAL Event', msg);
      if (msg.eventType === EventType.LOGIN_SUCCESS || msg.eventType === EventType.ACQUIRE_TOKEN_SUCCESS) {
        const result = msg.payload as AuthenticationResult;
        if (result.account) {
          instance.setActiveAccount(result.account);
        }
        authResponse.value = toAuthResponse(result);
        console.log(`MSAL Event ${msg.eventType}`, msg.payload);
      }
    });
    const redirectResult = await instance.handleRedirectPromise();
    const account = instance.getAllAccounts()[0];
    if (!redirectResult && account) {
      try {
        await instance.acquireTokenSilent({ ...loginRequest, account });
      } catch (err) {
        console.error(err);
      }
    }
  }

  async function login() {
    if (!authEnabled.value || !msal) {
      return;
    }
    await msal.loginRedirect({ ...loginRequest });
  }

  async function logout() {
    if (!msal) {
      return;
    }
    await msal.logoutRedirect();
    authResponse.value = null;
  }

  async function acquireToken(scopes: string[]): Promise<string | null> {
    if (!msal) {
      return null;
    }
    const account = msal.getActiveAccount() ?? msal.getAllAccounts()[0];
    try {
      const result = await msal.acquireTokenSilent({ scopes, account });
      return result.accessToken;
    } catch {
      await msal.acquireTokenRedirect({ scopes, account });
      return null;
    }
  }

  return { authEnabled, authResponse, loggedIn, user, token, isAuthenticated, init, login, logout, acquireToken };
});
