import { describe, expect, it } from "vitest";
import { buildApp, seedUsers } from "./index.js";

describe("GET /users", () => {
  it("returns an empty page on a fresh app", async () => {
    const app = buildApp();
    const response = await app.inject({ method: "GET", url: "/users" });
    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual({ data: [], page: 1, size: 20, total: 0, has_next: false });
    await app.close();
  });

  it.each([
    { page: 1, size: 10, expectedFirstId: "1", expectedCount: 10, has_next: true },
    { page: 2, size: 10, expectedFirstId: "11", expectedCount: 10, has_next: true },
    { page: 3, size: 10, expectedFirstId: "21", expectedCount: 5, has_next: false },
  ])("paginates 25 seeded users for page=$page size=$size", async (testCase) => {
    const app = buildApp(seedUsers(25));
    const response = await app.inject({
      method: "GET",
      url: `/users?page=${testCase.page}&size=${testCase.size}`,
    });
    expect(response.statusCode).toBe(200);
    const body = response.json();
    expect(Object.keys(body)).toEqual(["data", "page", "size", "total", "has_next"]);
    expect(body.page).toBe(testCase.page);
    expect(body.size).toBe(testCase.size);
    expect(body.total).toBe(25);
    expect(body.has_next).toBe(testCase.has_next);
    expect(body.data).toHaveLength(testCase.expectedCount);
    expect(body.data[0].id).toBe(testCase.expectedFirstId);
    await app.close();
  });

  it.each([
    { query: "?page=0", label: "page below 1" },
    { query: "?size=abc", label: "non-numeric size" },
  ])("rejects $label with 400", async (testCase) => {
    const app = buildApp(seedUsers(25));
    const response = await app.inject({ method: "GET", url: `/users${testCase.query}` });
    expect(response.statusCode).toBe(400);
    expect(response.json().error).toBe("invalid_query");
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

describe("DELETE /users/:id", () => {
  it("removes an existing user and returns 204", async () => {
    const app = buildApp(seedUsers(3));
    const response = await app.inject({ method: "DELETE", url: "/users/2" });
    expect(response.statusCode).toBe(204);
    const list = await app.inject({ method: "GET", url: "/users" });
    expect(list.json().total).toBe(2);
    expect(list.json().data.map((user: { id: string }) => user.id)).toEqual(["1", "3"]);
    await app.close();
  });

  it.each([{ id: "999" }, { id: "unknown" }])("returns 404 for missing id $id", async (testCase) => {
    const app = buildApp(seedUsers(3));
    const response = await app.inject({ method: "DELETE", url: `/users/${testCase.id}` });
    expect(response.statusCode).toBe(404);
    expect(response.json().error).toBe("not_found");
    await app.close();
  });
});
