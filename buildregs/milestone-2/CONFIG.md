# Constants and decisions

Decisions taken 2026-09-23. Anything marked DEFERRED is a conscious
"good enough for now", not an oversight — revisit before go-live.

| # | Constant | Used in | Value | Status |
|---|---|---|---|---|
| 1 | `TEAM_INBOX` | Phase 3 branch 4b | `support@buildregs.co.uk` | **DEFERRED.** Client has not confirmed the real "new paid job" inbox. Shipping on the placeholder. One-field change when Sandeep decides. |
| 2 | `TERMS_VERSION` | Phase 3 module 3 audit body | `2026-09` | **DECIDED.** Date stamp of the terms in force when the payment was taken. Bump this string whenever the T&Cs are revised, so every historic payment still points at the wording that was actually agreed. |
| 3 | `LOGO_URL` | all three email templates | *(none yet)* | **OPEN.** No hosted URL available. Templates ship with a styled text wordmark instead of a broken image. Source asset confirmed good: 1024x227 PNG, RGBA, transparent. Get the URL from WordPress admin, Media, the logo file, File URL field. |
| 4 | WordPress app password | Phase 1 module 6, Phase 3 module 3 | unchanged | **DEFERRED.** Stays inline in both blueprints for now. Still recommended: move it to a Make connection and rotate it, since it has already left Make in exported artifacts. Redacted from the git backups regardless. |
| 5 | `PROJECTS_FOLDER_ID` | Drive folder creation, team email | `1XQGcexK1EA7COStPHEGSu7W6JmS_Gw8f` | **CONFIRMED.** Verified as *Projects* inside *BuildRegs - Operations*, owned by support@buildregs.co.uk. Not the personal-Drive lookalike. |
| 6 | `TERMS_URL` | payment confirmation footer | `https://buildregs.co.uk/terms-and-conditions/` | **CONFIRMED.** |

## Swapping the text wordmark for the real logo

Once the hosted URL exists, in each template replace the block marked
`<!-- LOGO: text wordmark, swap for hosted image when URL available -->`
with:

```html
<img src="THE_URL" alt="BuildRegs" width="170"
     style="display:block; width:170px; max-width:170px; height:auto; border:0;">
```

Then re-paste the affected email bodies into Make.

Two cautions. Check the URL loads in a private browser window: an image that
works while you are logged in as admin can still 403 for everyone else, and
email clients are logged out. And note that WordPress upload URLs carry the
year and month, so re-uploading the logo later produces a new URL and
silently 404s the old one in every email already sent.

The source logo has a transparent background with a black wordmark, so it
will disappear against a dark backdrop. The templates place it on an
explicitly white card, which holds up in most clients, but a version with a
solid white background is safer if Gmail dark mode ever becomes a concern.

---

## Guard filter added 2026-09-23

Phase 1 module 2 now carries a filter, "Guard: required fields present":
email exists, email contains "@", and `__submission.serial_number` exists.

A payload failing any of those stops at the webhook. No folder is created,
no file uploaded, no CRM write, no failed email, and crucially no error
counted against the scenario's maxErrors, which is what was tripping Make's
automatic deactivation.

Module 5 also gained a filter requiring `4.fileSize > 0`, so a failed or
absent download can no longer produce a 0-byte "Untitled" file in the
client's Drive.

Blocked runs are not silent: Make's execution history records them and shows
the filter that stopped them. A no-file enquiry is still a valid enquiry and
passes the guard, landing on the "Not received" wording as designed.

Make cannot roll back a created Drive folder, a sent email or a posted CRM
record. `builtin:Rollback` only covers transactional modules, which these are
not. Preventing the run is the fix; undoing it is not available.

---

## Guard filter corrected 2026-09-24

The first version of the guard used Make's `exist` operator on `1.email` and
`1.__submission.serial_number`. A live submission carrying a valid email and
serial number 49 was still blocked, stopping the run after one operation, so
those conditions do not evaluate the way the blueprint API accepts them.

The guard now uses a single condition: `1.email` contains `@`. An empty or
malformed email fails it, which is the case that was creating junk folders;
a real address passes. `text:contains` is the operator family already proven
to work elsewhere in these scenarios.

Rather than blocking on a missing serial number, the reference now degrades
gracefully: `ifempty(__submission.serial_number; __submission.id)`. A missing
serial can no longer produce a truncated `BR-<date>-` folder name, and it no
longer stops a legitimate enquiry.

Module 5's `4.fileSize > 0` filter, which used the `number:greater` operator
and was never exercised, has been replaced by a filter on module 4: proceed
only when `1.file-upload[]` contains `http`. This guards on whether the
customer supplied a file at all, which is the meaningful question, and keeps
every filter in the scenario on the one operator family known to work.

---

## Client decisions received 2026-09-25

Sandeep supplied the hosted logo and the real team inbox, closing two
deferred items.

**Logo.** `https://buildregs.co.uk/wp-content/uploads/2025/11/BuildRegs-Black-1024x227.png`
The dark wordmark, 1024x227, matching the source asset's own dimensions, so
it is full size rather than a downscale. Now live in both customer-facing
emails in place of the text wordmark. The internal team notice keeps its
navy header bar and no image: a dark logo would be invisible there.

**Team inbox.** Changed from the `projects@` placeholder to
`support@buildregs.co.uk` in both scenarios, Phase 1 module 7b and Phase 3
module 4b. Note this is also the sending account, so the notices now arrive
in the same mailbox they are sent from. That is what was asked for and it
works, but it is worth watching that they are not filtered as self-sent.
