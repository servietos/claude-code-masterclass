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

  app.get("/users", async () => {
    return users;
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

  return app;
}
