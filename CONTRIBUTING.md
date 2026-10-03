# Contributing

How we work in a discovery repo. `CLAUDE.md` holds the full rules for agents; these are the ones people need to know.

1. **Install the hooks after you clone.** Run `sh scripts/install-hooks.sh` once. It adds a pre-commit hook that runs `scripts/check.py`, so a broken repo can't be committed, and copies the skills into `.claude/skills/`.
2. **One person runs intake.** Whoever held the conversation drops the notes in `inbox/` and runs intake. Nobody else creates interview or contact files for that conversation, so IDs never collide.
3. **Never edit raw notes.** Everything under `## Raw notes` is sealed by `raw_sha` at intake. To correct something, fix the extraction block or add a note; `check.py` fails if the raw section changes.
4. **Review within 24 hours.** After extract runs, the person who held the conversation checks the quotes against the raw notes, fixes anything polished, and sets `reviewed: yes`.
5. **Commit per skill step.** One commit per intake, extract, synthesize or weekly-review, with a message naming the skill and the IDs touched (e.g. `extract: INT-004`).
6. **Data repos stay private.** Interview notes and contact details are given in confidence. A project's discovery repo is never made public. Teammates get only the files in `share.txt`, exported with `scripts/export_share.py`; those may name firms but never people, emails or phone numbers. Anything shared outside the team (mentors, investors, public) must be anonymised: no names, firms or contact details, and no quote that identifies who said it.
