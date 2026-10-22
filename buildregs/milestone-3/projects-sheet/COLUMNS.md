# BuildRegs Projects sheet, column dictionary

One row per project. Written by Make, readable by Sandeep.

| # | Column | Meaning |
|---|---|---|
| A | `quote_reference` | Key. One row per project. BR-Q-<date>-<serial> |
| B | `project_reference` | The original enquiry reference from intake |
| C | `status` | See the status list on the Notes tab |
| D | `created_at` | When the project row was first written |
| E | `updated_at` | Last change of any kind |
| F | `customer_name` | Full name as submitted |
| G | `customer_email` | Also the FluentCRM contact key |
| H | `customer_phone` |  |
| I | `property_address` | The property the work is at |
| J | `package` | Full or Structural-only |
| K | `project_types` | One or more, comma separated |
| L | `standard_prices` | Matching project_types, same order |
| M | `subtotal` | Sum of standard_prices before discount or adjustment |
| N | `discount_type` | Combined project, Trade, or None |
| O | `discount_amount` | Positive number. 50% of the lowest-priced type |
| P | `discount_overridden` | yes when Sandeep changed or removed it |
| Q | `adjustment_amount` | Positive to add, negative to reduce |
| R | `adjustment_reason` | Shown to the customer, so write it plainly |
| S | `total` | What the customer pays. The single source for Stripe |
| T | `turnaround_days` | Working days from payment and full information |
| U | `approved_scope` | What is included, as approved |
| V | `approved_exclusions` | What is not included |
| W | `next_steps` | Customer next steps, sent with the documents |
| X | `india_notes` | PRIVATE. Never sent to the customer |
| Y | `project_folder_url` | The job folder |
| Z | `plans_folder_url` | Customer plans and supporting documents |
| AA | `approved_output_url` | Approved final documents only. Never working files |
| AB | `stripe_session_id` | Used to expire the old link when a quote is replaced |
| AC | `stripe_payment_id` |  |
| AD | `amount_paid` | From the payment itself, not the quote |
| AE | `payment_currency` |  |
| AF | `paid_at` |  |
| AG | `approval_token` | Random. Authorises the one-tap approval links |
| AH | `approved_at` | When Sandeep approved the quotation |
| AI | `quote_sent_at` | When the customer was sent the quotation |
| AJ | `handover_sent_at` | When the India team was notified. After payment only |
| AK | `ready_for_review_at` | When the team marked the package ready |
| AL | `delivered_at` | Starts the follow-up clock |
| AM | `checkin_sent_at` | Three day check-in. Blank means still due |
| AN | `review_request_sent_at` | Seven day review invitation. Blank means still due |
| AO | `awaiting_information` | yes when the job is paid but not production ready |
| AP | `notes` |  |
