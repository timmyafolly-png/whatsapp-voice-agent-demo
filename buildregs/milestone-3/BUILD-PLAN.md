# Milestone 3 build plan — Sandeep's 20 Oct refinements

Written 22 Oct 2026. Target date requested: 30 October.

---

## Part A — What he is asking for, restated

### 1. Approval on every quotation

- Hold **all** quotations for his approval, not just those over £2,500. The
  £2,500 cap stops being a gate and becomes irrelevant.
- The enquiry acknowledgement keeps sending automatically.
- Quotations and payment requests only leave after he approves.
- **The India team must not be notified at enquiry or at quotation.** Their
  first contact with a job is after Stripe confirms payment.

### 2. Prepare and approve quotations from his iPhone

A secure page, opened from a "Review enquiry" button in the internal email,
showing the enquiry prefilled and letting him price it:

- Customer name, email, phone, address, project reference, already filled in
- The original enquiry text and a way to open the uploaded plans
- Dropdown for service package, multi-select for project types
- Standard prices applied automatically, with add a charge, reduce the fee,
  or enter a bespoke price
- Editable scope, exclusions, turnaround
- Private instructions for the India team, held back until after payment
- Buttons: Save draft, Request information, Preview and approve quotation
- **Saving or editing must send nothing**

Pricing rules:

- Combined projects at one property: **50% off one lowest-priced eligible
  project type**, applied once only, even with three or more types or equal
  prices. Never on a single type.
- He can override the discount
- Overlapping work must not be double-charged
- Trade discounts need his approval before stacking with the combined discount

Record keeping:

- Quotation and payment records **separate per project**, not per customer,
  so an architect with several jobs has several records
- Keep the returning-customer safeguard until that works
- Quote, Stripe amount and saved record must always agree
- Replacing a quote must kill or replace the old unpaid payment request
- Repeated clicks must not create duplicate payment requests

### 3. Payment, then India team handover

Only after Stripe confirms payment:

- Customer gets confirmation and next steps
- A project task is created for the India team and they are notified, with
  the reference and property, the approved scope, his private instructions,
  access to the correct plans folder, and the turnaround or target date
- The handover goes to the team **as well as** support@buildregs.co.uk
- If information is missing, the paid job is marked **Awaiting information**,
  and the delivery clock starts only when payment and all information are in
- He wants to know what of the original Stage 3 works and what does not

### 4. His review, then customer delivery

- Team uploads the finished package and marks it **Ready for review**
- He gets an email with links to the documents
- He requests corrections or approves
- After previewing documents and the prepared email, one tap on
  **Approve and send to client**
- Only approved final documents reach the client. Internal notes and working
  files stay private
- Project recorded as delivered afterwards

### 5. Customer follow-up

- Three days after delivery: check the documents arrived, offer help
- Seven days after delivery: invite an honest review using his link, sent
  regardless of how the check-in went, with no steering toward a star rating

### 6. Completion and launch

- Use his eight supplied email templates, placeholders filled automatically,
  small BuildRegs logo, consistent fonts, readable on a phone, payment and
  download links as labelled buttons
- "Hello" when there is no first name, his standard signature on every email
- Previews of everything before go live, including a combined-project
  quotation and a calculations-only quotation
- Sender is BuildRegs from support@buildregs.co.uk, replies to that inbox
- Forminator acknowledgement stays disabled
- One consolidated update separating completed work, remaining agreed work,
  and additional work with cost and time
- Full journey tested on his phone, specifically proving a quotation does
  **not** notify the India team and a payment does
- Stripe stays in test mode until he approves the switch in writing

### 7. Later addition

- Stripe link shown as a **"Proceed securely — £{{total}}"** button, branded,
  tappable, opening that customer's own checkout. No raw URL.

---

## Part B — How each piece gets built

The guiding decision: **nothing here needs a bespoke web application.**
Everything he described can be built from what is already in place, which is
why the date is tight rather than impossible.

### B1. The approval pages, without building an app

He described two screens: price a quote, and approve finished documents.
Both are solved by the same two mechanisms.

**Mechanism one: a private Fluent Forms page on his own site.**
The Quote Builder is already a Fluent Forms form on buildregs.co.uk posting
to a Make webhook. The review page is the same pattern, on a page that is not
publicly linked and is restricted. Fluent Forms is responsive, so it works on
an iPhone without extra work. Prefilling comes from URL parameters that Make
writes into the "Review enquiry" button, so the page opens with the customer
already in it.

**Mechanism two: one-tap signed links.**
Every approve, reject or send action is a button in an email that points at a
Make webhook carrying a long random token. One tap, no login, no typing. The
token is stored on the project record and checked on arrival, so the links
cannot be guessed and each one works once.

