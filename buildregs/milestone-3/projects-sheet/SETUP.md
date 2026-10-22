# BuildRegs Projects sheet — what exists, and the two steps left

**The sheet:** https://docs.google.com/spreadsheets/d/1j7h3PsEwa_vHIIEmJXexvIoSJUoS81gv4V4YZRPvETQ/edit

File id `1j7h3PsEwa_vHIIEmJXexvIoSJUoS81gv4V4YZRPvETQ`, created 22 Oct 2026 in
the same folder as the price list.

All 42 columns are in place, A to AP, with one example row showing the expected
format of each. `COLUMNS.md` in this folder is the column dictionary.

---

## Both tabs are in place

The Google Sheets connector is not enabled in this session, so this was done
through Make instead: a one-off on-demand scenario calling the Sheets API,
run once, then deleted. Nothing was left behind.

| What | State |
|---|---|
| Tab renamed from Untitled to **Projects** | done |
| Header row frozen and styled | done |
| **Checks** tab added with live formulas | done |

The sheet's own id was not 0 as a first attempt assumed. The real id,
`1631417276`, was read back through the data store, because Make module
outputs cannot be read through the API. The probe record was deleted
afterwards.

### What the Checks tab reads now

| Check | Value |
|---|---|
| Projects recorded | 1 |
| Rows where total does not equal subtotal minus discount plus adjustment | **0** |
| Rows where amount paid does not equal total | **0** |
| Awaiting approval | 1 |

The two zeroes are the controls. Sandeep asked that the quote, the Stripe
amount and the saved record always agree, and those two counts are how that is
checked rather than assumed. Both must stay at zero. Any other number means
something wrote a figure it should not have, and the row can be found by
comparing columns M, O, Q, S and AD.

The ranges are open ended, so they cover rows added later without editing.
The follow-up queue is deliberately not here: the scheduled scenario owns the
dates and the sending, and two implementations could disagree.

Delete the example row once real projects are flowing. The checks ignore it,
because its arithmetic is correct.

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

The sheet is owned by **collsdigital@gmail.com**, so he needs sharing at
minimum, and ownership transferring at handover. Worth doing together with the
price list, which sits in the same folder and has the same issue.

Nothing else is outstanding on the sheet itself.
