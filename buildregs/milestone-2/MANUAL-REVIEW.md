# Manual Review Required — Phase 2 quote gate

Deployed 2 Oct 2026 to scenario **7229882 — BuildRegs Phase 2 — Quote Builder to Stripe**.
Scenario remains **inactive**, per the standing hold on automated quotation sending
until the controlled end-to-end test passes.

## What Sandeep asked for

A sixth Quote Status option, `Manual Review Required`, written by the automation when
a quotation needs human approval rather than going out automatically. He added the
option to the FluentCRM field himself (confirmed by screenshot, 2 Oct — the Quote
Status row now reads Draft / Quote Sent / Payment Pending / Paid / Declined /
Manual Review Required).

## When review is triggered

Three conditions, OR'd. All are "the system cannot price this confidently" — none of
them is a business threshold I invented.

| # | Condition | Why |
| --- | --- | --- |
| 1 | No standard price in the price list for the submitted project type | Nothing to quote from |
| 2 | Price list column C (Bespoke) = `Yes`, case-insensitive | Priced per job by a human by design |
| 3 | Calculated final price is zero or negative | Bad arithmetic or missing input |

**An adjustment amount deliberately does not trigger review.** The Quote Builder is
a staff tool; an adjustment entered there *is* the human judgement. Flagging it for
review would mean every adjusted quote needs approving twice.

If Sandeep wants a cap as well — "review anything adjusted by more than £X", or
"review anything over £Y" — that is a fourth condition and a one-line change to the
`reviewNeeded` formula. It needs a number from him, so it is not in.

## How it is built

```
1 webhook -> 8 price list -> 3 standardPrice -> 11 finalPrice -> 4 projectRef
  -> 20 decide (reviewNeeded, reviewReason)
  -> 50 ROUTER
       route A  [reviewNeeded = yes]  51 CRM: Manual Review Required -> 52 team email
       route B  [reviewNeeded = no ]  5 CRM: Quote Sent -> 16 pence -> 15 Stripe -> 7 client email
```

Both routes carry an explicit filter rather than one filter and a fallback. A Make
router sends the bundle down *every* route whose filter passes, and an unfiltered
route always passes — so a bare fallback would have fired on every single run,
quoting automatically even when review was required. The two filters are mutually
exclusive by construction.

On the review route **no Stripe session is created and no quotation email reaches
the client**. The job stops at the CRM flag plus a team email.

The decision lives in module 20 as a variable rather than inline in the router
filters, so the rule is readable in one place and the filters stay as
`reviewNeeded = yes` / `= no`.

```
reviewNeeded =
  if(length(trim(ifempty(8.`1`; ""))) = 0; "yes";
  if(lower(trim(ifempty(8.`2`; ""))) = "yes"; "yes";
  if(parseNumber(11.finalPrice) > 0; "no"; "yes")))
```

`reviewReason` mirrors the same branches and carries the plain-English explanation
into the team email, so whoever picks the job up is told why it stopped.

## Test evidence

Run in scenario 7636164 (on-demand harness), execution `f5dea4d4a32a402c96dc604148d43ae0`,
2 ops, SUCCESS. Six synthetic cases evaluated through the exact deployed formula and
parked in the data store so the outputs could be read back rather than inferred:

```
A=yes B=yes C=yes D=no E=no F=no
```

| Case | Inputs | Result | Expected |
| --- | --- | --- | --- |
| A | no price row | `yes` | yes |
| B | Bespoke `Yes` | `yes` | yes |
| C | final price 0 | `yes` | yes |
| D | £799 standard, no adjustment | `no` | no |
| E | Bespoke `no` lowercase, £950 | `no` | no |
| F | £799 adjusted up to £1,049 | `no` | no |

Case E confirms the `lower()` guard; case F confirms an adjustment alone does not
trip review. Reason strings returned correctly for A, B and C.

A separate run (`c8a622d06c77415d9db17fe37d5ace74`, 2 ops, SUCCESS) posted
`quote_status: "Manual Review Required"` to the live FluentCRM REST endpoint for
`collsdigital@gmail.com` with `handleErrors: true`, so a non-2xx would have failed
the run. It did not — **FluentCRM accepted the write**.

**Not proven programmatically:** that FluentCRM *stored* the value. FluentCRM returns
200 and silently discards a value that is not in the field's configured option list,
and it will not serve custom field values back over REST (see FOLDER-LINK-FIX.md).
The only way to confirm is to open the contact and look. Collins to eyeball
`collsdigital@gmail.com` in FluentCRM and check the Manual Review Required radio is
selected. **That test record should then be set back to whatever it should be.**

## Bug found and fixed in the same deploy

Module 5, the CRM write on the auto-quote route, was **missing `__force_update`**.
Its own stored sample in the blueprint shows what that caused:

```
statusCode: 422
{"data":{"email":{"unique":"Provided email already assigned to another subscriber."}}}
```

Every contact reaching the Quote Builder already exists, because Phase 1 created them
at intake. So this call failed **every time** — and `handleErrors` was `false`, so Make
counted the 422 as a success and carried on to Stripe and the client email without
comment. Same class of bug as the 404-saved-as-a-file issue in MULTIFILE-FIX.md: a
green run that did not do its job.

This is the direct cause of the quote-stage fields Sandeep reported as blank.

Fixed:
- added `"__force_update": true`
- `handleErrors` false -> **true**
- added an error handler: alert email to support@ naming the reference, client, project
  type and final price, with what to set by hand, then `Resume` so the client is still
  quoted even if the CRM write fails
- added `"quote_status": "Quote Sent"` — it was only setting a *tag* named "Quote Sent",
  never the status field
- added `project_reference` and `project_type`

## Known gaps, not guessed at

**Custom field keys.** Only keys proven live are written: `quote_status`,
`project_reference`, `project_type`, `final_price`. The exact keys for Standard Price,
Adjustment Amount, Adjustment Reason, Quote Created and Quote Sent are not confirmed,
and FluentCRM silently drops values for keys that do not exist — so writing a guessed
key looks like success and leaves the field blank. These need reading off
FluentCRM -> Configure Custom Data before they are wired.

**Project type missing from the price list.** Condition 1 above catches a row that
exists with a blank price. It does **not** catch a project type with no row at all:
`google-sheets:filterRows` emits zero bundles when nothing matches, which halts that
branch before module 20 ever runs — so no quote, no flag, no alert, silently. Today
the dropdown options and the price list are kept in step by hand, so a mismatch
should not occur, but it is a real hole. Fixing it properly means restructuring the
lookup so a no-match still produces a bundle. Flagged for the Phase 2 build rather
than bolted on here.
