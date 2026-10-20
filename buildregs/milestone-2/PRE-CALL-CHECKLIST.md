# Pre-call checklist — Milestone 2 verification, 20 Oct 2026, 2pm

Live state read from Make at the time of writing, not from memory.
Team 2535413, org 8783114.

---

## Part 0 — Live state as it stands right now

| Scenario | ID | Active | Valid | Queue | DLQ |
|---|---|---|---|---|---|
| Phase 1 — Intake (Forminator) | 7129360 | yes | yes | empty | 0 |
| Phase 2 — Quote Builder to Stripe | 7229882 | yes | yes | empty | 0 |
| Phase 3 — Payment & Assignment | 7248863 | yes | yes | empty | 0 |
| ZZ TEST (delete me) | 7636164 | no | — | — | — |

All three active together on Core. Stripe connection in use by Phase 2 is
**"BuildRegs Stripe (test)"**, id 10506139. A second Stripe connection
(10506123) exists but is attached to nothing.

All outbound email across all three scenarios now sends through **Sandeep's
Google connection** (support@buildregs.co.uk). That is why DKIM signs as
buildregs.co.uk and DMARC aligns.

---

## Part 1 — ONE BLOCKER: build this before 2pm

**The returning-customer route to Manual Review does not exist.**

Sandeep asked for it explicitly and asked to see it tested live. Phase 1's
flow today is:

```
1 webhook -> 2 projectRef -> 3 create folder -> 70 datastore write
  -> 21 normalise uploads -> 20 build fields -> 6 FluentCRM
  -> 7 ROUTER (files / client email / team email)
```

There is no returning-customer detection anywhere in it.

What is **already** fine, and what to tell him plainly:

- Phase 1 never writes the quotation or payment fields, so it cannot and does
  not clear them. `standard_price`, `final_price`, `stripe_payment_id`,
  `amount_paid` and the rest are untouched by a new enquiry. That half of his
  instruction is already satisfied.

What is **not** fine:

- Phase 1 does overwrite `project_reference`, `project_type`, `enquiry_date`,
  `drive_folder_url` and `quote_status` on an existing contact. A returning
  customer loses the first project's reference and folder link from their
  contact record.
- Module 70 writes the datastore record keyed on email with
  `"overwrite": true`. A second enquiry replaces the first project's folder
  pointer, so a Phase 3 payment for the **old** project would resolve to the
  **new** project's folder.
- Nothing flags the enquiry for human attention.

Smallest change that satisfies what he asked for:

1. Insert `datastore:GetRecord` on store 199758, key `{{1.email_1}}`, before
   module 3. Set it not to fail when the record is absent.
2. Add to module 20:
   `isReturning = {{if(length(trim(ifempty(<get>.projectRef; ""))) > 0; "yes"; "no")}}`
3. `quoteStatus` becomes `Manual Review Required` when `isReturning = yes`.
4. Gate module 70 on `isReturning = no`, so the first project's folder pointer
   survives.
5. Leave `project_reference` and `drive_folder_url` out of the module 6 body
   when returning, so the original project's details are not overwritten.
6. Add a team email on the returning branch naming both references.
7. Customer still gets the normal acknowledgement. Phase 1 sends no quote and
   no payment link, so there is no risk of an unintended quotation or payment
   request from this path.

Test it with a second submission from an address already in the store, for
example `adamquarmby@hotmail.com` or `gdhami1985@gmail.com`.

---

## Part 2 — Two real enquiries arrived on 19 October

These are not in any of the other documents. Both ran unattended and green.

| Ref | Client | Email | When | Ops |
|---|---|---|---|---|
| BR-20261019-093711 | James Pryer-Freeman | jamespf1@gmail.com | 19 Oct 09:37 | 12 |
| BR-20261019-151057 | Aleksander Raszpla | araszpla@hotmail.co.uk | 19 Oct 15:10 | 16 |

Check before the call:

- [ ] Both Drive folders exist with the drawings inside, correctly named
- [ ] Both contacts in FluentCRM carry first name, last name, phone,
      project_ref, project_type, enquiry_date, folder link
- [ ] The 16-operation run is the multi-file path firing for a real customer
      (3.99 MB transfer suggests more than one file, or one large one). If it
      is multi-file, that is live proof of the multi-file fix and worth showing
