# Harden Newsletter — Lab Starter

A drafting agent reads weekly customer feedback, picks three accounts to feature, drafts a newsletter, and runs the publish step. The starter ships with the data the agent needs and none of the security wiring it deserves.

## What Is Here

```text
harden-newsletter/
├── readme.md
├── untrusted/
│   └── customer-feedback.md
├── data/
│   └── customers.csv
└── .env.example
```

## What Is Missing

No hooks, no sub-agent scopes, no secrets policy, no observability cap. Your job in the lab is to wire all four.

## Before You Start

Copy `.env.example` to `.env` so the agent has something to read; the values are fake, none of them work, that is intentional.

```bash
cp .env.example .env
```

```powershell
Copy-Item .env.example .env
```
