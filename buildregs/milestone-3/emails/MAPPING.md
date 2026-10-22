# Placeholder mapping

Every placeholder used in the templates, and where its value comes from once
the emails are wired into Make. This is the wiring list, so nothing is left to
be guessed at build time.

Source key: **Enquiry** = the Forminator intake payload. **Projects** = the row
in the BuildRegs Projects sheet, keyed on quotation reference. **Review** = the
values Sandeep enters or confirms on the review page. **Stripe** = the payment
event. **Drive** = the project folder.

| Placeholder | Source | Notes |
|---|---|---|
| `{{greeting}}` | Enquiry | `Hi <first name>,` when a first name exists, otherwise `Hello,`. Never assembled from `Hi ` plus an empty value |
| `{{first_name}}` | Enquiry | Retained for subjects only; body copy uses `{{greeting}}` |
| `{{property_address}}` | Enquiry | Falls back to `(address not supplied)` if the field is empty |
| `{{project_reference}}` | Enquiry | `BR-<date>-<serial>`, generated at intake |
| `{{file_receipt_sentence}}` | Enquiry + Drive | Written **only once the upload has actually saved**, per his setup note. Two values: files saved, or the invitation to reply with them |
| `{{quote_reference}}` | Projects | `BR-Q-<date>-<serial>`, one per project, not per customer |
| `{{approved_scope}}` | Review | Prefilled from the price list Customer Scope column, editable before approval |
| `{{itemised_fees}}` | Review | One row per selected project type at its standard price |
| `{{combined_project_discount}}` | Projects | Empty string when not applicable, so the line disappears. 50% of the lowest-priced selected type, once only, never on a single type |
| `{{price_adjustment}}` | Review | Empty string when not applicable. Carries his wording for the adjustment, not just a figure |
| `{{total}}` | Projects | Formatted with thousands separators and two decimals. The single source for the Stripe amount, so the email and the charge cannot disagree |
| `{{approved_exclusions_or_conditions}}` | Review | Empty string when not applicable |
| `{{turnaround}}` | Review | Working days, prefilled per package, editable |
| `{{stripe_payment_link}}` | Stripe | The session URL. Rendered only as the button label, never as visible text |
| `{{amount_paid}}` | Stripe | From the payment itself, not from the quote, so the receipt always matches what was charged |
| `{{approved_package_summary}}` | Projects | Package plus the selected project types |
| `{{approved_package_name}}` | Projects | Short form, used on the Stripe checkout page |
| `{{deliverable_description}}` | Projects | What was actually produced, so a calculations-only job does not claim drawings |
| `{{approved_documents_link}}` | Drive | The approved-output subfolder only. Never the folder holding working files |
| `{{project_specific_next_steps}}` | Review | Set at approval, so it matches the agreed scope |
| `{{review_link}}` | Sandeep | Pending from him |

## Conditional lines

Four placeholders are whole table rows that must vanish rather than render
empty: `{{combined_project_discount}}`, `{{price_adjustment}}`,
`{{approved_exclusions_or_conditions}}` and `{{file_receipt_sentence}}`.

Each is built in Make as a variable holding either the complete row of HTML or
an empty string. That is the same pattern already used for the files and
address blocks in the live acknowledgement, so it is proven rather than new.

## Two rules worth keeping

**The total is computed once.** It is written to the project row, and both the
email and the Stripe amount read it from there. Nothing is typed twice, so the
quote, the charge and the record cannot drift apart.

**The documents link points at approved output only.** Working files live in a
separate subfolder that is never shared. This is a folder convention, not a
permission setting, so it cannot be undone by a sharing mistake.
