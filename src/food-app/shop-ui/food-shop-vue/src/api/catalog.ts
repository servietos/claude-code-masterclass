import { environment } from '@/environments/environment';
import type { CatalogItem } from '@/models/catalog-item';
import { http, HttpError } from './http';

const entityUrl = () => `${environment.catalogApi}/food`;

export function getAll(): Promise<CatalogItem[]> {
  return http<CatalogItem[]>(entityUrl());
}

export function add(item: CatalogItem): Promise<CatalogItem> {
  return http<CatalogItem>(entityUrl(), {
    method: 'POST',
    body: JSON.stringify(item),
  });
}

export function update(item: CatalogItem): Promise<CatalogItem> {
  return http<CatalogItem>(entityUrl(), {
    method: 'PUT',
    body: JSON.stringify({ ...item }),
  });
}

export async function remove(id: number): Promise<void> {
  try {
    await http<unknown>(`${entityUrl()}${id}`, { method: 'DELETE' });
  } catch (err) {
    if (err instanceof HttpError && err.status === 404) {
      return;
    }
    throw err;
  }
}
