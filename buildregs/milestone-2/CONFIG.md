# Constants and decisions

Decisions taken 2026-09-23. Anything marked DEFERRED is a conscious
"good enough for now", not an oversight — revisit before go-live.

| # | Constant | Used in | Value | Status |
|---|---|---|---|---|
| 1 | `TEAM_INBOX` | Phase 3 branch 4b | `projects@buildregs.co.uk` | **DEFERRED.** Client has not confirmed the real "new paid job" inbox. Shipping on the placeholder. One-field change when Sandeep decides. |
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
