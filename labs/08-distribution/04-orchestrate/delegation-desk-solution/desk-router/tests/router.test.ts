import { expect, test } from 'claude-code/testing'

const PROMPT = { origin: { kind: 'composer' }, wait: false } as const

const SPAWN = {
  tool_use_id: 'toolu_1',
  description: 'Find the loyalty discount',
  prompt: 'Where is the loyalty discount calculated in shop-api?',
  subagentType: 'general-purpose',
  provider: { plugin: 'engine', tier: 'core' },
  parentModel: 'claude-sonnet-5-5',
  background: false,
  fork: false,
} as const

test('a lookup prompt carries the delegation hint', async ($, on) => {
  let context: readonly string[] = []
  on('prompt.submit', (_, e) => {
    context = e.context ?? []

    return { text: e.text }
  })

  await $.prompt.submit({ ...PROMPT, text: 'Where is the loyalty discount calculated?' })

  expect(context.join('\n')).toContain('desk-router:scout')
})

test('a prompt that changes code carries no hint', async ($, on) => {
  let context: readonly string[] = []
  on('prompt.submit', (_, e) => {
    context = e.context ?? []

    return { text: e.text }
  })

  await $.prompt.submit({ ...PROMPT, text: 'Raise the shipping fee to 5.90' })

  expect(context).toEqual([])
})

test('a generic lookup spawn goes to the scout with the brief', async ($, on) => {
  let spawned = { subagentType: '', prompt: '' }
  on('agent.spawn', (_, e) => {
    spawned = { subagentType: e.subagentType, prompt: e.prompt }

    return { model: 'claude-haiku-5-5', agentId: 'a1' }
  })

  await $.agent.spawn(SPAWN)

  expect(spawned.subagentType).toBe('desk-router:scout')
  expect(spawned.prompt).toContain('[desk-router brief]')
})

test('a named specialist keeps its type and still gets the brief', async ($, on) => {
  let spawned = { subagentType: '', prompt: '' }
  on('agent.spawn', (_, e) => {
    spawned = { subagentType: e.subagentType, prompt: e.prompt }

    return { model: 'claude-sonnet-5-5', agentId: 'a2' }
  })

  await $.agent.spawn({ ...SPAWN, subagentType: 'Plan', description: 'Plan the shipping change' })

  expect(spawned.subagentType).toBe('Plan')
  expect(spawned.prompt).toContain('[desk-router brief]')
})

test('/desk lists every briefed subagent', async ($, on) => {
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('command.register', () => ({ value: { command: 'desk' } }))
  on('agent.spawn', () => ({ model: 'claude-haiku-5-5', agentId: 'a3' }))

  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })
  await $.agent.spawn(SPAWN)
  const answer = await $.command.run({
    command: 'desk',
    args: '',
    origin: { kind: 'composer' },
    presentation: { isFullscreen: false, columns: 80 },
  })

  expect(answer.text).toContain('desk-router:scout on claude-haiku-5-5 (rerouted)')
})
