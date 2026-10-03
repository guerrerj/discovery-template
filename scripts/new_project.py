#!/usr/bin/env python3
"""Scaffold a fresh discovery repo for a new idea from this one.

Two modes:
  --here   turn this repo (a fresh clone of the template) into the project in place:
           apply the project rewrites, install the hooks and make one commit
           "new-project: <name>". Refuses if it has already been run or if the
           data folders already hold anything.
  --dest   (advanced) copy the method into a new folder and scaffold it there;
           you then git init it, install the hooks and push it yourself.

Either way it creates empty data folders (contacts, interviews, insights, reports, inbox),
sets the persona list in every place it lives, and writes a project-specific README, a
project.md stub, a hypotheses.md holding only the header and a kill rule naming the
personas, and a default share.txt (the sharing allowlist for scripts/export_share.py; the
scripts, the share scan in check.py and CLAUDE.md's sharing rule come with the method).
The new-project skill then fills project.md, hypotheses.md and the persona rules with
domain content, and confirms the share.txt allowlist with the user.

Usage:
  python3 scripts/new_project.py --here --name "Climb Desk" --slug climbing \
      --personas owner,manager,front-desk,setter,member,intermediary
  python3 scripts/new_project.py --name "Climb Desk" --slug climbing \
      --personas owner,manager,intermediary --dest ../climbing-discovery
"""
import argparse, os, re, shutil, subprocess, sys
from datetime import date

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPY = ["USAGE.md", "CLAUDE.md", "CONTRIBUTING.md", "LICENSE", ".gitignore", ".gitattributes", "guides", "templates", "scripts", ".skills"]
# Every file this script writes uses newline="\n", so Windows doesn't produce CRLF; .gitattributes keeps it LF in git.
EMPTY_DIRS = ["inbox/processed", "contacts", "interviews", "insights", "reports"]
DATA_DIRS = ["contacts", "interviews", "insights"]
PLACEHOLDER = "# <Project name> — project brief"  # first line of the template's project.md; gone once scaffolded

def rewrite(path, fn):
    with open(path, encoding="utf-8") as f: s = f.read()
    s2 = fn(s)
    if s2 != s:
        with open(path, "w", encoding="utf-8", newline="\n") as f: f.write(s2)

def git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)

def refuse_here(root):
    """Return a reason --here must not run in `root`, or None."""
    if not os.path.isdir(os.path.join(root, ".git")):
        return f"{root} is not a git repo. Clone your private copy of the template first, then run --here inside it."
    pm = os.path.join(root, "project.md")
    if not os.path.isfile(pm):
        return "project.md is missing, so this doesn't look like a fresh template clone."
    with open(pm, encoding="utf-8") as f:
        if not f.read().lstrip().startswith(PLACEHOLDER):
            return "new_project.py has already been run here (project.md is no longer the template placeholder). Nothing changed."
    for d in DATA_DIRS:
        p = os.path.join(root, d)
        extra = [f for f in (os.listdir(p) if os.path.isdir(p) else []) if f != ".gitkeep"]
        if extra:
            return f"{d}/ already contains {len(extra)} file(s) besides .gitkeep; --here only runs on a fresh template clone. Nothing changed."
    st = git(root, "status", "--porcelain")
    if st.returncode != 0:
        return "git status failed; is git installed and on PATH?"
    if st.stdout.strip():
        return "the working tree has uncommitted changes; commit or discard them first so the new-project commit holds only the scaffold. Nothing changed."
    return None

