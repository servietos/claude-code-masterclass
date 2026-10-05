import { describe, expect, test } from "claude-code/testing";

const BAND = { plugin: "ask-check", surface: "terminal", component: "AbovePrompt", props: { hasSurvey: false, isWorking: false, maxRows: 10, bodyColumns: 120 } };

function harness(on: any) {
  const sent: string[] = [];
  on("session.start", ($: any, e: any) => ({ cwd: e.cwd }));
  on("prompt.submit", ($: any, e: any) => {
    if (e.origin?.kind === "plugin") sent.push(e.text);
    return { text: e.text };
  });
  on("turn.complete", () => ({ text: "" }));
  on("ui.render", { component: "AbovePrompt" }, ($: any, e: any) => {
    const { Box } = $.ui.resolve(e);
    return Box({ children: [] });
  });
  return { sent };
}

async function start($: any) {
  await $.session.start({ surface: "terminal", isInteractive: true, cwd: "/work" } as any);
}

async function say($: any, text: string) {
  await $.prompt.submit({ text, wait: false, origin: { kind: "composer" } } as any);
}

async function reply($: any, answer: string) {
  await $.turn.complete({ reason: "answer", answer, durationMs: 1, isAborted: false, turnId: "t" } as any);
}

describe("ask-check", () => {
  test("a question the user already answered shows their sentence and one key sends it", async ($, on) => {
    const h = harness(on);
    await start($);
    await say($, "create the images and then the gamma ... use the sand palette");
    await reply($, "The images are ready.\n\nShould I start the Gamma call with these images?");
    const ui = await $.ui.mount(BAND as any);
    expect(await ui.find({ type: "Text", text: /asked 1 · already answered 1/ })).toBeDefined();
    expect(await ui.find({ type: "Text", text: /you said "create the images and then the gamma" \(prompt 1\)/ })).toBeDefined();
    await ui.press({ key: "send" } as any);
    expect(h.sent).toEqual([`Already answered: "create the images and then the gamma" (my prompt 1). Proceed.`]);
    await ui.unmount();
  });

  test("a standing no-questions instruction answers every question", async ($, on) => {
    harness(on);
    await start($);
    await say($, "override blue and green db ... no other questions ... just do it");
    await reply($, "Done on blue. Shall I add the classes route to the edge proxy too? Should I restart the API?");
    const ui = await $.ui.mount(BAND as any);
    expect(await ui.find({ type: "Text", text: /asked 2 · already answered 2/ })).toBeDefined();
    expect(await ui.find({ type: "Text", text: /you said "no other questions"/ })).toBeDefined();
    await ui.unmount();
  });

  test("a question asked again shows the reply to the first ask", async ($, on) => {
    harness(on);
    await start($);
    await say($, "fix the green slot config");
    await reply($, "For vouchers-ui, is environment.box.ts or environment.prod.ts the green one?");
    await say($, "why don't you look in the hetzner box");
    await reply($, "Still waiting on the one question: is environment.box.ts or environment.prod.ts the green one?");
    const ui = await $.ui.mount(BAND as any);
    expect(await ui.find({ type: "Text", text: /asked before 1/ })).toBeDefined();
    expect(await ui.find({ type: "Text", text: /asked before, you replied "why don't you look in the hetzner box" \(prompt 2\)/ })).toBeDefined();
    await ui.unmount();
  });

  test("an unanswered question is counted without a send key", async ($, on) => {
    harness(on);
    await start($);
    await say($, "make the header collapsible");
    await reply($, "Done. Should the footer collapse as well?");
    const ui = await $.ui.mount(BAND as any);
    expect(await ui.find({ type: "Text", text: /asked 1 · already answered 0/ })).toBeDefined();
    expect(await ui.findAll({ type: "Button" })).toHaveLength(0);
    await ui.unmount();
  });

  test("the band clears on the next prompt and stays away while working", async ($, on) => {
    harness(on);
    await start($);
    await say($, "create the images and then the gamma");
    await reply($, "Should I start the Gamma call with these images?");
    const busy = await $.ui.mount({ ...BAND, props: { ...BAND.props, isWorking: true } } as any);
    expect(await busy.findAll({ type: "Text", text: /asked/ })).toHaveLength(0);
    await busy.unmount();
    await say($, "yes");
    const ui = await $.ui.mount(BAND as any);
    expect(await ui.findAll({ type: "Text", text: /asked/ })).toHaveLength(0);
    await ui.unmount();
  });

  test("question marks in code and pasted-back answer text are ignored", async ($, on) => {
    harness(on);
    await start($);
    await reply($, "Report: the green and blue databases do not have the ionos model catalogue yet.");
    await say($, "the green and blue databases do not have the ionos model catalogue yet ... fix the import");
    await reply($, "Fixed.\n\n```sql\nSELECT * FROM t WHERE x = ?\n```\nWant me to run the catalogue script on green and blue databases too?");
    const ui = await $.ui.mount(BAND as any);
    expect(await ui.find({ type: "Text", text: /asked 1 · already answered 0/ })).toBeDefined();
    await ui.unmount();
  });
});
