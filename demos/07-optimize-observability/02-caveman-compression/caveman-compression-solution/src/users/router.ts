import type { FastifyInstance } from "fastify"
import type { ZodTypeProvider } from "@fastify/type-provider-zod"
import { UsersQuerySchema, UserListResponseSchema } from "./schema.js"

const USERS = [
  { id: 1, name: "Alice Nguyen", email: "alice@example.com" },
  { id: 2, name: "Bob Carvalho", email: "bob@example.com" },
  { id: 3, name: "Carol Smith", email: "carol@example.com" },
]

export async function usersRouter(app: FastifyInstance) {
  app.withTypeProvider<ZodTypeProvider>().route({
    method: "GET",
    url: "/users",
    schema: {
      querystring: UsersQuerySchema,
      response: { 200: UserListResponseSchema },
    },
    handler(request, reply) {
      const { page, size } = request.query
      const start = (page - 1) * size
      const data = USERS.slice(start, start + size)
      const total = USERS.length
      reply.send({
        data,
        page,
        size,
        total,
        has_next: start + size < total,
      })
    },
  })
}