Together these give him: tap to open and price, tap to preview, tap to
approve. On a phone, in email, with no app to install and nothing new to host.

**Save draft without sending.** The Save draft button posts to a separate
Make webhook that writes the partial quote to the project record and stops.
No email module on that path, so it physically cannot send. Reopening the
review link reloads what he saved. This is deliberately handled on our side
rather than relying on a form plugin feature.

**Fallback if the site cannot host the page.** Make Interfaces can serve the
same form, and Sandeep already has a Make login. Slightly worse to use on a
phone, so it is the second choice, not the first.

### B2. Per-project records

This is the structural change, and it is the one that unlocks half the list.

Today a FluentCRM contact holds one project's worth of quote and payment
data, which is why a second enquiry from the same person collides with the
first. The fix is to stop keeping project data on the person.

**New Google Sheet, "BuildRegs Projects", one row per project,** keyed on the
quotation reference. It holds the customer, the property, the selected types
and package, scope, exclusions, turnaround, every price component, the
discount and any override, his private India-team notes, the status, the
Stripe session id, and the approval tokens.

A Sheet rather than a Make data store, for three reasons: he can open and read
it himself, it has no size ceiling worth worrying about, and the price list
already lives in Sheets so there is nothing new to learn.

FluentCRM keeps being the contact record: one person, one contact, their
details and their history. Projects live in the Sheet. That is exactly the
split he described.

**This also retires the returning-customer problem** rather than guarding
against it. He asked for the safeguard to stay until this works, so the order
is: build the manual-review safeguard first, then the per-project records,
then retire the safeguard once it is proven.

### B3. Pricing, discount and overlap

- Standard prices stay in the existing **BuildRegs Price List** sheet
- The review page carries a price per project type so the total updates as he
  taps, with the Sheet remaining the master
- **Combined discount:** of the selected types, take the lowest priced one and
  halve it. Only when two or more types are selected. Applied once, whatever
  the number of types and regardless of ties
- He gets an override box, so he can remove or change the discount
- **Overlap** is a judgement, not a rule. The page will show a warning when he
  selects types that commonly overlap, and give him the reduce-the-fee box to
  act on it. Automating a decision he has not defined would be worse than
  surfacing it to him
- **Trade discount** stays off until he defines it. When he does, it needs his
  tick before it can stack with the combined discount

One trade-off to know: prices live in both the Sheet and the review page's
calculation. If he changes a price in the Sheet, the page needs the same
change. Acceptable for launch; a small sync job removes it later.

### B4. Stripe, matching amounts and no duplicates

- The Stripe amount is built from the saved project row, never from anything
  typed twice, so the quote, the checkout and the record cannot disagree
- **Replacing a quote:** Stripe can expire a checkout session on request. On
  re-approval we expire the old session, then create the new one, so the old
  payment link dies rather than lingering
- **Repeated clicks:** before creating a session we check the project row. If
  an unpaid session already exists for this exact approved quote, we reuse it.
  Only a changed quote creates a new one
- **Checkout wording and branding** are set on the session itself, so the
  product name, the project and the reference appear at checkout as he wrote
- **The post-checkout page** needs Suhaib to update the thank-you page to his
  wording, worded so it stays true while a payment is still processing

### B5. Payment, then handover

Triggered only by Stripe's confirmation, which is already how Phase 3 works:

1. Customer confirmation and next steps, from his template 5
2. Project row flipped to paid, with the Stripe references recorded
3. **India team task created and notified** with reference, property,
   approved scope, his private notes, the folder link and the turnaround
4. Folder access granted to the team's addresses automatically
5. support@buildregs.co.uk notified alongside
6. If required information is missing, status set to **Awaiting information**
   and the delivery clock held until it arrives

**What of the original Stage 3 exists today:** the team notification works and
the plans-folder link works. **Task creation does not exist.** That is a
straight answer to his question. What a "task" should be is his call, and it
is in the questions below.

### B6. Review and delivery

1. Team marks a job **Ready for review**, either through a small form or by
   placing the package in a "Ready for review" subfolder that Make watches
2. He gets an email with links to the documents and a preview of the customer
   email as it will send
3. Buttons: **Approve and send to client**, or **Request corrections**
4. Approval sends his template 6 with a download link to a folder containing
   only the approved final documents, never the working files
5. Project row marked delivered, with the date, which starts the follow-up
   clock

Keeping internal files private is a folder discipline question, so the
structure will be: working files in one subfolder, approved output in another,
and only the second is ever shared.

### B7. Follow-ups

A single scheduled scenario, running once a day, reading the projects Sheet:

