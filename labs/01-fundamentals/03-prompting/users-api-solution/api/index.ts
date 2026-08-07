import Fastify from "fastify";
import type { FastifyInstance } from "fastify";
import { z } from "zod";

export interface User {
  id: string;
  name: string;
  email: string;
}

const createUserSchema = z.object({
  name: z.string().min(1),
  email: z.email(),
});

const listQuerySchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  size: z.coerce.number().int().min(1).max(100).default(20),
});

export function seedUsers(count: number): User[] {
  return Array.from({ length: count }, (_, index) => ({
    id: String(index + 1),
    name: `User ${index + 1}`,
    email: `user${index + 1}@example.com`,
  }));
}

export function buildApp(seed: User[] = []): FastifyInstance {
  const app = Fastify({ logger: false });
  const users: User[] = [...seed];
  let nextId = users.length + 1;

  app.get("/users", async (request, reply) => {
    const parsed = listQuerySchema.safeParse(request.query);
    if (!parsed.success) {
      return reply.status(400).send({ error: "invalid_query", issues: parsed.error.issues });
    }
    const { page, size } = parsed.data;
    const start = (page - 1) * size;
    const data = users.slice(start, start + size);
    return {
      data,
      page,
      size,
      total: users.length,
      has_next: start + size < users.length,
    };
  });

  app.post("/users", async (request, reply) => {
    const parsed = createUserSchema.safeParse(request.body);
    if (!parsed.success) {
      return reply.status(400).send({ error: "invalid_body", issues: parsed.error.issues });
    }
    const user: User = { id: String(nextId++), ...parsed.data };
    users.push(user);
    return reply.status(201).send(user);
  });

  app.delete("/users/:id", async (request, reply) => {
    const parsed = z.object({ id: z.string().min(1) }).safeParse(request.params);
    if (!parsed.success) {
      return reply.status(400).send({ error: "invalid_params", issues: parsed.error.issues });
    }
    const index = users.findIndex((user) => user.id === parsed.data.id);
    if (index === -1) {
      return reply.status(404).send({ error: "not_found" });
    }
    users.splice(index, 1);
    return reply.status(204).send();
  });

  return app;
}
