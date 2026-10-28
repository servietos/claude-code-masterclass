import { environment } from '@/environments/environment';
import type { Order } from '@/models/order';
import type { OrderEventResponse } from '@/models/order-event-response';
import { logger } from '@/services/logger';
import { http } from './http';

export function checkout(order: Order): Promise<OrderEventResponse> {
  logger.logEvent('checking out order', order as unknown as Record<string, unknown>);
  const url = `${environment.ordersApi}/orders/create`;
  logger.logEventObject('using url', url);
  return http<OrderEventResponse>(`${environment.ordersApi}/orders/create`, {
    method: 'POST',
    body: JSON.stringify(order),
  });
}
