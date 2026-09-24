# Milestone 2 verification log

Evidence for each fix, so the claims can be checked rather than taken on
trust. Every line below was observed, not inferred.

---

## Phase 1 — Intake (scenario 7129360)

Verified by a direct webhook test on 2026-09-23, execution
`9193bc1363f74923a7e3dd19b53d5048`, status 1, 9 operations.

| Claim | Evidence |
|---|---|
| Greeting renders a name | Email read `Hi Timmy,`. Previously `Hi ,` because the template asked for a `name` field the webhook never sends. |
| Reference uses the submission serial, not the client's email | Folder and email both read `BR-20260923-9001`. Previously `BR-<date>-<email address>`, which appeared in client folder names. |
| Uploaded file keeps its real name | Drive holds `dummy.pdf`, 13,264 bytes, `application/pdf`. Previously every upload landed as `file.txt` regardless of type. |
| Files-received wording is conditional | Email read `Your plans: Received`, which only renders when the upload returned an id. |
| Folder created in the client's Drive | Parent is `1XQGcexK1EA7COStPHEGSu7W6JmS_Gw8f` (*Projects*, inside *BuildRegs - Operations*, owned by support@buildregs.co.uk). Not the freelancer's personal-Drive lookalike. |
| FluentCRM contact is created with a name | Contact `timmyafolly@gmail.com` carries First Name `Timmy`, Last Name `Afolly`, Phone `07700 900123`. Phase 3 never writes names, so these can only have come from intake. Previously the request body was missing its closing brace and returned `400 rest_invalid_json` on every enquiry, silently, because the module was set not to treat rejections as errors. |

Not yet verified: the guard filters, the no-file path, and `enquiry_date`.

## Phase 3 — Payment & Assignment (scenario 7248863)

Verified by two webhook tests on 2026-09-23 and 2026-09-24, executions
`2dcc96a3d0cc4fd58efa9572c4cc3a26` and `15f7fbc493a54d868dcd5b6dcf8b6a3c`,
both status 1, 5 operations.

| Claim | Evidence |
|---|---|
| Greeting uses the name Stripe collected | Email read `Hi Timmy Afolly,`. Previously a bare `Hi,` while `customer_details.name` sat unused. |
| Amount comes from the payment, not the quote | Payload deliberately disagreed with itself: `amount_total` 84900 against metadata `final_price` "849". Email showed `£849.00`, so the figure derives from `amount_total / 100`. A metadata-derived value would have read `£849`. |
| Payment timestamp parses and converts | `created` 1790138259 is 04:37 UTC. Email showed `23 September 2026, 05:37`, correct for British Summer Time. This confirms `parseDate(...; "X")` handles a Unix timestamp. |
| Audit logging writes a full record | Ten of ten custom fields populated on the contact: `quote_status` Paid, `payment_date` 2026-09-23, `project_reference` BR-Q-20260923-9003, `project_type` Loft Conversion, `stripe_payment_id` pi_test_br9003, `stripe_session_id` cs_test_br9003, `amount_paid` 849.00, `payment_currency` GBP, `terms_version` 2026-09, `terms_accepted_at` 2026-09-23. |
| A CRM failure cannot swallow the confirmation | Module 3 carries a Resume handler. The handoff notes claimed one existed; the blueprint had none, so a CRM error would have aborted the run and left a paying customer with no receipt and the team unaware. |

Not yet verified: the `payerEmail` fallback when Stripe metadata is absent.

Date-typed fields store the date only, so `05:37` is not retained in the CRM.
Accepted deliberately: the exact timestamp lives in Stripe permanently and is
reachable through the stored `stripe_payment_id`.

## Corrections made along the way

Two mistakes of mine, both caught by testing rather than review:

The audit write initially used `project_ref` and sent a readable date string.
The schema already had `project_reference`, and its date fields cannot parse
`23 September 2026, 05:37`. Eight of ten fields were being discarded while the
run reported success. Keys and formats were realigned to the real schema.

Phase 1 initially wrote `quote_status: "Enquiry received"`. That is not one of
the field's options (`Draft`, `Quote Sent`, `Payment Pending`, `Paid`,
`Declined`), so it would have been dropped on every enquiry. It was removed for
a separate reason first: with `__force_update` set, a repeat enquiry from a
customer who had already paid would have reset their status from `Paid` back to
a lead. Quote status now belongs solely to the quoting and payment stages.

## Still open

- Fluent Forms is sending a payload without `email`, `__submission` or a usable
  `file-upload`, so the live form path cannot be tested. This blocks the client's
  own end-to-end test, which is itself a Milestone 2 deliverable.
- Phase 1 guard filters, no-file path and `enquiry_date` are untested.
- The Phase 3 metadata fallback is untested.
- Neither team email has been confirmed as received.
- Real team inbox and hosted logo URL remain deferred by agreement.
