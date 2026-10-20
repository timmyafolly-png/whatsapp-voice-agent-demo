# The £2,500 cap — what controls it, and how to test it

---

## 1. Where the price comes from

Two things add up to the quote total:

```
Standard Price (looked up from the price list)
      +   Adjustment (the number you type in the Quote Builder)
      =   Final Price
```

The **price list** is a Google Sheet called **BuildRegs Price List**.
Column A is the project type, column B is the standard price, column C says
whether it is bespoke.

Here is what is actually in it right now:

| Project type you pick | Standard price | Bespoke? |
|---|---|---|
| Single-Storey Extension | £799 | No |
| Double-Storey Extension | £999 | No |
| Loft Conversion | £849 | No |
| Garage Conversion | £749 | No |
| Structural Opening / RSJ Calculations | £249 | No |
| Outbuilding | £749 | No |
| New Build House | *(blank)* | **Yes** |
| Combined / Non-Standard Project | *(blank)* | **Yes** |

So when you pick "Single-Storey Extension" in the Quote Builder, the
automation looks up £799 by itself. You do not type that. You only type the
adjustment.

---

## 2. What actually controls the cap

**One scenario, one module, one line.**

- Scenario: **BuildRegs Phase 2 — Quote Builder to Stripe**
- Module: **"6. Decide: auto-quote or manual review"**
- The line: `finalPrice > 2500`

That module does not send anything. All it does is make one decision and
write down a yes or a no. Then the next module along, the **router**, reads
that yes or no and picks which of two paths the quote goes down:

```
                  ┌─ YES, needs review ─→  mark CRM "Manual Review Required"
   the decision ──┤                        + email the team
                  └─ NO, send it ───────→  mark CRM "Quote Sent"
                                           + create Stripe link
                                           + email the quote to the customer
```

**The important part:** on the review path there is no Stripe step and no
customer email. The quote physically cannot reach the customer. It is not
that it is held back politely, it is that those modules are not on that path
at all.

---

## 3. The four things that send a quote to review

Any **one** of these is enough. They are not combined.

1. The project type has no price in column B
2. The project type is marked Bespoke in column C
3. The final price is **above £2,500**
4. The final price comes out as zero or less

Number 3 is the cap Sandeep asked about. Numbers 1 and 2 are why
"New Build House" and "Combined / Non-Standard Project" always go to review
no matter what the price is.

---

## 4. How to test the cap — the exact numbers to type

Use **Single-Storey Extension** every time, because its standard price is
£799 and the sums are easy.

| Test | Project type | Adjustment you type | Total | What should happen |
|---|---|---|---|---|
| Just under | Single-Storey Extension | `1700` | £2,499 | **Sends automatically** |
| Exactly on the line | Single-Storey Extension | `1701` | £2,500 | **Sends automatically** |
| Just over | Single-Storey Extension | `1702` | £2,501 | **Held for review** |

That is the whole test. Three quotes, one pound apart at the top end.

**Why £2,500 itself sends:** the rule is "above £2,500". £2,500 is not above
£2,500. So it goes out. £2,500.01 would be held. This is deliberate and it is
how it was specified on 6 October.

---

## 5. What to show him after each one

**After £2,499 and after £2,500 (the two that send):**

- Your inbox: the quotation email arrived, with a payment link in it
- FluentCRM, the contact: Quote Status reads **Quote Sent**
- FluentCRM, same contact: Standard Price £799, Adjustment, Final Price,
  and both Quote Created and Quote Sent have dates

**After £2,501 (the one that is held):**

- Your inbox: **nothing arrived.** Pause here. This is the whole point
- support@buildregs.co.uk: a team email arrived saying it needs pricing by
  hand, and giving the reason in plain English
- FluentCRM, the contact: Quote Status reads **Manual Review Required**
- FluentCRM, same contact: **Quote Sent is empty.** The quote was created but
  never sent, so there is no send date. Quote Created has a date, Quote Sent
  does not
- Stripe: no new payment link was created

That last pair is the detail worth pointing out. The record does not claim a
quote went out when it did not.

---

## 6. A second, easier way to show the same thing

If you want to demonstrate the review path without doing the arithmetic,
pick **New Build House**. It has no price and is marked Bespoke, so it goes
to review every single time regardless of what you type.

Useful if a number test goes wrong on the call and you need to show the
review path another way.

---

## 7. If he asks to change the cap

Say: "It is one number in one place, I can change it in two minutes."

Then be aware, for yourself, that it is actually **two** edits in the same
module. The number appears in the decision itself, and again in the wording
of the team email that explains why a quote was held. If only the first is
changed, the email will keep quoting the old figure at whoever picks the job
up. Change both.

---

## 8. One thing to test before the call

Run a quote with the adjustment box **left empty**, on a normal project type.

That is the most common real-world quote, and it is the one combination that
has never been run. The final price is calculated as standard price plus
adjustment, so it is worth confirming an empty adjustment reads as zero and
gives you £799 rather than an error.

Do that one first, before you do the three cap tests.

---

## 9. Which form, and which box is the adjustment

**The form is the Quote Builder:**

> **https://buildregs.co.uk/quote-builder/**

That is the live page. There is also an older page at
`/quote-builder-internal/` which is retained but not the one in use.

This is a **Fluent Forms** form, and it posts straight to a fixed Make
webhook. The page it sits on does not matter to the automation.

### What the automation actually reads from that form

The form sends eight fields. The automation only uses four of them:

| Form field name | What the automation does with it |
|---|---|
| `email` | The customer's email. Everything is keyed off this |
| `dropdown` | The project type. This is what looks up the standard price |
| `numeric_field_1` | **The adjustment.** This is the box that moves the total |
| `input_text` | The adjustment reason. Goes to the CRM only |
| `numeric_field` | **Ignored.** Nothing reads it |
| `numeric_field_2` | **Ignored.** Nothing reads it |
| `input_text_1` | **Ignored.** Nothing reads it |

**Watch out for this.** There are three boxes on that form that the
automation does not read at all. If you type your adjustment into the wrong
numeric box, the total will not move and the quote will go out at the plain
standard price. On a live call that would look like the cap had failed when
in fact nothing was ever adjusted.

### How to be certain which box is which, before the call

Submit one throwaway quote with a number you would recognise, say `1234`,
in whichever box you think is the adjustment. Then open Make, Phase 2,
History, click the run, and click the first module. You will see the raw
payload the form sent, with the field names next to the values. If `1234`
is sitting next to `numeric_field_1`, that is the right box.

One run settles it, and you will not be guessing in front of him.

### Optional: hitting the numbers exactly, without the form

If you want to rehearse the cap precisely, you can post to the webhook
directly from your own machine. Run this in a terminal, changing the email to
your own:

```
curl -X POST https://hook.eu1.make.com/17mavo7znmwtdbrw99dgy9lcsg4o2wo7 \
  -H "Content-Type: application/json" \
  -d '{
    "email": "YOUR-EMAIL@example.com",
    "dropdown": "Single-Storey Extension",
    "numeric_field_1": "1702",
    "input_text": "Threshold rehearsal",
    "__submission": { "serial_number": "9101" }
  }'
```

`1701` gives £2,500 and should send. `1702` gives £2,501 and should hold.

Two warnings. This is the live scenario, so it really will create a Stripe
test session, really will email the address you put in, and really will write
to the CRM. Use your own email address, and change `serial_number` each time
so each test gets its own reference.

Use the form itself for the actual demo. Sandeep should see the real journey,
not a terminal.
