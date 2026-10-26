#!/usr/bin/env python3
"""Apply a guarded SQL delta to a local dev database twice and prove it is idempotent.

Runs the script with Windows auth through sqlcmd (-E -C -f 65001 -b -W -i), then runs it again,
and compares the two runs: the second must exit 0, report no affected rows before the closing
verification SELECT, and print the same verification block as the first.

    python apply-dev-delta.py --database Vouchers-Dev --script infra/db/schema-changes/x.sql
    python apply-dev-delta.py --database Vouchers-Dev --script x.sql --dry-run

Summary line: runs=N exit=N first_writes=N second_writes=N verify_identical=yes|no idempotent=yes|no
Exit code 0 only when idempotent=yes.
"""
import argparse
import os
import re
import subprocess
import sys

AFFECTED = re.compile(r"^\((\d+) rows? affected\)\s*$", re.M)


def command(args, path):
    return ["sqlcmd", "-S", args.server, "-E", "-C", "-f", "65001", "-b", "-W", "-d", args.database, "-i", path]


def run(args, path):
    p = subprocess.run(command(args, path), capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout + p.stderr


def last_block(out):
    lines = out.splitlines()
    seps = [i for i, line in enumerate(lines) if line.strip() and set(line.strip()) <= set("- ")]
    if not seps or seps[-1] == 0:
        return ""
    return "\n".join(line.rstrip() for line in lines[seps[-1] - 1:]).strip()


def writes(out, final):
    body = out[: out.rfind(final)] if final and final in out else out
    return sum(int(n) for n in AFFECTED.findall(body))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--database", required=True)
    ap.add_argument("--script", required=True)
    ap.add_argument("--server", default=".")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.isfile(args.script):
        print(f"script not found: {args.script}", file=sys.stderr)
        return 2
    path = os.path.abspath(args.script)

    if args.dry_run:
        print("would run twice: " + " ".join(command(args, path)))
        print("runs=0 dry_run=yes")
        return 0

    rc1, out1 = run(args, path)
    if rc1:
        print(out1)
        print(f"runs=1 exit={rc1} first_writes=? second_writes=? verify_identical=no idempotent=no")
        return 1

    rc2, out2 = run(args, path)
    f1, f2 = last_block(out1), last_block(out2)
    w1, w2 = writes(out1, f1), writes(out2, f2)
    same = f1 == f2
    ok = rc2 == 0 and w2 == 0 and same
    if rc2:
        print(out2)
    print("--- verification, run 2")
    print(f2)
    print(f"runs=2 exit={rc2} first_writes={w1} second_writes={w2} verify_identical={'yes' if same else 'no'} idempotent={'yes' if ok else 'no'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
