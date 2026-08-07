#!/usr/bin/env bash
set -uo pipefail

node --import tsx --import ./stub/register.mjs src/06-ci-check.ts
exit $?
