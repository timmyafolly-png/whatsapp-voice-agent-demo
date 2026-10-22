# BuildRegs Projects sheet — what exists, and the two steps left

**The sheet:** https://docs.google.com/spreadsheets/d/1j7h3PsEwa_vHIIEmJXexvIoSJUoS81gv4V4YZRPvETQ/edit

File id `1j7h3PsEwa_vHIIEmJXexvIoSJUoS81gv4V4YZRPvETQ`, created 22 Oct 2026 in
the same folder as the price list.

All 42 columns are in place, A to AP, with one example row showing the expected
format of each. `COLUMNS.md` in this folder is the column dictionary.

---

## Two steps to finish, by hand

The Google Sheets connector is not enabled in this session, only Drive, so the
data tab was created but tabs cannot be added or renamed through the API. Both
of these are quick.

### Step 1: rename the tab

The tab is currently called **Untitled**. Rename it to **Projects**. The
formulas below reference that name, and so will the Make modules.

### Step 2: add a Checks tab

New tab called **Checks**. Paste this into A1, then put the formulas in column B.

| A | B |
|---|---|
| Projects recorded | `=COUNTA(Projects!A2:A)` |
| Rows where the total does not equal subtotal minus discount plus adjustment | `=SUMPRODUCT((Projects!$A$2:$A<>"")*(ABS(Projects!$S$2:$S-(Projects!$M$2:$M-Projects!$O$2:$O+Projects!$Q$2:$Q))>0.005))` |
| Rows where the amount paid does not equal the total | `=SUMPRODUCT((Projects!$AD$2:$AD<>"")*(ABS(Projects!$AD$2:$AD-Projects!$S$2:$S)>0.005))` |
| Awaiting approval | `=COUNTIF(Projects!$C$2:$C,"Awaiting approval")` |
| Approved | `=COUNTIF(Projects!$C$2:$C,"Approved")` |
| Quote sent | `=COUNTIF(Projects!$C$2:$C,"Quote sent")` |
| Paid | `=COUNTIF(Projects!$C$2:$C,"Paid")` |
| Awaiting information | `=COUNTIF(Projects!$C$2:$C,"Awaiting information")` |
| In production | `=COUNTIF(Projects!$C$2:$C,"In production")` |
| Ready for review | `=COUNTIF(Projects!$C$2:$C,"Ready for review")` |
| Delivered | `=COUNTIF(Projects!$C$2:$C,"Delivered")` |

The first three rows are the ones that matter. Sandeep asked that the quote, the
Stripe amount and the saved record always agree. Those two counts are how that
gets checked rather than assumed, and both should read **0** at all times. Any
other number means something wrote a figure it should not have.

The ranges are open ended, so they cover rows added later without editing.

Delete the example row once real projects are flowing. Both checks ignore it
anyway, because its arithmetic is correct.

**The follow-up queue is deliberately not in the sheet.** Working out which jobs
are due a three or seven day email is done by the scheduled Make scenario, which
owns the dates and the sending. Duplicating that as sheet formulas would give two
answers that could disagree.

---

## Status values

Use exactly these, in this order of progress:

```
Draft
Awaiting approval
Approved
Quote sent
Paid
Awaiting information
In production
Ready for review
Delivered
Declined
```

`awaiting_information` in column AO is a separate yes or no flag, because a job
can be paid and waiting on information at the same time. The status says where
the job is; the flag says whether the clock is running.

---

## How Make uses this sheet

**One row per project, keyed on `quote_reference` in column A.** Never keyed on
the customer, which is what makes an architect with four jobs work properly.

| Stage | What it does to the row |
|---|---|
| Enquiry arrives | Creates the row with the customer, the property and the folders. Status `Draft` |
| Review page opened | Reads the row to prefill |
| Save draft | Updates the priced fields. Status stays `Draft`. **Sends nothing** |
| Approve | Writes `approved_at` and the token, sets status `Approved` |
| Quote sent | Writes `stripe_session_id` and `quote_sent_at`, status `Quote sent` |
| Payment confirmed | Writes the Stripe fields and `paid_at`, status `Paid` |
| Handover | Writes `handover_sent_at` after payment only |
| Ready for review | Writes `ready_for_review_at` |
| Delivered | Writes `approved_output_url` and `delivered_at` |
| Follow-ups | Writes `checkin_sent_at` and `review_request_sent_at` |

**Two rules the row enforces:**

The `total` in column S is written once and read from there by both the
quotation email and the Stripe amount. Nothing is typed twice, so they cannot
drift apart.

`approved_output_url` in column AA points at an approved-output subfolder only,
never the folder holding working files. That is a folder convention, so a
sharing mistake cannot expose drafts.

**Dates are written as `YYYY-MM-DD HH:mm:ss`** by Make, and Make does all date
arithmetic. The sheet does not depend on parsing them, which is why no formula
above reads a date.

---

## Before Sandeep sees it

- The sheet is owned by **collsdigital@gmail.com**, so he needs sharing at
  minimum, and ownership transferring at handover. Worth doing together with
  the price list, which is in the same folder and has the same issue.
- Rename the tab and add the Checks tab first, so the first thing he opens
  reads properly.
