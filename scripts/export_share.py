#!/usr/bin/env python3
"""Export the files listed in share.txt to a folder the team can see.

Scans every listed file first (scripts/sharescan.py: emails, phone numbers, contact
names). Any hit prints file:line and the match, and nothing is copied. On success,
copies the files preserving relative paths and writes EXPORT.md (files, date, commit).

Usage: python3 scripts/export_share.py --dest PATH   (PATH outside the repo, empty or new)
"""
import argparse, os, shutil, subprocess, sys
from datetime import date

sys.dont_write_bytecode = True  # no __pycache__ in the repo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sharescan

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def git(root, *args):
    try:
        return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dest", required=True); ap.add_argument("--root", default=ROOT)
    a = ap.parse_args(); root = os.path.abspath(a.root); dest = os.path.abspath(a.dest)
    if sharescan.load_patterns(root) is None:
        sys.exit(f"export: no {sharescan.ALLOWLIST} in {root}; nothing is shareable")
    if os.path.commonpath([root, dest]) == root:
        sys.exit("export: --dest must be outside the repo")
    if os.path.isdir(dest) and os.listdir(dest):
        sys.exit(f"export: {dest} is not empty; use a new folder so no stale files ride along")

    files, errors = sharescan.check(root)
    if errors:
        for e in errors: print("BLOCKED", e)
        print(f"\nexport: FAILED ({len(errors)} problems); nothing copied"); sys.exit(1)
    if not files:
        sys.exit("export: share.txt matches no files; nothing to export")

    for rel in files:
        os.makedirs(os.path.dirname(os.path.join(dest, rel)) or dest, exist_ok=True)
        shutil.copy2(os.path.join(root, rel), os.path.join(dest, rel))
    commit = git(root, "rev-parse", "HEAD") or "unknown (not a git repo)"
    dirty = git(root, "status", "--porcelain", "--", *files)
    with open(os.path.join(dest, "EXPORT.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# Export\n\n- Date: {date.today()}\n- Commit: {commit}" +
                (" (some exported files have uncommitted changes)" if dirty else "") +
                "\n- Source: scripts/export_share.py, from share.txt\n\n## Files\n" +
                "".join(f"- {rel}\n" for rel in files))
    print(f"export: OK, {len(files)} files to {dest}")
    for rel in files: print("  ", rel)

if __name__ == "__main__":
    main()