def scaffold(dest, a, personas, here):
    """Apply the project rewrites in `dest`. In --dest mode, copy the method there first."""
    if not here:
        os.makedirs(dest)
        for item in COPY:
            s = os.path.join(SRC, item); d = os.path.join(dest, item)
            (shutil.copytree if os.path.isdir(s) else shutil.copy2)(s, d)
    for dname in EMPTY_DIRS:
        os.makedirs(os.path.join(dest, dname), exist_ok=True)
        open(os.path.join(dest, dname, ".gitkeep"), "w").close()  # git doesn't track empty folders
    pset = "{" + ", ".join(f'"{p}"' for p in personas) + "}"
    hint = " | ".join(personas)

    rewrite(os.path.join(dest, "scripts", "check.py"), lambda s: re.sub(r"PERSONAS = \{[^}]*\}", f"PERSONAS = {pset}", s))
    for t in ("contact.md", "interview.md"):
        rewrite(os.path.join(dest, "templates", t), lambda s: re.sub(r"persona: .*", f"persona: {hint}", s))
    rewrite(os.path.join(dest, "templates", "insight.md"), lambda s: re.sub(r"persona_scope: \[.*\]", f"persona_scope: [{', '.join(personas)}]", s))
    # intake persona rules → placeholder for the skill to fill
    # Replace only the `<persona>` placeholder line, so the intermediary description and the straddle tie-break survive.
    rules = "\n".join(f"- `{p}` — (fill in: who counts as this persona)" for p in personas if p != "intermediary")
    rewrite(os.path.join(dest, ".skills", "intake", "SKILL.md"),
            lambda s: re.sub(r"^- `<persona>` — .*$", lambda m: rules, s, count=1, flags=re.M))
    # CLAUDE.md / USAGE: project name
    rewrite(os.path.join(dest, "CLAUDE.md"), lambda s: s.replace("for the product itself", f"for {a.name} itself"))
    rewrite(os.path.join(dest, "USAGE.md"), lambda s: s.replace("<project>-discovery", os.path.basename(dest)).replace("<project>-share-", f"{a.slug}-share-"))
    # share.txt: default allowlist; the new-project skill confirms it with the user
    with open(os.path.join(dest, "share.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("""# share.txt — the allowlist for scripts/export_share.py.
# Everything NOT listed here is private and never leaves this repo.
# One path or glob per line, relative to the repo root; # starts a comment.
# Never list contacts/, interviews/, inbox/ or reports/outreach-* (check.py blocks it).
# Listed files must not contain names, emails or phone numbers: refer to people as CON-###.

hypotheses.md
guides/*.md
reports/synthesis-*.md
reports/team-coverage.md
""")
    named = ", ".join(p for p in personas if p != "intermediary")
    # hypotheses: header + kill rule naming the personas + one placeholder
    with open(os.path.join(dest, "hypotheses.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"""# Hypotheses

Status: untested | supported (weak) | supported | contradicted | mixed. Every status change cites insight IDs and the date.

## Kill rule
- Target: 15 interviews across: {named} (plus intermediaries for referrals).
- Pass: ≥3 "come back when it exists" AND ≥1 artifact shared, pilot or prepay.
- Checked: every Friday via `scripts/tally.py`.

<!-- Before interview one: write HYP-001.. from project.md. Each hypothesis needs **Statement:**, **Status:** untested, **Evidence:** —, **Log:** (empty). Phrase each so an interview can contradict it. -->
""")
    # README: project-specific; says the MIT LICENSE covers the method only, not the project data
    with open(os.path.join(dest, "README.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"""# {a.name} — customer discovery

Scaffolded from discovery-template on {date.today()}. Interview notes and contact details here are given in confidence; keep this repo private (see `CONTRIBUTING.md`).

Personas: {", ".join(personas)}. The idea and kill rule are in `project.md`; hypotheses in `hypotheses.md`.

## The loop
1. After a conversation, put the raw notes in `inbox/` the same day.
2. **intake** creates or updates the contact and the interview file; raw notes are sealed and never edited.
3. **extract** appends the structured block; whoever held the conversation reviews it within 24 hours and sets `reviewed: yes`.
4. Every 4–5 interviews, **synthesize** links pains to insights and updates hypothesis statuses.
5. Fridays, **weekly-review** runs `scripts/tally.py` and writes the week's note with open loops and kill-rule status.

Numbers come only from `scripts/tally.py`. See `USAGE.md` for how to drive the skills with an agent.

## Licence
The MIT licence in LICENSE covers the method and scripts only. Your project data (contacts, interviews, insights, reports) is not licensed for sharing. Keep this repo private.
""")
    with open(os.path.join(dest, "project.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"""# {a.name} — project brief

*Created {date.today()} by new_project.py. The new-project skill fills this from the founder's description.*

## The idea (one paragraph, the founder's words)

## Who has the problem (personas, one line each)
{chr(10).join(f'- **{p}** — ' for p in personas if p != 'intermediary')}
- **intermediary** — associations, consultants, suppliers who can refer us

## What we think the pain is (our guess, to be tested)

## Who we think pays, and why

## Known alternatives and incumbents

## What would kill it

## Kill rule
15 interviews across: {named} (plus intermediaries); ≥3 "come back when it exists"; ≥1 artifact shared, pilot or prepay.
""")

def finish_here(root, name):
    """Install the hooks and make the single new-project commit."""
    try:
        r = subprocess.run(["sh", "scripts/install-hooks.sh"], cwd=root, capture_output=True, text=True)
    except OSError:
        sys.exit("scaffolded, but 'sh' wasn't found to install the hooks. Run `sh scripts/install-hooks.sh` from Git Bash, then "
                 f"`git add -A && git commit -m \"new-project: {name}\"`.")
    if r.returncode != 0:
        sys.exit(f"scaffolded, but installing the hooks failed:\n{r.stdout}{r.stderr}")
    git(root, "add", "-A")
    c = git(root, "commit", "-q", "-m", f"new-project: {name}")  # the pre-commit hook runs check.py here
    if c.returncode != 0:
        sys.exit(f"scaffolded and hooks installed, but the commit failed:\n{c.stdout}{c.stderr}\n"
                 "If git asks who you are, set `git config user.name` and `git config user.email`, then "
                 f"`git commit -m \"new-project: {name}\"`.")
    return git(root, "log", "--oneline", "-1").stdout.strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="project display name")
    ap.add_argument("--slug", required=True, help="short id, e.g. climbing")
    ap.add_argument("--personas", required=True, help="comma-separated, e.g. owner,manager,intermediary")
    where = ap.add_mutually_exclusive_group(required=True)
    where.add_argument("--here", action="store_true", help="turn this template clone into the project in place, and commit")
    where.add_argument("--dest", help="(advanced) destination folder for a separate copy (must not exist)")
    a = ap.parse_args()
    personas = [p.strip() for p in a.personas.split(",") if p.strip()]
    if "intermediary" not in personas: personas.append("intermediary")

    if a.here:
        why = refuse_here(SRC)
        if why: sys.exit(f"new_project.py --here: {why}")
        scaffold(SRC, a, personas, here=True)
        commit = finish_here(SRC, a.name)
        print(f"project set up in place: {SRC}\n  personas: {personas}\n  hooks installed; committed {commit}\n"
              "  next: run the new-project skill to fill project.md, hypotheses.md and intake persona rules; confirm share.txt; then git push")
        return

    dest = os.path.abspath(a.dest)
    if os.path.exists(dest): sys.exit(f"{dest} already exists")
    scaffold(dest, a, personas, here=False)
    print(f"scaffolded {dest}\n  personas: {personas}\n  next: run the new-project skill to fill project.md, hypotheses.md and intake persona rules; confirm share.txt; then git init && sh scripts/install-hooks.sh")

if __name__ == "__main__":
    main()
