import { environment } from '@/environments/environment';
import { useAuthStore } from '@/stores/auth';

export class HttpError extends Error {
  constructor(
    readonly url: string,
    readonly status: number,
    readonly statusText: string,
  ) {
    super(`Http failure response for ${url}: ${status} ${statusText}`);
    this.name = 'HttpError';
  }
}

function patternToRegExp(pattern: string): RegExp {
  const escaped = pattern
    .split('*')
    .map((part) => part.replace(/[.+?^${}()|[\]\\]/g, '\\$&'))
    .join('.*');
  return new RegExp(`^${escaped}$`, 'i');
}

function scopesForUrl(url: string): string[] | null {
  const target = url.split(/[?#]/)[0] ?? url;
  const match = environment.azure.appReg.scopes.find(([resource]) => patternToRegExp(resource).test(target));
  return match ? match[1] : null;
}

export async function http<T>(url: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  headers.set('Ocp-Apim-Subscription-Key', environment.azure.apimSubscriptionKey);
  if (init?.body !== undefined && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (!headers.has('Accept')) {
    headers.set('Accept', 'application/json, text/plain, */*');
  }

  if (environment.authEnabled) {
    const scopes = scopesForUrl(url);
    if (scopes) {
      const token = await useAuthStore().acquireToken(scopes);
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
    }
  }

  const response = await fetch(url, { ...init, headers });
  if (!response.ok) {
    throw new HttpError(url, response.status, response.statusText);
  }

  const text = await response.text();
  return (text ? JSON.parse(text) : null) as T;
}
