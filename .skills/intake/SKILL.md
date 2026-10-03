---
name: intake
description: Turn raw material in inbox/ (typed interview notes, call transcripts, email threads, voice-memo transcripts) into a contact file and an interview file in the discovery repo. Use whenever the user says they had a call, meeting, or conversation with a customer, dropped notes in the inbox, or asks to "log" or "file" an interview — even if they only paste notes into chat. Never edits raw notes.
---

# Intake

Purpose: get a raw conversation into the repo with a stable ID and correct frontmatter, without changing a word of the notes. Everything downstream (extraction, insights, tally) depends on this being done consistently.

## Steps

1. **Find the material.** Look in `inbox/` for new `.md`/`.txt` files, or use text the user pasted. One file = one conversation. If a file holds several conversations, split it.

2. **Identify the contact.** Search `contacts/` by name and firm. If found, use their `CON-###`. If not, create one from `templates/contact.md` with the next free number (`ls contacts/` and take max+1), named `contacts/CON-###-firstname-lastname.md` (lowercase, hyphenated; use `CON-###-<firm-slug>.md` if no person is named). Fill what the material tells you: name, firm, role, persona (see below), source (`cold` / `referral:CON-###` / `intermediary:CON-###` / `warm:<teammate>`). Leave unknown fields blank rather than guessing. Set `status: interviewed` and add a History line `YYYY-MM-DD — interviewed (INT-###)`.

3. **Create the interview file** `interviews/INT-###.md` from `templates/interview.md` (next free number). Fill the frontmatter: id, contact, name, firm, persona, date, format, duration if known, source, `recorded: yes/no`, `extracted: no`, `reviewed: no`.

4. **Paste the raw notes verbatim** under `## Raw notes`. Do not clean up spelling, reorder, or summarise. If the source was an email thread, keep the thread; if a transcript, keep speaker labels. The raw block is the evidence; the extract skill works from it and the human checks against it.

5. **Seal the raw notes**: run `python3 scripts/check.py --seal INT-###`. This writes `raw_sha` into the frontmatter; from now on any change to the raw section fails the check.

6. **Move the inbox file** to `inbox/processed/` (create if needed) so it isn't ingested twice.

7. **Run `python3 scripts/check.py`** and fix anything it reports.

8. **Report** in one line: `Created INT-007 for CON-005 (Name, Firm, persona). Run extract next.`

## Persona rules

- `<persona>` — (filled per project by the new-project skill: job titles and role descriptions that count as this persona)
- `intermediary` — association staff, consultants who refer, instructors. Their interviews count for context but the kill rule's commitments come from every other persona.

If a person straddles (e.g. "Owner/Manager"), pick the persona that matches what they mostly talked about and note the other in the contact's role field.

## Don'ts

- Don't extract or summarise here; that's the extract skill.
- Don't create a contact for people merely mentioned in the notes (referrals). Referrals are captured by extract and become contacts when you actually reach out.
- Don't invent dates. If the date isn't in the material, ask.

## Before finishing
Run `python3 scripts/check.py`; fix or report failures. Commit with a message naming this skill and the IDs touched (e.g. `intake: INT-007, CON-005`). Print the list of changed files.
