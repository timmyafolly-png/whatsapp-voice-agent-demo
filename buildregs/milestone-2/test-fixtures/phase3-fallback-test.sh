#!/usr/bin/env bash
# Phase 3 FALLBACK test. Scenario 7248863 must be ACTIVE.
# metadata.client_email is deliberately absent. The receipt must still
# reach the customer via data.object.customer_details.email.

curl -X POST https://hook.eu1.make.com/ilxwmxve3wtdobyjdvkw5yituvanp2ao \
  -H "Content-Type: application/json" \
  -d '{
  "id": "evt_test_br9004",
  "object": "event",
  "type": "checkout.session.completed",
  "created": 1790223294,
  "livemode": false,
  "data": {
    "object": {
      "id": "cs_test_br9004",
      "object": "checkout.session",
      "created": 1790223294,
      "currency": "gbp",
      "status": "complete",
      "payment_status": "paid",
      "amount_total": 74900,
      "amount_subtotal": 74900,
      "payment_intent": "pi_test_br9004",
      "metadata": {
        "project_ref": "BR-Q-20260924-9004",
        "project_type": "Garage Conversion",
        "standard_price": "749",
        "final_price": "749"
      },
      "customer_details": {
        "name": "Timmy Afolly",
        "email": "timmyafolly@gmail.com",
        "phone": null
      }
    }
  }
}'
