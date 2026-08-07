#!/usr/bin/env bash
set -uo pipefail

npx tsx src/06-ci-check.ts
exit $?
