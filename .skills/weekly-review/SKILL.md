---
name: weekly-review
description: Generate the Friday discovery note for the repo — tally, interviews this week, insight and hypothesis changes, open loops oldest first, kill-rule status — and leave the two hand-written reflection lines blank. Use on Fridays, when the user says "weekly", "where are we", "status", "what do I owe people", or before a team/mentor update. Also use to list open loops at any time.
---

# Weekly review

Purpose: ten minutes on Friday that keeps commitments from dying in email, shows kill-rule progress honestly, and leaves a record of how the thinking changed.

## Steps

1. **Run** `python3 scripts/tally.py --json`. All numbers in the note come from this output.

2. **Create** `reports/week-YYYY-MM-DD.md` from `templates/weekly.md` (date = this Friday).

3. **Fill each section:**
   - *Tally*: interviews total and by persona, contacts by status, commitments by type, unextracted/unreviewed IDs (nag if any).
   - *Interviews this week*: IDs with name/firm/persona and the one-line summary from each extraction block.
   - *New or strengthened insights*: from `insights/` files changed this week (check `last_updated`); note count changes.
   - *Hypothesis changes*: any Log lines in `hypotheses.md` dated this week.
   - *Open loops*: two lists from the tally, oldest first. Flag anything older than 5 days in bold. Also flag, as "thank-you not recorded", any interview dated this week whose "Asks I owe them" section has no thank-you line.
   - *Kill-rule status*: the three counters and MET / not yet, plus replicated insights.
   - *Next week*: proposed — who to contact (from contacts with status `identified`/`contacted` and overdue `next_action_date`), which interviews to extract, whether a synthesis is due (every 4–5 interviews).

4. **Leave blank** "What surprised me" and "What I'm avoiding". These are the user's, hand-written; the value of the note is that they're answered honestly, not that they're filled.

5. **Report** the open loops and kill-rule line in chat, and ask the user to fill the two blanks.

## Rules

- Never invent a number. If the tally doesn't have it, say "not tracked".
- Don't editorialise about progress. State counts; the user judges.
- If the tally's kill-rule interview count is ≥ 15 (the first number in `kill_rule.interviews`, e.g. `15/15`, from `tally.py --json`) and `kill_rule.met` is false, say so plainly at the top of the note.

## Before finishing
Run `python3 scripts/check.py`; fix or report failures. Commit with a message naming this skill and the IDs touched. Print the list of changed files.
