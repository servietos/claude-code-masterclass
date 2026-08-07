import { z } from "zod";

export const FindingSchema = z.object({
  line: z.number().int().nullable(),
  severity: z.enum(["critical", "high", "medium", "low"]),
  summary: z.string(),
  recommendation: z.string(),
});

function reviewSchema<T extends "security" | "performance" | "style">(name: T) {
  return z.object({
    reviewer: z.literal(name),
    findings: z.array(FindingSchema),
    overall_verdict: z.enum(["block", "comment", "approve"]),
  });
}

export type ReviewerName = "security" | "performance" | "style";

export type ReviewerConfig = {
  name: ReviewerName;
  systemPrompt: string;
  reviewerSchema: ReturnType<typeof reviewSchema>;
};

export const securityReviewer: ReviewerConfig = {
  name: "security",
  systemPrompt:
    "You are a security code reviewer. Focus exclusively on security issues: injection vulnerabilities, weak cryptography, missing authentication checks, insecure storage of secrets, weak session validation. Ignore performance and style, other reviewers cover those. Be specific: cite the line number and the exact attack scenario.",
  reviewerSchema: reviewSchema("security"),
};

export const performanceReviewer: ReviewerConfig = {
  name: "performance",
  systemPrompt:
    "You are a performance code reviewer. Focus exclusively on performance issues: unbounded data structures, missing pagination, N+1 queries, blocking calls in hot paths, missed caching opportunities or caches that grow without bound. Ignore security and style. Cite line numbers and quantify the impact when possible.",
  reviewerSchema: reviewSchema("performance"),
};

export const styleReviewer: ReviewerConfig = {
  name: "style",
  systemPrompt:
    "You are a code-style and correctness reviewer. Focus on type safety (any, unknown, loose types), naming, dead code, incorrect control flow, and broken edge-case handling. Do NOT report security or performance issues, those are covered. Cite line numbers.",
  reviewerSchema: reviewSchema("style"),
};

export const reviewers: ReviewerConfig[] = [
  securityReviewer,
  performanceReviewer,
  styleReviewer,
];

export type Review = z.infer<ReturnType<typeof reviewSchema>>;

export function parseJsonBlock(raw: string): unknown {
  const text = raw.trim().replace(/^```(?:json)?\s*/i, "").replace(/```$/i, "");
  return JSON.parse(text);
}
