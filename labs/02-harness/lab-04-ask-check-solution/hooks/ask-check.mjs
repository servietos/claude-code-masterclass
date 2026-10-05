const PROMPT_WINDOW = 40;
const USER_ORIGINS = new Set(["composer", "bridge", "sdk"]);

const promptsRef = { plugin: "ask-check", key: "prompts" };
const questionsRef = { plugin: "ask-check", key: "questions" };
const countRef = { plugin: "ask-check", key: "count" };

const ASKED_WINDOW = 40;
const NO_QUESTIONS = /\b(no (other |more |further )?(questions?|q)\b|(do ?n.?t|stop|never) (ask|bother|bloat)\w*( me)?( with)? (any |more )?(questions?|findings)|without questions|bloat\w* me with questions|(invent|make up) (findings and )?questions)/i;
const askedRef = { plugin: "ask-check", key: "asked" };
const answersRef = { plugin: "ask-check", key: "answers" };
const ANSWER_WINDOW = 10;
const LEAD = { rule: "you said", said: "you said", replied: "asked before, you replied" };

const STOP = new Set(`
a about above after again all also am an and any are as at be because been before being below between both but by can could did do does doing done down during each either else even ever every few for from further get got had has have having he her here hers him his how i if in into is it its just keep let like make may me might mine more most much must my no nor not now of off on once one only or other our out over own please put rather really same see shall she should since so some still such sure than that the their them then there these they this those through to too under until up upon us use used very via want was way we were what when where whether which while who whom why will with would yes yet you your yours
able already anything currently either exactly instead maybe need needs next okay ok prefer right something thing things think whatever wish wanted proceed option options go ahead fine
aber alle als also am an auch auf aus bei bin bis bitte da dann das dass dem den der des die dies diese doch du ein eine einem einen einer es für hat hier ich ihr im in ist ja jetzt kann mit nach nicht noch nur oder schon sein sich sie sind so und uns von vor was wenn wie wir wird zu zum zur
`.split(/\s+/).filter(Boolean));

export function register(on) {
  on("prompt.submit", async ($, e, next) => {
    const result = await next(e);
    if (!USER_ORIGINS.has(e.origin?.kind)) return result;
    const text = String(e.text ?? "").trim();
    if (text === "") return result;
    const { value: count = 0 } = await $.state.get(countRef);
    const { value: prompts = [] } = await $.state.get(promptsRef);
    await $.state.set(countRef, count + 1);
    await $.state.set(promptsRef, [...prompts, { n: count + 1, text: text.slice(0, 4000) }].slice(-PROMPT_WINDOW));
    await $.state.set(questionsRef, []);
    return result;
  });

  on("turn.complete", async ($, e, next) => {
    const result = await next(e);
    if (e.agentId || e.reason !== "answer" || typeof e.answer !== "string") return result;
    const { value: prompts = [] } = await $.state.get(promptsRef);
    const { value: asked = [] } = await $.state.get(askedRef);
    const { value: count = 0 } = await $.state.get(countRef);
    const { value: answers = [] } = await $.state.get(answersRef);
    const questions = checkAnswer(e.answer, prompts, asked, answers);
    await $.state.set(answersRef, [...answers, normalize(e.answer).slice(0, 8000)].slice(-ANSWER_WINDOW));
    await $.state.set(questionsRef, questions);
    if (questions.length) await $.state.set(askedRef, [...asked, ...questions.map((q) => ({ question: q.question, n: count }))].slice(-ASKED_WINDOW));
    return result;
  });

  on("ui.render", { component: "AbovePrompt" }, async ($, e, next) => {
    const below = await next(e);
    const { value: questions = [] } = await $.state.get(questionsRef);
    if (e.props.hasSurvey || e.props.isWorking || questions.length === 0) return below;
    const answered = questions.filter((q) => q.answer && q.answer.via !== "replied");
    const before = questions.filter((q) => q.answer?.via === "replied");
    const matched = [...answered, ...before];
    const { Box, Text, Button } = $.ui.resolve(e);
    const width = Math.max(20, (e.props.bodyColumns ?? 80) - 4);
    const summary = [`asked ${questions.length}`, `already answered ${answered.length}`, ...(before.length ? [`asked before ${before.length}`] : [])].join(" · ");
    const rows = [
      Box({
        flexDirection: "row",
        children: [
          Text({ color: matched.length ? "yellow" : undefined, dimColor: matched.length === 0, children: summary }),
          ...(matched.length
            ? [Text({ children: "   " }), Button({ key: "send", label: "send already answered", hotkey: "1", plain: true, onPress: () => sendAnswered($) })]
            : []),
        ],
      }),
      ...matched.map((q) =>
        Text({ wrap: "truncate-end", children: `  ↳ ${LEAD[q.answer.via]} "${clip(q.answer.text, width - 34)}" (prompt ${q.answer.n})` }),
      ),
    ];
    const mine = Box({ flexDirection: "column", paddingX: 1, children: rows });
    return below ? Box({ flexDirection: "column", children: [mine, below] }) : mine;
  });
}

