export type AskCheckPrompt = { n: number; text: string };
export type AskCheckQuestion = { question: string; answer: { text: string; n: number } | null };
export type AskCheckAsked = { question: string; n: number };

declare module "claude-code" {
  interface PluginState {
    "ask-check": { prompts: AskCheckPrompt[]; questions: AskCheckQuestion[]; asked: AskCheckAsked[]; answers: string[]; count: number };
  }
}
