import { describe, expect, it } from "vitest";
import { buildApp } from "./index.js";

describe("GET /users", () => {
  it("returns an empty array on a fresh app", async () => {
    const app = buildApp();
    const response = await app.inject({ method: "GET", url: "/users" });
    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual([]);
    await app.close();
  });
});

describe("POST /users", () => {
  it("creates a user and returns 201", async () => {
    const app = buildApp();
    const response = await app.inject({
      method: "POST",
      url: "/users",
      payload: { name: "Ada", email: "ada@example.com" },
    });
    expect(response.statusCode).toBe(201);
    expect(response.json()).toMatchObject({ name: "Ada", email: "ada@example.com" });
    await app.close();
  });

  it.each([
    { name: "", email: "ada@example.com" },
    { name: "Ada", email: "not-an-email" },
  ])("rejects invalid payload %j with 400", async (payload) => {
    const app = buildApp();
    const response = await app.inject({ method: "POST", url: "/users", payload });
    expect(response.statusCode).toBe(400);
    expect(response.json().error).toBe("invalid_body");
    await app.close();
  });
});
