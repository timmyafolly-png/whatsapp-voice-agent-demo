# Constants to fill before this goes live

Five values are referenced by name across the templates and the apply guide.
Four are quick; one is a real decision for Sandeep.

| Constant | Used in | Current value | Status |
|---|---|---|---|
| `LOGO_URL` | all three email templates | *(placeholder)* | **Needed.** Hosted URL of the buildregs house mark + wordmark, e.g. `https://buildregs.co.uk/wp-content/uploads/.../buildregs-logo.png`. Never base64 — Gmail strips it. I could not read it myself: this environment's network policy blocks `buildregs.co.uk`. |
| `TEAM_INBOX` | Phase 3 branch 4b | `projects@buildregs.co.uk` | **Client decision.** The handoff records the real "new paid job" inbox as TBC. Ship M2 on `projects@` and swap when Sandeep confirms — it's a one-field change. |
| `TERMS_VERSION` | Phase 3 module 3 audit body | *(suggest `2026-09`)* | **Client decision.** Needs to be a value Sandeep can point at later and say "that's the wording they agreed to". A date stamp of the last T&C revision is the usual choice. |
| `PROJECTS_FOLDER_ID` | team notification button | `1XQGcexK1EA7COStPHEGSu7W6JmS_Gw8f` | Confirmed — the Shared Drive folder owned by support@buildregs.co.uk. Already hardcoded correctly. Do **not** substitute the personal-Drive lookalike `1hAPsa_fAv1GDP49YtHSCAw9baqZmKjc6`. |
| `TERMS_URL` | payment confirmation footer | `https://buildregs.co.uk/terms-and-conditions/` | Confirmed, already in place. |

## Swapping the logo

Once you have the hosted URL, from the repo root:

```bash
cd buildregs/milestone-2/emails
sed -i 's|LOGO_URL|https://buildregs.co.uk/wp-content/uploads/YYYY/MM/buildregs-logo.png|g' *.html
```

Then re-paste the three bodies into Make. Check the rendered width — the templates
size the logo to 170px wide, so supply an image at least 340px wide for retina screens.
