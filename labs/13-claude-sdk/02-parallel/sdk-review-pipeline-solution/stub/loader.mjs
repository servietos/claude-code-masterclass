const FAKE = new URL("./fake-sdk.mjs", import.meta.url).href;

export async function resolve(specifier, context, nextResolve) {
  if (specifier === "@anthropic-ai/claude-agent-sdk") {
    return { url: FAKE, shortCircuit: true, format: "module" };
  }
  return nextResolve(specifier, context);
}
