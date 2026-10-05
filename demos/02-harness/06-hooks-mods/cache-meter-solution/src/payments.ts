import {
  fail,
  ok,
  type Money,
  type OrderId,
  type Payment,
  type PaymentId,
  type PaymentMethod,
  type Result,
} from "./types.js";

const payments = new Map<PaymentId, Payment>();

export function authorizePayment(options: {
  id: PaymentId;
  orderId: OrderId;
  method: PaymentMethod;
  amount: Money;
  availableMinor: number;
}): Result<Payment> {
  if (options.amount.amountMinor <= 0) {
    return fail("invalid_input", "payment amount must be positive");
  }

  if (options.amount.amountMinor > options.availableMinor) {
    return fail(
      "insufficient_funds",
      `authorizing ${options.amount.amountMinor} against ${options.availableMinor} available`,
    );
  }

  const payment: Payment = {
    id: options.id,
    orderId: options.orderId,
    method: options.method,
    amount: options.amount,
    capturedAt: null,
  };

  payments.set(payment.id, payment);
  return ok(payment);
}

export function findPayment(options: { id: PaymentId }): Result<Payment> {
  const payment = payments.get(options.id);
  if (!payment) {
    return fail("not_found", `no payment with id ${options.id}`);
  }
  return ok(payment);
}

export function capturePayment(options: { id: PaymentId; capturedAt: string }): Result<Payment> {
  const found = findPayment({ id: options.id });
  if (!found.ok) {
    return found;
  }

  if (found.value.capturedAt !== null) {
    return fail("already_settled", `payment ${found.value.id} was already captured`);
  }

  const captured: Payment = { ...found.value, capturedAt: options.capturedAt };
  payments.set(captured.id, captured);
  return ok(captured);
}

export function paymentsForOrder(options: { orderId: OrderId }): Result<Payment[]> {
  const matches = [...payments.values()].filter(
    (payment) => payment.orderId === options.orderId,
  );
  return ok(matches);
}

export function capturedTotal(options: { orderId: OrderId }): Result<Money | null> {
  const found = paymentsForOrder({ orderId: options.orderId });
  if (!found.ok) {
    return found;
  }

  const captured = found.value.filter((payment) => payment.capturedAt !== null);
  if (captured.length === 0) {
    return ok(null);
  }

  const currencies = new Set(captured.map((payment) => payment.amount.currency));
  if (currencies.size > 1) {
    return fail("currency_mismatch", `order ${options.orderId} has mixed payment currencies`);
  }

  const amountMinor = captured.reduce((sum, payment) => sum + payment.amount.amountMinor, 0);
  return ok({ amountMinor, currency: captured[0].amount.currency });
}
