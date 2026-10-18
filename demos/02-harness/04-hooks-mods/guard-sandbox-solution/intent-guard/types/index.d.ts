export type IntentGuardHeld = {
  id: string;
  tool: string;
  command: string;
  cwd: string;
  agentId: string | null;
  reasons: string[];
  lastPrompt: string;
};

declare module "claude-code" {
  interface PluginState {
    "intent-guard": { prompts: string[]; lastAnswer: string; held: IntentGuardHeld[] };
  }
}
