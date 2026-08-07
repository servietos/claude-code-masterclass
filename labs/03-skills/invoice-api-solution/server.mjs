import express from "express";
import { renderInvoice } from "./scripts/render.mjs";

const app = express();
app.use(express.json());

app.get("/health", (_req, res) => res.json({ status: "ok" }));

app.post("/invoices", async (req, res) => {
  const buffer = await renderInvoice(req.body);
  res.set({
    "Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "Content-Disposition": `attachment; filename="${req.body.number}.docx"`,
  });
  res.send(buffer);
});

const port = process.env.PORT ?? 3200;
app.listen(port, () => console.log(`invoice api on http://127.0.0.1:${port}`));
