# Rules for any agent working in this repo

These are not suggestions. If a step below conflicts with what the user asks, do what the user asks only after saying which rule it breaks.

## Data integrity
1. **Raw notes are immutable.** Never edit anything under `## Raw notes` in an interview file after intake. The intake skill records `raw_sha` in the frontmatter; `scripts/check.py` fails if the raw section no longer matches it.
2. **Numbers come from `scripts/tally.py` only.** Never count interviews, commitments, open loops or replication by reading files. If asked for a number, run the script and quote it. If the script doesn't produce it, answer "not tracked".
3. **Every claim carries an ID.** In insights, hypothesis logs and reports, any statement about what a customer said cites `INT-###`; any statement about a pattern cites `INS-###`. A sentence without an ID is labelled "(opinion)".
4. **Quotes are verbatim.** Rough phrasing from the notes stays rough. Reconstructed wording is prefixed `~paraphrase:`. Never polish a quote.
5. **No invented dates, emails, names or firms.** Leave the field blank and say what's missing.

## Workflow
6. **Run `python3 scripts/check.py` before finishing any turn that changed files.** If it fails, fix the problem or report it; never report success with a failing check.
7. **Commit after each skill step** with a message naming the skill and the IDs touched, e.g. `extract: INT-002`. If git isn't initialised, say so once and continue.
8. **Show what changed.** After writing, print `git diff --stat` (or list the files) so the user can review before moving on.
9. **Referrals do not become contacts automatically.** They are recorded in the interview's `### Referrals given`; a contact file is created only when the user says they're reaching out.
10. **Unextracted or unreviewed interviews are flagged at the start of every session** (the check script prints them). Offer to extract; do not run synthesize while any interview is unextracted.
11. **Kill rule is reported, not interpreted.** State the three counters and MET / not yet. Do not say the project is "on track" or "going well".

## Scope
12. **No product work in this repo.** No feature lists, mockups, architecture or code for the product itself. If the user asks, remind them of the kill rule status and put the idea in `reports/parking-lot.md` (create it if missing).
13. **Don't run outreach.** Draft emails if asked; never send anything, never contact anyone.
14. **Don't reorganise.** No renaming files, changing IDs, moving sections or "tidying" the repo unasked.

## Sharing
15. **Sharing boundary.** Only files listed in `share.txt` leave this repo, via `scripts/export_share.py`. Never write people's names, emails or phone numbers into a `share.txt` file; refer to people by contact ID (CON-###); firm names are allowed in team exports. Anything shared outside the team (mentors, investors, public) must be anonymised: no names, firms or contact details, and no quote that identifies who said it. Never add `contacts/`, `interviews/` or `inbox/` to `share.txt`.

## Skills
The method lives in `.skills/*/SKILL.md` (mirrored in `.claude/skills/` if the user copied them). Read the relevant SKILL.md before acting; do not improvise a different process because it seems faster.
