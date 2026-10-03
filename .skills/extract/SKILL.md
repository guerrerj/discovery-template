---
name: extract
description: Append a structured, traceable extraction block to an interview file in the discovery repo — pains as verbatim quotes, workarounds, tools they pay for, commitments, asks owed, referrals, vocabulary. Use after intake whenever an interview file has `extracted: no`, or when the user asks to "process", "extract", "structure", or "pull the insights out of" an interview. Also use when the user pastes raw notes and asks what they mean.
---

# Extract

Purpose: do the tedious, skippable step reliably — turn raw notes into fields the tally script and the synthesize skill can use — while keeping every item traceable to the interview and the customer's own words.

## Steps

1. Read the interview file's frontmatter and `## Raw notes`. Note the persona; it changes what counts as a pain (a front-line user's pains are day-to-day tasks; a manager's are reporting, cost and staffing).

2. Append the block below after the raw notes. Use exactly these headings — `scripts/tally.py` parses them.

3. Set `extracted: yes` in the frontmatter. Leave `reviewed: no`; the human flips it after checking.

4. Report: the one-line summary, the count of pains and commitments, and anything you weren't sure about.

## Block format (use verbatim)

```
## Extraction (INT-###, extracted YYYY-MM-DD, needs review)

### Summary
- One sentence: who they are and the single most important thing they said.

### Pains (verbatim or marked ~paraphrase)
- "…" — context in a few words
- ~paraphrase: … — context

### Unprompted vs prompted
- Raised by them before we steered: …
- Raised only after we asked: …

### Workarounds they built
- …

### Tools they pay for
- Tool — what it's used for — anything they said about it

### Current process (steps, in their words where possible)
1. …

### Commitments obtained
- [artifact] what they agreed to share
- [intro] who they offered to introduce
- [follow-up] a second meeting or check-in they agreed to
- [pilot] / [prepay] if any
- [come-back] said "come back when it exists" or equivalent
(one line per commitment, tag in square brackets first; omit tags that don't apply)

### Asks I owe them
- YYYY-MM-DD | what I promised | open

### They owe me
- YYYY-MM-DD | what they said they'd send or do | open

### Referrals given
- Name, role, firm, how to reach — and whether we may use the interviewer's name

### Vocabulary (their words for things)
- term — what they mean by it

### Contradicts or complicates our thinking
- …

### Candidate insights
- Short pattern statement — bears on HYP-### (proposal only; synthesize decides)
```

## Rules

- **Verbatim means verbatim.** If the notes are rough, quote the rough phrase and add context after the dash. Use `~paraphrase:` when you must reconstruct. Never polish a quote into something they didn't say.
- **Unprompted matters most.** The notes usually show where the interviewer steered; anything the customer raised before that point goes in "Raised by them". If you can't tell, say so.
- **A commitment is something they gave up**: time, reputation, an artifact, money. "Sounds great" is not a commitment. "Happy to chat again once you have something" is `[come-back]`. "I'll send you the spreadsheet we use" is `[artifact]` and also a `They owe me` line.
- **Open loops get dates.** Use the interview date if no other date is stated. The weekly review sorts by these.
- **Don't decide insights here.** Propose candidates; the synthesize skill checks them against existing insights so we don't create duplicates.
- **When the notes are thin**, the block is thin. Don't fill sections to look complete.

## Before finishing
Run `python3 scripts/check.py`; fix or report failures. Commit with a message naming this skill and the IDs touched. Print the list of changed files.
