# 3. Stripe checkout wording

Not an email. This is configuration set on the Stripe Checkout Session when it
is created, so it appears on the payment page itself.

## Product name (line item)

```
BuildRegs — {{approved_package_name}}
```

## Description shown under the product

```
Project: {{property_address}}
Quotation reference: {{quote_reference}}
```

## Custom message on the checkout page

```
Secure payment for the services set out in your BuildRegs quotation.

Once your payment is confirmed, we'll email your confirmation and next steps.

For any questions before paying, contact support@buildregs.co.uk.
```

## How this is applied

Set on the session at creation, in the Phase 2 Stripe module:

| Stripe field | Value |
|---|---|
| `line_items[0][price_data][product_data][name]` | `BuildRegs — {{approved_package_name}}` |
| `line_items[0][price_data][product_data][description]` | `Project: {{property_address}} · Quotation reference: {{quote_reference}}` |
| `custom_text[submit][message]` | the custom message above |
| `customer_email` | the customer's email, so they do not retype it |
| `metadata[quote_reference]` | the key Phase 3 uses to find the project row |
| `metadata[project_reference]` | the original enquiry reference |
| `success_url` | the thank-you page carrying template 4's wording |

The current module sends a generic `BuildRegs Quote` as the product name and
carries no description or custom text, so all of the above is new.

`metadata[quote_reference]` matters more than it looks: it is what lets the
payment find its own project row rather than guessing from the payer's email
address, which is what makes separate records per project work.