- Delivered three days ago, no check-in sent: send template 7
- Delivered seven days ago, no review request sent: send template 8,
  unconditionally, with no star-rating steer

This is the right pattern. Nothing sits waiting inside a scenario for days.

### B8. The eight emails

All eight rebuilt from his wording, on the existing template structure, which
already handles the logo, fonts, buttons and phone widths:

1. Enquiry acknowledgement, with the conditional file-receipt sentence, and
   confirming files only once they have actually saved
2. Approved quotation, with itemised fees and the discount, adjustment and
   conditions lines hidden when unused, and the **Proceed securely** button
3. Stripe checkout wording
4. Post-checkout page wording, for Suhaib
5. Payment received
6. Delivery after his approval
7. Three-day check-in
8. Seven-day review invitation

"Hello" where there is no first name, his signature on all eight.

---

## Part C — Sequence, and the 30 October question

Ordered so the launch-critical path lands first.

| # | Work | Days |
|---|---|---|
| 1 | Hold all quotations for approval; remove India team from enquiry and quote notifications | 0.5 |
| 2 | Projects Sheet, and rewire the quote and payment stages onto it | 1.5 |
| 3 | The eight email templates | 1.5 |
| 4 | Review page: prefill, package and types, pricing, discount, scope, notes | 2.5 |
| 5 | Save draft, Request information, Preview and approve, as one-tap links | 1.0 |
| 6 | Stripe: session expiry on replacement, duplicate protection, checkout wording and button | 0.5 |
| 7 | Payment to India handover: task, notification, folder access, Awaiting information | 1.0 |
| 8 | Ready for review, his approval, delivery to customer | 1.5 |
| 9 | Three and seven day follow-ups | 0.5 |
| 10 | Previews for him, then the full journey tested on his phone | 1.0 |

**About twelve working days of build.** From 22 October there are six working
days to 30 October.

So the honest position, and it is not a refusal: **the paying journey can be
live by 30 October.** Items 1, 2, 3, 6, 7 and the core of 4 and 5 get an
enquiry acknowledged, a quote priced and approved on his phone, a payment
taken, the customer confirmed and the India team handed the job. That is
BuildRegs trading, which is what he actually said he needs by the start of
November.

Items 8 and 9, the delivery approval flow and the follow-ups, are not needed
on day one. **Nothing can be delivered to a customer in the first week that
was not first paid for and produced**, so the delivery approval screen is
genuinely needed a week or two after launch, not before it. Proposing early
November for those is a sequencing argument, not a delay.

That split should be put to him as the recommendation, with the reasoning,
rather than either promising everything by the 30th or asking to move the date.

---

## Part D — What we need from him

Blocking. Each one stops a specific item above.

1. **The India team's email addresses**, and the Google accounts that need
   folder access. Blocks B5 entirely, and he asked us to confirm they can open
   the files, which cannot be tested without them.
2. **What a "project task" should be.** If the team uses a tool, which one and
   access to it. If not, the fastest honest answer is a shared task Sheet plus
   the email, and that can be built immediately.
3. **The review link** for template 8. He said he would provide it.
4. **The small BuildRegs logo**, or confirmation to resize the existing one.
   The file currently on the site is 1024px wide.
5. **Which project types overlap**, so the warning in B3 names real pairs
   rather than guessing.
6. **The trade discount rules**, if he wants them this round. Percentage, who
   qualifies, how it interacts with the combined discount.
7. **What counts as "required information"** for a job to be production ready,
   so Awaiting information can be judged rather than always manual.
8. **The service packages** as he wants them offered. The price list has Full
   and Structural-only. Confirm that is the list.
9. **Who hosts the review page.** Confirmation that Suhaib can add a
   restricted page on buildregs.co.uk, and who restricts it.
10. **Turnaround per package.** The price list says around 7 working days for
    everything. Confirm, or give the real figures.

Not blocking, but needed before go live:

11. Suhaib to update the post-checkout thank-you page to his template 4.
12. Confirmation that the £2,500 threshold is now retired rather than kept as
    a second gate on top of approving everything.
13. Whether the combined discount applies across packages or only within one.

---

## Part E — Things to watch

- **Operations.** The full journey is roughly 40 to 60 Make operations per
  paid job, against 10,000 a month on Core. Fine at current volume, worth
  watching if enquiries climb past roughly 150 a month.
- **The dormant duplicate webhook.** The old Fluent Forms enquiry form still
  has a live feed into Phase 1. Harmless only while that form stays off any
  public page. Worth disabling as part of this work.
- **Price list and dropdown drift.** A project type on the website with no row
  in the price list still halts silently. Worth fixing while the pricing is
  being rebuilt anyway.
- **Stripe stays in test mode** throughout, until he confirms in writing.
