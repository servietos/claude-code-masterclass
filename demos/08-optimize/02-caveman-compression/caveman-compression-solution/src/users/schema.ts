import { z } from "zod"

export const UserSchema = z.object({
  id: z.number(),
  name: z.string(),
  email: z.string(),
})

export const UsersQuerySchema = z.object({
  page: z.coerce.number().optional().default(1),
  size: z.coerce.number().optional().default(20),
})

export const UserListResponseSchema = z.object({
  data: z.array(UserSchema),
  page: z.number(),
  size: z.number(),
  total: z.number(),
  has_next: z.boolean(),
})

export type User = z.infer<typeof UserSchema>
export type UsersQuery = z.infer<typeof UsersQuerySchema>
export type UserListResponse = z.infer<typeof UserListResponseSchema>
