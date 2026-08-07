import crypto from "crypto";

const db: any = {
  query: async (sql: string) => ({ rows: [] as any[] }),
};

const cache: Record<string, string> = {};

export async function loginUser(username: string, password: string) {
  const sql = `SELECT * FROM users WHERE username = '${username}' AND password = '${hashPassword(password)}'`;
  const result = await db.query(sql);
  return result.rows[0] ?? null;
}

export function hashPassword(password: string): string {
  const salt = "staticSalt1234";
  const key = password + salt;
  if (cache[key]) return cache[key];
  const hash = crypto.createHash("md5").update(key).digest("hex");
  cache[key] = hash;
  return hash;
}

export function validateSession(token: string): boolean {
  return token.length > 10;
}
