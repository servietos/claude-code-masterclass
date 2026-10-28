import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Delegation } from '../types'

const SCOUT = 'desk-router:scout'
const GENERIC = new Set(['general-purpose', 'Explore'])
const PEOPLE = new Set(['composer', 'bridge', 'sdk'])
const LOOKUP = /\b(where (is|are|does|do)|which (files?|modules?|functions?)|what (does|do|reads|calls)|find|locate|list)\b/i
const HINT = `desk-router: this prompt is a lookup. Delegate it to the ${SCOUT} agent and answer from its report.`
const BRIEF = [
  '[desk-router brief]',
  '- Read only: never edit or write a file.',
  '- Cite every fact as path:line.',
  '- Report in at most 1500 characters.',
].join('\n')

const ledger = atom({ plugin: 'desk-router', key: 'ledger' } as const, [])

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'desk', description: 'List the subagents desk-router briefed in this session' })

    return next(e)
  })

  on('prompt.submit', ($, e, next) =>
    PEOPLE.has(e.origin.kind) && !e.command && LOOKUP.test(e.text)
      ? next({ ...e, context: [...(e.context ?? []), HINT] })
      : next(e),
  )

  on('agent.spawn', async ($, e, next) => {
    if (e.resume || e.workflow || e.fork) {
      return next(e)
    }

    const isRerouted = GENERIC.has(e.subagentType) && LOOKUP.test(`${e.description} ${e.prompt}`)
    const subagentType = isRerouted ? SCOUT : e.subagentType
    const started = await next({ ...e, subagentType, prompt: `${e.prompt}\n\n${BRIEF}` })
    const entry: Delegation = { subagentType, description: e.description, model: started.model ?? 'denied', isRerouted }
    await update($, ledger, all => [...all, entry])

    return started
  })

  on('command.run', { command: 'desk' }, async $ => {
    const list = await read($, ledger)
    const rows = list.map((one, i) => `${i + 1}. ${one.subagentType} on ${one.model}${one.isRerouted ? ' (rerouted)' : ''}: ${one.description}`)

    return { text: rows.length > 0 ? rows.join('\n') : 'No subagent briefed yet.' }
  })
}
