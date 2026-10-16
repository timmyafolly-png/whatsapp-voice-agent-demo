# Phase 1 Intake — changes of 15 October 2026

Done after Sandeep confirmed the Make upgrade to Core (10,000 ops, reset 15 Oct,
next reset 15 Nov). Scenario 7129360, team 2535413, org 8783114.

## Status

| Scenario | ID | Active | Valid |
|---|---|---|---|
| Phase 1 — Intake (Forminator) | 7129360 | yes | yes |
| Phase 2 — Quote Builder to Stripe | 7229882 | yes | yes |
| Phase 3 — Payment & Assignment | 7248863 | yes | yes |
| ZZ TEST - drive scope check (delete me) | 7636164 | no | — |

All three run active at once on Core. Confirmed empirically, not inferred.

## The discovery that mattered

The Forminator payload changed shape around 11 October, and the queue held
**both** shapes at once. It is not only `upload_1` that changed:

| Field | Before ~11 Oct | After |
|---|---|---|
| `upload_1` | `"https://.../a.pdf"` (string) | `{file:{file_url:[...]}}` (array, multi-file) |
| `upload_1` when empty | `""` | `[]` |
| `name_1` | `"Jack Broadway"` (string) | `{first_name, last_name}` |
| `address_1` | `"{\"street_address\":\"...\"}"` (JSON string) | `{street_address}` |
| `phone_1` | absent | present |

The scenario reads the **flat** fields (`name_1_first_name`,
`name_1_last_name`, `address_1_street_address`), which exist in both shapes, so
names and addresses were never affected. Only uploads were, and only uploads
needed changing.

## Changes made

1. **New module 21, "Normalise uploads (any Forminator shape)"** (`util:SetVariables`),
   placed before module 20. Two independent variables:
   - `fileUrls` = `{{ifempty(1.upload_1.file.file_url; split(ifempty(1.upload_1; ""); ","))}}`
   - `uploadCount` = nested `if` that returns the array length for the new shape,
     the comma-split count for the old string shape, and 0 for both empty cases.
   Verified against all six shapes: old single (1), old comma-pair (2),
   new 1 file (1), new 3 files (3), `""` (0), `[]` (0).
2. **Module 40 feeder** iterates `{{21.fileUrls}}`, gated on `{{21.uploadCount}} > 0`.
   Multiple files are supported because `file_url` is an array and the feeder
   iterates it.
3. **Module 4** gained a guard so an empty URL is never fetched.
4. **Module 6 (FluentCRM)** now sends `"phone": "{{1.phone_1}}"`.
5. **Module 6** writes `quote_status` from a new variable instead of the literal
   `"Draft"`.
6. **Modules 20** gained `isHandled` and `quoteStatus`, both driven by
   `contains("jack@studiopcm.co.uk"; lower(trim(1.email_1)))`.
7. **Modules 8 and 9** (customer acknowledgement, team notification) now carry
   the filter `{{20.isHandled}} = no`.

### Suppression list — how to extend it

Two places in module 20, `isHandled` and `quoteStatus`. Add an address to the
quoted string in both, comma-separated:

    contains("jack@studiopcm.co.uk,someone@else.com"; lower(trim(1.email_1)))

It is a substring match, so use full addresses. Waheed Ahmed's address is not in
the list — his acknowledgement suppression is **not** currently implemented; add
it here if still required.

## Queue processing

Five items were queued while the scenario was inactive. Every payload was
archived to `queue-archive/` before anything was deleted, with a curl command to
replay any of them.

