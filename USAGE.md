# Using the repo with an agent

**First:** after cloning, run `sh scripts/install-hooks.sh` once (hooks aren't copied by `git clone`; `new_project.py --here` runs it for you). This installs a pre-commit hook that runs `scripts/check.py` (so a broken repo can't be committed) and copies the skills into `.claude/skills/` so Claude Code triggers them by name. `CLAUDE.md` is read automatically by Claude Code and holds the rules the agent must follow.

**Requires Python 3.7+, standard library only.** Commands here say `python3`. On Windows, if `python3` isn't available (the python.org installer provides `python` and `py`), use `python` or `py -3` instead. The pre-commit hook tries `python3`, then `python`, then `py -3`, and blocks the commit with a clear message if none of them runs. Run `install-hooks.sh` from Git Bash on Windows.

The skills are plain Markdown; they work with any agent that can read files and run a shell.

## Claude Code (recommended)
```
cd <project>-discovery
claude
> Use the intake skill on inbox/<date>-<name>.md
> Use the extract skill on INT-002
> Use the synthesize skill
> Use the weekly-review skill
```
Claude Code discovers skills in `.skills/` if you point it there; simplest is to say
"read .skills/extract/SKILL.md and follow it for INT-002". You can also copy the five
folders into `~/.claude/skills/` so they trigger by name.

## Any chat LLM (no tools)
Paste the SKILL.md you want to run, then paste the file(s) it needs, and ask it to
produce the output. Paste the result back into the repo yourself. Run
`python3 scripts/tally.py` locally for the numbers — never let the model count.

## Order of operations after a conversation
1. Notes → `inbox/` (same day).
2. intake → extract (same day, 10 minutes including your review).
3. Flip `reviewed: yes` in the interview frontmatter once you've checked the quotes.
4. Thank-you email; referral contacted; update the contact file History.
5. Every 4–5 interviews: synthesize.
6. Friday: weekly-review, then hand-write the two reflection lines.

## Adding a hypothesis
Copy an existing block in `hypotheses.md`, next HYP number, status `untested`, empty Log.

## When the tally shows unreviewed interviews
That's the one step that's tempting to skip. Two minutes per interview: read the quotes
against the raw notes, fix any the model polished, then set `reviewed: yes`.

## New idea
In a fresh clone of the template (your private copy):
```
> Run the new-project skill. Idea: <one paragraph>. Name: <name>.
```
It sets the project up in place with `new_project.py --here`, installs the hooks and commits; then `git push`. To scaffold a separate folder instead, give it a destination (`--dest ../<slug>-discovery`), then `cd` there, `git init && sh scripts/install-hooks.sh`, and push it to a new private repo.

## Sharing
The repo stays private. Teammates, mentors or advisors get an exported folder holding only the files listed in `share.txt`. Everything not listed stays private.
- `python3 scripts/coverage.py` regenerates `reports/team-coverage.md`: firm, region, owner and status for every contact. It reads only firm, region, assigned_to and status (region and owner are blank if a contact file lacks them), never names, emails, phones, roles or History. Run it after contact changes and before an export.
- `python3 scripts/export_share.py --dest ../<project>-share-YYYY-MM-DD` scans every `share.txt` file for emails, phone numbers and contact names. If anything is found it prints `file:line` and the match and copies nothing. Otherwise it copies the files and writes `EXPORT.md` with the file list, date and commit. Use a new, empty folder outside the repo each time.
- `check.py` runs the same scan on every commit, and fails if `share.txt` lists anything under `contacts/`, `interviews/`, `inbox/` or `reports/outreach-*`.
- To share something new, add it to `share.txt`. Refer to people as CON-### and to firms by name.