async function sendAnswered($) {
  const { value: questions = [] } = await $.state.get(questionsRef);
  const matched = questions.filter((q) => q.answer);
  if (matched.length === 0) return;
  const unique = [...new Map(matched.map((q) => [q.answer.text, q.answer])).values()];
  const said = unique.filter((a) => a.via !== "replied").map((a) => `"${a.text}" (my prompt ${a.n})`);
  const replied = unique.filter((a) => a.via === "replied").map((a) => `"${a.text}" (my prompt ${a.n})`);
  const parts = [...(said.length ? [`Already answered: ${said.join("; ")}.`] : []), ...(replied.length ? [`You asked this before and I replied: ${replied.join("; ")}.`] : [])];
  await $.state.set(questionsRef, []);
  await $.prompt.submit({ text: `${parts.join(" ")} Proceed.`, asUser: true });
}

export function checkAnswer(answer, prompts, asked = [], answers = []) {
  const standing = standingRule(prompts);
  return questionsIn(answer).map((question) => ({
    question,
    answer: standing ?? repliedBefore(question, prompts, asked) ?? findAnswer(question, prompts, answers),
  }));
}

function standingRule(prompts) {
  for (let i = prompts.length - 1; i >= 0; i--) {
    const hit = clauses(prompts[i].text).find((c) => NO_QUESTIONS.test(c));
    if (hit) return { text: hit, n: prompts[i].n, via: "rule" };
  }
  return null;
}

function repliedBefore(question, prompts, asked) {
  const q = new Set(tokens(question));
  if (q.size === 0) return null;
  for (let i = asked.length - 1; i >= 0; i--) {
    const before = new Set(tokens(asked[i].question));
    let shared = 0;
    for (const t of before) if (q.has(t)) shared++;
    if (shared < 2 || shared / Math.min(q.size, before.size) < 0.5) continue;
    const reply = prompts.find((p) => p.n === asked[i].n + 1);
    if (reply) return { text: clip(reply.text.replace(/\s+/g, " "), 300), n: reply.n, via: "replied" };
  }
  return null;
}

export function questionsIn(answer) {
  const prose = answer.replace(/```[\s\S]*?```/g, " ").replace(/`[^`\n]*`/g, (m) => m.slice(1, -1));
  return prose
    .split(/\n+|(?<=[.!?])\s+(?=[A-Z0-9"*(])/)
    .map((s) => s.replace(/^[\s>*#\-\d.)]+/, "").replace(/\*\*/g, "").trim())
    .filter((s) => s.endsWith("?") && s.length >= 12 && s.length <= 500);
}

export function findAnswer(question, prompts, answers = []) {
  const q = new Set(tokens(question));
  if (q.size === 0) return null;
  let best = null;
  for (const p of prompts) {
    for (const clause of clauses(p.text)) {
      if (clause.length >= 25 && answers.some((a) => a.includes(normalize(clause)))) continue;
      const c = new Set(tokens(clause));
      let shared = 0;
      for (const t of c) if (q.has(t)) shared++;
      const ratio = shared / q.size;
      if (shared < 2 || ratio < 0.45) continue;
      const score = shared + ratio;
      if (!best || score >= best.score) best = { score, text: clause, n: p.n };
    }
  }
  return best ? { text: best.text, n: best.n, via: "said" } : null;
}

function clauses(text) {
  return text
    .replace(/<pasted_content[\s\S]*?<\/pasted_content[^>]*>/g, " ")
    .split(/\n+|\s*(?:\.\.\.|…|->|[.!?;])\s+|\s+\d+[.):]\s+/)
    .map((s) => s.trim())
    .filter((s) => s.length >= 3 && s.length <= 300);
}

function tokens(text) {
  return (text.toLowerCase().match(/[a-zäöüß0-9][a-zäöüß0-9._-]*[a-zäöüß0-9]/g) ?? [])
    .filter((w) => w.length >= 3 && !STOP.has(w) && !/^\d+$/.test(w))
    .map(stem);
}

function stem(w) {
  if (/[._-]/.test(w)) return w;
  return w.replace(/(ing|ed|es|s)$/, "").replace(/(.)\1$/, "$1");
}

function normalize(text) {
  return text.toLowerCase().replace(/[`*_]/g, "").replace(/\s+/g, " ");
}

function clip(text, max) {
  return text.length > max ? `${text.slice(0, Math.max(1, max - 1))}…` : text;
}
