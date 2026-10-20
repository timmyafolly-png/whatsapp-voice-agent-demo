# Call runbook — what to click, in order

Read top to bottom. Each test says what you do, and what Sandeep should see.
If what he sees matches, that test passed. Nothing else to think about.

---

## Before he joins: open these five tabs

1. **Make** — make.com, team BuildRegs Automation, the Scenarios list
2. **Google Drive** — the "Projects" folder inside "BuildRegs - Operations"
3. **FluentCRM** — buildregs.co.uk/wp-admin, then FluentCRM, then Contacts
4. **Stripe** — dashboard.stripe.com, with the **Test mode** toggle ON
5. **The form** — the Upload Plans page on buildregs.co.uk

Also open your own email inbox. You will be receiving the test emails.

Leave all three scenarios switched ON. They are already on.

---

## TEST 1 — A normal enquiry with drawings

**You do:** Fill in the Upload Plans form. Use your own email. Attach two
files with obvious names like `plan-one.pdf` and `plan-two.pdf`. Submit.

**Then show him, in this order:**

| Tab | Point at | He should see |
|---|---|---|
| Make | Phase 1, History | A new row, green, just now |
| Drive | Projects folder | A new folder named like `BR-20261020-143015` |
| Drive | Inside that folder | **Both** your files, with their real names |
| FluentCRM | Contacts, your contact | Your first and last name, your phone number |
| FluentCRM | Same contact, scroll down | Project reference, project type, enquiry date, folder link |
| Your inbox | The acknowledgement | Greets you by first name. Shows the reference. Says "Your plans: Received" |

**What this proves:** the whole intake path, and that multiple files work.

---

## TEST 2 — An enquiry with no drawings

**You do:** Fill in the same form again. Same email. **Attach nothing.**
Submit.

**Then show him:**

- Make, Phase 1, History: the run is still **green**, not red
- Your inbox: the new email now says "Your plans: Not received, please reply
  to this email with your files"

**What this proves:** someone who forgets to attach their plans still gets
looked after, and the run does not break.

---

## TEST 3 — A quote below the threshold

**You do:** Open the Quote Builder. Build a quote that comes to **£2,499**.
Send it.

**Then show him:**

- Your inbox: the quotation email arrives, with a payment link
- FluentCRM, the contact: Quote Status says **Quote Sent**
- FluentCRM, same contact: Standard Price, Adjustment, Final Price, Quote
  Created and Quote Sent all have values in them

**What this proves:** a normal quote goes out on its own, and the numbers
land in the CRM.

---

## TEST 4 — A quote at exactly £2,500

**You do:** Build a quote that comes to **exactly £2,500**. Send it.

**He should see:** it goes out automatically, same as Test 3.

**Say this out loud:** "The rule is above £2,500. So exactly £2,500 goes
out, and £2,500.01 is held. That is deliberate and it is how it was
specified."

**What this proves:** you know exactly where the line sits.

---

## TEST 5 — A quote above the threshold

**You do:** Build a quote that comes to **£2,501**. Send it.

**Then show him:**

- Your inbox: **no quotation email arrives.** This is the point. Let the
  silence sit for a second
- support@buildregs.co.uk: a team email arrives saying it needs pricing by
  hand, and giving the reason
- FluentCRM, the contact: Quote Status says **Manual Review Required**
- FluentCRM, same contact: **Quote Sent is empty.** The quote was created
  but never sent, so there is no send date

**What this proves:** the approval cap works, the customer is never shown a
price that was not approved, and the record does not claim a quote was sent
when it was not.

---

## TEST 6 — A test payment

**You do:** Go back to the £2,499 quote from Test 3. Click the payment link
in the email. Pay with card `4242 4242 4242 4242`, any future expiry date,
any three-digit code.

**Then show him:**

| Tab | Point at | He should see |
|---|---|---|
| Stripe | Payments | The payment, and **Test mode** clearly showing |
| Your inbox | The receipt | Right name, and the amount matches Stripe exactly |
| Your inbox | Same receipt | A real date and time, not blank |
| FluentCRM | The contact | Quote Status now says **Paid** |
| FluentCRM | Same contact | Payment date, amount paid, currency, and the two Stripe reference numbers |
| support@ | The team email | "NEW PAID JOB", with a folder link that opens |

**What this proves:** money in, receipt out, record written, team told.

**Say this out loud:** "Stripe stays in test mode until you tell me in
writing to switch it."

---

## TEST 7 — A returning customer

**Only run this if I have built it before the call. Ask me first.**

**You do:** Submit the Upload Plans form again using an email address that
has already been through the system.

**Then show him:**

- FluentCRM, that contact: Quote Status says **Manual Review Required**
- FluentCRM, same contact: the **old** quote and payment figures are still
  there, untouched
- Your inbox: no quotation, no payment request
- support@buildregs.co.uk: a team email saying this is a returning customer
  with a second project

**What this proves:** exactly what he asked for. Nothing overwritten,
nothing sent by mistake, a human picks it up.

---

## The two real enquiries from Sunday

Open these before the call so you can speak to them:

- **James Pryer-Freeman**, 19 October, reference BR-20261019-093711
- **Aleksander Raszpla**, 19 October, reference BR-20261019-151057

Both came in on their own, both ran green, neither of us touched them.
Check their folders and CRM records look right, then tell him:

"Two genuine enquiries came in on Sunday and the system handled both without
anyone involved. They are sitting there waiting for quotes whenever you want
to price them."

That is the single best thing you can show him. It is not a test, it is the
thing actually working.

---

## At the end, say what is not finished

Keep it short and say it before he asks:

1. Stripe is in test mode and stays there until he says otherwise in writing
2. The team notices still go to the `support@buildregs.co.uk` placeholder,
   and the emails show a text wordmark rather than a logo. Both were parked
   by agreement, both are quick to change when he decides
3. If a project type is ever added to the website dropdown without being
   added to the price list, that enquiry stops quietly. Today the two are
   kept in step by hand. Worth putting on the Milestone 3 list
4. There is one empty leftover folder, `BR-20261015-220007`, that only he can
   delete because it belongs to his account
5. The test folders, records and the ZZ TEST scenario are all still in place,
   as he asked. He can clear them whenever he is ready

Then: "If you are happy with all of that, I will send the written handover
today and we can agree the Milestone 3 dates."
