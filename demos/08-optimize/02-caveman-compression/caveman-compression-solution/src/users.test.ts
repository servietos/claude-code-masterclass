import { describe, it, expect, beforeAll, afterAll } from "vitest"
import Fastify from "fastify"
import { serializerCompiler, validatorCompiler } from "@fastify/type-provider-zod"
import { usersRouter } from "./users/router.js"

const app = Fastify()

beforeAll(async () => {
  app.setValidatorCompiler(validatorCompiler)
  app.setSerializerCompiler(serializerCompiler)
  await app.register(usersRouter)
  await app.ready()
})

afterAll(async () => {
  await app.close()
})

describe("GET /users", () => {
  it("returns 200 with data array", async () => {
    const response = await app.inject({ method: "GET", url: "/users" })
    expect(response.statusCode).toBe(200)
    const body = response.json()
    expect(Array.isArray(body.data)).toBe(true)
    expect(body.data.length).toBeGreaterThan(0)
  })

  it("returns has_next: false on page beyond data", async () => {
    const response = await app.inject({ method: "GET", url: "/users?page=99" })
    expect(response.statusCode).toBe(200)
    const body = response.json()
    expect(body.has_next).toBe(false)
  })
})
