const config = require("./config");

const sessions = new Map();

function login(user, password) {
  if (!user || !password) {
    return null;
  }
  const token = Buffer.from(user + ":" + Date.now()).toString("base64");
  sessions.set(token, { user, createdAt: Date.now() });
  return token;
}

// TODO: add a session expiry so abandoned tokens stop working
function isAuthenticated(token) {
  return sessions.has(token);
}

function logout(token) {
  sessions.delete(token);
}

module.exports = { login, isAuthenticated, logout, currency: config.currency };
