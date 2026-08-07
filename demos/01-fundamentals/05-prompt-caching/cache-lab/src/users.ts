import {
  fail,
  ok,
  type Currency,
  type Money,
  type Result,
  type User,
  type UserId,
  type UserStatus,
} from "./types.js";

const users = new Map<UserId, User>();

const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

export function createUser(options: {
  id: UserId;
  email: string;
  creditLimit: Money;
  createdAt: string;
}): Result<User> {
  if (!EMAIL_PATTERN.test(options.email)) {
    return fail("invalid_input", `${options.email} is not a valid email address`);
  }

  if (options.creditLimit.amountMinor < 0) {
    return fail("invalid_input", "credit limit cannot be negative");
  }

  const user: User = {
    id: options.id,
    email: options.email,
    status: "active",
    creditLimit: options.creditLimit,
    createdAt: options.createdAt,
  };

  users.set(user.id, user);
  return ok(user);
}

export function findUser(options: { id: UserId }): Result<User> {
  const user = users.get(options.id);
  if (!user) {
    return fail("not_found", `no user with id ${options.id}`);
  }
  return ok(user);
}

export function setUserStatus(options: { id: UserId; status: UserStatus }): Result<User> {
  const found = findUser({ id: options.id });
  if (!found.ok) {
    return found;
  }

  const updated: User = { ...found.value, status: options.status };
  users.set(updated.id, updated);
  return ok(updated);
}

export function assertUserCanTransact(options: { id: UserId }): Result<User> {
  const found = findUser({ id: options.id });
  if (!found.ok) {
    return found;
  }

  if (found.value.status !== "active") {
    return fail("user_suspended", `user ${found.value.id} is ${found.value.status}`);
  }

  return ok(found.value);
}

export function remainingCredit(options: {
  id: UserId;
  committedMinor: number;
  currency: Currency;
}): Result<Money> {
  const found = findUser({ id: options.id });
  if (!found.ok) {
    return found;
  }

  const limit = found.value.creditLimit;
  if (limit.currency !== options.currency) {
    return fail("currency_mismatch", `credit limit is ${limit.currency}, not ${options.currency}`);
  }

  return ok({
    amountMinor: limit.amountMinor - options.committedMinor,
    currency: limit.currency,
  });
}
