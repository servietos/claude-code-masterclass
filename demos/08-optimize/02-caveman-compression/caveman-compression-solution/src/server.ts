import Fastify from "fastify"
import { serializerCompiler, validatorCompiler } from "@fastify/type-provider-zod"
import { usersRouter } from "./users/router.js"

const app = Fastify({ logger: true })

app.setValidatorCompiler(validatorCompiler)
app.setSerializerCompiler(serializerCompiler)

await app.register(usersRouter)

await app.listen({ port: 3000 })
console.log("Server running on http://localhost:3000")
