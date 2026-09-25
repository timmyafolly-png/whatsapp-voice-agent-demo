# Milestone 2 acceptance test

Two runs, about ten minutes, roughly 16 operations. Run these yourself
before Sandeep sees anything, then run them again with him.

Stripe stays in TEST MODE throughout.

---

## Pre-flight

1. Make, eu1, team **BuildRegs Automation**. Note which scenarios are on.
   At the time of writing: Phase 2 ON, Phase 1 OFF, Phase 3 OFF.
2. The free plan allows **two active at once**. Turning on a third silently
   switches another off, and submissions to the switched-off one queue but
   never run. So do Test A and Test B in sequence, not together.
3. Check the ops counter. About 419 of the monthly 1,000 remained on
   2026-09-23. Each run below costs roughly 8.

---

## Test A: intake

**Set up.** Switch **Phase 1 ON**. Leave Phase 2 as it is. Phase 3 stays OFF.

**Do.** Go to the live Upload Plans form on buildregs.co.uk and submit a real
entry. Use an address you control. Attach one file with a distinctive name
and extension, for example `loft-plans-TEST.pdf`. Pick any project type.

Submit through the actual form, not Make's "Run once". Run once fires
regardless of active state and has hidden problems before.

**Then check all six:**

| # | Where | Expect |
|---|---|---|
| A1 | Make execution history | One run, green, about 8 operations |
| A2 | Drive, Projects folder | New folder named `BR-<date>-<number>`, e.g. `BR-20260923-42`. **Not** an email address |
| A3 | Inside that folder | Your file, named `loft-plans-TEST.pdf` or close to it. **Not** `file.txt` |
| A4 | FluentCRM, Contacts | The contact exists **with first and last name filled in**. This is the one that has never worked. Open it and confirm the custom fields `project_ref`, `project_type` and `quote_status` carry values |
| A5 | Your inbox | Branded acknowledgement. Greeting shows your actual first name, not `Hi ,`. Reference matches A2. Project type shown. A row reading "Your plans: Received" |
| A6 | support@buildregs.co.uk | Team notice. No stray ` / / ` where the old UTM fields were. Space between first and last name in the subject. Folder link opens the right folder |

**Then the negative case.** Submit again with **no file attached**. Expect:
the run still completes green, and the acknowledgement now reads
"Your plans: Not received — please reply to this email with your files".
Previously this would have failed the whole run.

---

## Test B: payment

**Set up.** Switch **Phase 1 OFF**, switch **Phase 3 ON**. Keep Phase 2 as it is.

**Do.** Take a quote through the Quote Builder as normal and pay the Stripe
test link with card `4242 4242 4242 4242`, any future expiry, any CVC.

**Then check all five:**

| # | Where | Expect |
|---|---|---|
| B1 | Make execution history | One run, green |
| B2 | Customer inbox | Branded receipt. Greeting uses the name entered at Stripe checkout, not `Hi,`. **Amount matches what Stripe actually charged** |
| B3 | Same email | "Date" shows a real date and time such as `23 September 2026, 14:07`. If it is blank or nonsense, see Risk 2 below |
| B4 | FluentCRM contact | `quote_status` = Paid, plus `project_ref`, `stripe_payment_id`, `stripe_session_id`, `amount_paid`, `payment_currency`, `terms_version` = 2026-09, `terms_accepted_at`. **If any are missing, see Risk 1** |
| B5 | support@buildregs.co.uk | High-priority "NEW PAID JOB" notice with amount, payment intent, checkout session and a working Projects folder link |

---

## The two things most likely to fail

These are unverified by design; I could not run either scenario.

**Risk 1: FluentCRM ignores the new custom fields.** Ten audit fields are
written under `custom_values`. If a custom field does not already exist in
FluentCRM, it is dropped silently and the run still looks green. Check B4
field by field. If some are missing, create the matching custom fields in
FluentCRM under Settings, Custom Fields, using exactly those key names, then
re-run Test B.

**Risk 2: the payment date renders empty or wrong.** It is produced by
`parseDate(1.data.object.created; "X")`, reading Stripe's Unix timestamp. If
Make does not accept the `X` format token, B3 will be blank or absurd. The
fallback is to use `{{now}}` formatted as `DD MMMM YYYY, HH:mm` in
Europe/London, which is slightly less accurate but always renders.

---

## Restore afterwards

Put the on/off state back to whatever you noted in pre-flight, so nothing is
left silently switched off.

---

## What to send back

For each of the eleven checks, pass or fail. For any failure, the Make
execution detail for the failing module: its input, its output and the error
text. That is enough to diagnose and fix without guessing.

---

## Still outstanding regardless of the result

- The real "new paid job" team inbox. Still the placeholder
  `support@buildregs.co.uk` pending Sandeep's decision.
- The hosted logo URL. Templates currently render a text wordmark.
- Multi-file uploads. Only the first file is kept; fixing it needs an
  Iterator and a router restructure. Proposed for Milestone 3.
