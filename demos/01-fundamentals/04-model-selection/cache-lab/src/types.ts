export type Brand<T, B extends string> = T & { readonly __brand: B };

export type OrderId = Brand<string, "OrderId">;
export type UserId = Brand<string, "UserId">;
export type PaymentId = Brand<string, "PaymentId">;

export type ErrorCode =
  | "not_found"
  | "invalid_input"
  | "already_settled"
  | "insufficient_funds"
  | "user_suspended"
  | "currency_mismatch"
  | "line_items_empty";

export type AppError = {
  code: ErrorCode;
  detail: string;
};

export type Result<T> = { ok: true; value: T } | { ok: false; error: AppError };

export function ok<T>(value: T): Result<T> {
  return { ok: true, value };
}

export function fail<T>(code: ErrorCode, detail: string): Result<T> {
  return { ok: false, error: { code, detail } };
}

export type Currency = "EUR" | "USD" | "GBP";

export type Money = {
  amountMinor: number;
  currency: Currency;
};

export type OrderStatus = "draft" | "placed" | "settled" | "cancelled";

export type LineItem = {
  sku: string;
  quantity: number;
  unitPrice: Money;
};

export type Order = {
  id: OrderId;
  userId: UserId;
  status: OrderStatus;
  lineItems: LineItem[];
  placedAt: string | null;
};

export type UserStatus = "active" | "suspended" | "closed";

export type User = {
  id: UserId;
  email: string;
  status: UserStatus;
  creditLimit: Money;
  createdAt: string;
};

export type PaymentMethod = "card" | "sepa" | "credit";

export type Payment = {
  id: PaymentId;
  orderId: OrderId;
  method: PaymentMethod;
  amount: Money;
  capturedAt: string | null;
};
