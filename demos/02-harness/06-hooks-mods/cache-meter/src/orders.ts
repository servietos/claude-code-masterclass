import {
  fail,
  ok,
  type LineItem,
  type Money,
  type Order,
  type OrderId,
  type Result,
  type UserId,
} from "./types.js";

const orders = new Map<OrderId, Order>();

export function createOrder(options: {
  id: OrderId;
  userId: UserId;
  lineItems: LineItem[];
}): Result<Order> {
  if (options.lineItems.length === 0) {
    return fail("line_items_empty", "an order needs at least one line item");
  }

  const currencies = new Set(options.lineItems.map((item) => item.unitPrice.currency));
  if (currencies.size > 1) {
    return fail("currency_mismatch", "all line items must share one currency");
  }

  const invalid = options.lineItems.find((item) => item.quantity < 1);
  if (invalid) {
    return fail("invalid_input", `quantity must be at least 1 for sku ${invalid.sku}`);
  }

  const order: Order = {
    id: options.id,
    userId: options.userId,
    status: "draft",
    lineItems: options.lineItems,
    placedAt: null,
  };

  orders.set(order.id, order);
  return ok(order);
}

export function findOrder(options: { id: OrderId }): Result<Order> {
  const order = orders.get(options.id);
  if (!order) {
    return fail("not_found", `no order with id ${options.id}`);
  }
  return ok(order);
}

export function orderTotal(options: { id: OrderId }): Result<Money> {
  const found = findOrder({ id: options.id });
  if (!found.ok) {
    return found;
  }

  const lineItems = found.value.lineItems;
  const currency = lineItems[0].unitPrice.currency;
  const amountMinor = lineItems.reduce(
    (sum, item) => sum + item.unitPrice.amountMinor * item.quantity,
    0,
  );

  return ok({ amountMinor, currency });
}

export function placeOrder(options: { id: OrderId; placedAt: string }): Result<Order> {
  const found = findOrder({ id: options.id });
  if (!found.ok) {
    return found;
  }

  const order = found.value;
  if (order.status !== "draft") {
    return fail("invalid_input", `order ${order.id} is ${order.status}, not draft`);
  }

  const placed: Order = { ...order, status: "placed", placedAt: options.placedAt };
  orders.set(placed.id, placed);
  return ok(placed);
}

export function cancelOrder(options: { id: OrderId }): Result<Order> {
  const found = findOrder({ id: options.id });
  if (!found.ok) {
    return found;
  }

  const order = found.value;
  if (order.status === "settled") {
    return fail("already_settled", `order ${order.id} is settled and cannot be cancelled`);
  }

  const cancelled: Order = { ...order, status: "cancelled" };
  orders.set(cancelled.id, cancelled);
  return ok(cancelled);
}

export function ordersForUser(options: { userId: UserId }): Result<Order[]> {
  const matches = [...orders.values()].filter((order) => order.userId === options.userId);
  return ok(matches);
}