- Four test entries deleted: Naikoo Suhaib and Clues Arena (both
  cluesarena@gmail.com, Sandeep's test address) and two Shivani Mann entries.
- **Jack Broadway processed at 21:13 UTC**, execution
  `b05b6f49c3684cda965cbf8ad13c7d59`, status SUCCESS, 10 operations.
  Ten operations is the whole flow with **both email modules skipped**, which is
  the suppression working.
  - Folder: `BR-20261015-221315` (`1C5GOLE_gecqRGYJ47sxdmcRQvSmRoz0F`)
  - Drawing: `gtmsTi1JII4F-26-RES-012-53-Wells-Road-LT-Planning-Issue-June26.pdf`,
    16,826,583 bytes, owned by support@buildregs.co.uk
  - `quote_status` written as "Quote Sent"
  - No acknowledgement, no quotation, no payment email sent to him
- Queue is now empty.

## Two failures on the way, and what they teach

1. **`remove()` rejects a non-array.** The first version of module 21 used
   `remove(ifempty(...); "")` to strip empty strings. On Jack's old-shape payload
   it failed with *"Function 'remove' finished with error! Invalid array."*
   The fix computes the count separately instead of cleaning the array.
   Note the failure was at module 21, *before* any email module, so nothing
   reached the customer and the queue item stayed replayable.
2. **Duplicate variable names.** `fileCount` was briefly declared in both module
   21 and module 20. Renamed to `uploadCount` in 21.
3. **`isinvalid: true` is not always a blueprint problem.** It was set by the
   failed execution and persisted across two blueprint updates, then cleared
   itself after the first successful run. Do not chase it as a schema error;
   check whether a run failed recently.

## Open items

- **Mail authentication VERIFIED 16 Oct.** Test enquiry BR-20261016-072647 sent to
  collsdigital@gmail.com. Gmail "Show original" reported:

  | Field | Value |
  |---|---|
  | Visible From | `support@buildregs.co.uk` |
  | Reply-To | not set; replies go to the From address (module 8 has `replyTo: ""`) |
  | Return-Path | not captured in the summary box; moot, see below |
  | SPF | PASS, IP 209.85.220.41 (Google range) |
  | DKIM | PASS, domain `buildregs.co.uk` |
  | DMARC | **PASS** |
  | Message-ID | `<259614d5-e039-7142-bc66-b691c3b37e64@buildregs.co.uk>` |
  | X-Mailer | nodemailer 2.7.2 (Make's email module) |

  **Alignment holds.** DKIM signed as `buildregs.co.uk`, the same domain as the
  visible From, so DKIM is aligned and DMARC passes on that basis. Return-Path is
  therefore not load-bearing here. The failure mode to watch for in future, if the
  sending connection is ever changed, is DKIM signing as `gmail.com` instead: SPF
  and DKIM would both still show PASS while DMARC failed on alignment.

- **Sequencing conflict to flag to Sandeep.** He asked for the header check
  *before* the Make acknowledgement goes live, and in the same message asked for
  Phase 1 to be reactivated. Reactivating makes the acknowledgement live. Phase 1
  was left active, because the alternative is losing genuine enquiries again, as
  happened to Jack. If he wants it held, add every address to the suppression
  list or deactivate 7129360.
- **Empty orphan folder** `BR-20261015-220007`
  (`1R9bsl51RvGXjZ2GFAd1KHEAfxPEziyjR`) left by the failed run. Trashing it was
  refused because it is owned by support@buildregs.co.uk. Sandeep deletes it.
- **Scenario 7636164** "ZZ TEST (delete me)" still present.
- **Test artefacts from the 16 Oct deliverability run** to remove: CRM contact
  "Deliverability Test", Drive folder `BR-20261016-072647`
  (`1JEue_AwRSUXBYz7iXj7lnMvzWFSv5Q9U`). The file inside it was attached in error
  and belongs to an unrelated project; delete it rather than leaving it in a
  client folder.
- **Phone field still unconfirmed.** The CRM write sends `"phone"`, and the run
  succeeded, but FluentCRM is unreachable from the automation environment so the
  stored value has not been read back. Open the "Deliverability Test" contact and
  check the Phone field shows 07700 900123. If blank, the key name is wrong for
  this FluentCRM version.
- **Phone blanking edge case.** `"phone": "{{1.phone_1}}"` sends an empty string
  when the field is absent, and `__force_update` is on, so a repeat enquiry from
  an existing contact submitted without a phone would clear the stored number.
  Every current form submission carries `phone_1`, so this only affects replays
  of pre-11-October payloads. Left simple deliberately; Make's expression syntax
  makes a conditional JSON key awkward.
- Forminator "Upload Plans" acknowledgement stays uncreated, as instructed.
- Quotation approval and payment rules unchanged. No SMS added. Stripe still in
  test mode.