- [ ] Neither is a test submission from Sandeep

These are genuine customers waiting on quotes. Flag that to him. They are also
the strongest evidence on the call: the system ran twice, unattended, with no
intervention from either of us.

---

## Part 3 — Check these yourself before he joins

Do not discover any of this live.

**Intake**
- [ ] Submit a fresh enquiry through the live Upload Plans form with two files
      attached and a distinctive name, so you have a clean run to walk through
- [ ] Confirm folder name is `BR-<date>-<number>`, not an email address
- [ ] Confirm both files land with their real names, not `file.txt`
- [ ] Confirm the acknowledgement greets by first name, shows the reference,
      and reads "Your plans: Received"
- [ ] Submit once with no file. Run should still go green and the email should
      read "Not received, please reply to this email with your files".
      This path has never been tested

**Quotation and the threshold**
- [ ] Run a quote at £2,499, at £2,500 exactly, and at £2,501
- [ ] Confirm £2,500 goes out automatically and £2,501 holds
- [ ] Confirm the review branch creates no Stripe session and sends the client
      nothing
- [ ] Open the held contact and confirm the `quote_status` radio really shows
      Manual Review Required. FluentCRM returns 200 and silently discards a
      value outside the option list, so only looking at it proves anything
- [ ] Confirm `quote_sent` is blank on a held quote and dated on an auto quote

**Payment**
- [ ] Take one quote all the way through Stripe checkout with
      `4242 4242 4242 4242`. This has never been done with a real checkout,
      only with simulated webhook payloads back on 23 and 24 September
- [ ] Confirm the receipt amount matches what Stripe charged
- [ ] Confirm the date renders as a real date and time, not blank
- [ ] Open the contact and check all ten audit fields field by field
- [ ] Confirm the NEW PAID JOB notice arrives with a working folder link
- [ ] Confirm the Stripe dashboard is showing TEST mode, and have that tab open

**Housekeeping**
- [ ] Have the Make execution history, Drive Projects folder, FluentCRM
      contact list and Stripe test dashboard open in tabs before he joins
- [ ] Leave the test folders, records and ZZ TEST scenario in place. He asked
      for that explicitly
- [ ] Exception: the file inside `BR-20261016-072647` was attached in error
      and belongs to an unrelated project. Delete that file, not the folder

---

## Part 4 — Answers to have ready

**The £2,500 boundary.** Settled and evidenced. The rule is strictly
*above* £2,500. A quotation of exactly £2,500 goes out automatically;
£2,500.01 is held. The formula is `parseNumber(11.finalPrice) > 2500` in
module 20 of scenario 7229882, one place to change it. Eleven synthetic cases
were run through the deployed formula; cases H, J and K pin the boundary at
£2,500, £2,501 and £2,499. The cap applies to the final price after any
adjustment, so £2,000 adjusted up by £600 is held.

**Why an adjustment alone does not trigger review.** The Quote Builder is a
staff tool, so an adjustment entered there is already the human judgement.
He confirmed this on 6 October.

**Review is triggered by four conditions, OR'd:** no price row for the project
type, the price list marks it Bespoke, final price above £2,500, or final price
zero or negative.

---

## Part 5 — Say these are still open, do not let him find them

- The returning-customer route, unless built before the call
- Phase 3's `payerEmail` fallback when Stripe metadata is absent, untested
- A project type with no row at all in the price list halts the branch
  silently: no quote, no flag, no alert. Condition 1 catches a blank price but
  not a missing row. Dropdown and price list are kept in step by hand today
- Phone blanking: a returning enquiry submitted with no phone would clear the
  stored number, because `__force_update` is on. Only affects replays of
  pre-11-October payloads
- Date fields in FluentCRM are date-only, so two quotes on the same day are
  indistinguishable by `quote_created`
- The real team inbox is still the `support@buildregs.co.uk` placeholder, and
  templates render a text wordmark rather than a hosted logo. Both deferred by
  agreement
- Empty orphan folder `BR-20261015-220007` needs deleting by him; it is owned
  by support@buildregs.co.uk so you cannot
- FluentCRM reports its server-side cron is not enabled. Harmless here because
  Make does the work, but it would affect FluentCRM's own sequences
- Waheed Ahmed's acknowledgement suppression was never implemented. His
  address is not in the module 20 suppression list
