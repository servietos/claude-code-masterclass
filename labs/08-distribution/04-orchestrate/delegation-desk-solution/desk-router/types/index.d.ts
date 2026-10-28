export type Delegation = {
  subagentType: string
  description: string
  model: string
  isRerouted: boolean
}

declare module 'claude-code' {
  interface PluginState {
    'desk-router': { ledger: Delegation[] }
  }
}
