# Forminator payload and field mapping

The public Upload Plans page runs a **Forminator** form titled "Quote Request",
not the Fluent Forms form the automation was originally built against. It is
now connected to Make through Forminator's own webhook integration, so the live
page is untouched: layout, required fields, upload, consent wording and every
existing submission are exactly as they were.

## What Forminator actually sends

Captured from a real submission on 2026-09-26.

| Key | Example | Used for |
|---|---|---|
| `name_1_first_name` | `Levy` | greeting, CRM first name |
| `name_1_last_name` | `Afolly` | CRM last name, team email |
| `email_1` | `timmyafolly@gmail.com` | guard, recipient, CRM key |
| `select_1` | `Loft Conversion` | project type |
| `textarea_1` | `This is a test submission` | description in the team email |
| `address_1_street_address` | `161 Fedrack street LA` | **property address** |
| `upload_1` | `https://buildregs.co.uk/wp-content/uploads/forminator/...` | file download |
| `consent_1`, `consent_2` | `checked` | recorded in the team email |
| `entry_time` | `2026-09-26 05:08:54` | reference cross-check |
| `form_title` | `Quote Request` | identifies the source form |

`address_1` also arrives as a JSON string; the flattened
`address_1_street_address` is the one to use.

## The reference number

Forminator sends **no submission number**. There is no `serial_number` and no
entry id anywhere in the payload, unlike Fluent Forms.

The reference is therefore built from the timestamp:
`BR-{{formatDate(now; "YYYYMMDD-HHmmss"; "Europe/London")}}`, giving
`BR-20260926-054512`. Unique to the second, so two enquiries cannot collide,
and it still reads as a reference to a customer.

Before this was fixed, every folder came out named `BR-20260926-` with nothing
after the dash, because the mapping still referenced the Fluent Forms
`__submission.serial_number` that Forminator does not send.

## Files-received wording

Now driven by `4.fileSize > 0` rather than by whether the upload module
returned an id. A failed download previously still produced a zero-byte file in
Drive, which made the upload look successful and the email claim the plans had
arrived. Judging on the downloaded size is honest about what was actually
received.

No filter sits on the download module. A filter there would stop every module
after it, so a file-less enquiry would have produced a folder and then complete
silence for the customer. The Resume handlers cover a failed download instead,
and the customer always gets an acknowledgement, correctly worded either way.

## Property address

New to the automation: Fluent Forms never carried this field. It now appears in
the acknowledgement email, the team email, and on the contact record as
FluentCRM's native `address_line_1`, so no custom field was needed.

---

## Direct job-folder link in the paid-job email

Sandeep reported that the button in the paid-job notice opened the general
Projects directory rather than the individual job, and that he could not find
the quoted reference in the list.

Two separate causes. The folder is created at enquiry time by Phase 1, which
Phase 3 has never seen. And the two reference series do not match: intake
produces `BR-<date>-<time>` while the quote produces `BR-Q-<date>-<serial>`,
so nothing in the payment payload can identify the folder by name.

The reference he could not find, `BR-Q-20260925-9010`, had no folder at all.
It came from a simulated payment pushed directly at the payment webhook with
no enquiry before it, so nothing was ever created. Confirmed by searching
Drive directly: no folder of that name, and none created in Projects that day.

The fix links the two stages by the client's email address, which is the only
value both stages reliably share:

- Phase 1 writes the new folder's link to the contact's `drive_folder_url`
- Phase 3 looks the contact up by email and points the button at it

The lookup falls back to the Projects root if it returns nothing, so the worst
case is the previous behaviour rather than a broken link. The button label
changes with it, reading "Open this job's folder" when a specific folder was
found and "Open Projects folder" when it was not, so the team can tell at a
glance which they are getting. The URL is also printed beneath the button in
case the button is stripped by a mail client.

Phase 3 now costs 7 operations per payment rather than 5.
