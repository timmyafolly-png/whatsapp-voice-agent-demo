#!/usr/bin/env bash
# Phase 3 (Payment & Assignment) webhook tests.
# Run from your own machine. Scenario 7248863 must be ACTIVE.
# Each run costs about 5 operations.

set -e

echo "=== TEST 1: normal payment, metadata present ==="
curl -X POST https://hook.eu1.make.com/ilxwmxve3wtdobyjdvkw5yituvanp2ao \
  -H "Content-Type: application/json" \
  -d '{
  "id": "evt_test_pi_test_br9001",
  "object": "event",
  "type": "checkout.session.completed",
  "created": 1790138259,
  "livemode": false,
  "data": {
    "object": {
      "id": "cs_test_br9001",
      "object": "checkout.session",
      "created": 1790138259,
      "currency": "gbp",
      "status": "complete",
      "payment_status": "paid",
      "amount_total": 84900,
      "amount_subtotal": 84900,
      "payment_intent": "pi_test_br9001",
      "metadata": {
          "project_ref": "BR-Q-20260923-9001",
          "project_type": "Loft Conversion",
          "standard_price": "849",
          "final_price": "849",
          "client_email": "timmyafolly@gmail.com"
        },
      "customer_details": {
        "name": "Timmy Afolly",
        "email": "timmyafolly@gmail.com",
        "phone": null
      }
    }
  }
}'
echo
echo
echo "Wait for the run to finish, then check the results before continuing."
echo "Press Enter to run TEST 2, or Ctrl-C to stop here."
read -r _

echo "=== TEST 2: metadata.client_email MISSING, tests the fallback ==="
curl -X POST https://hook.eu1.make.com/ilxwmxve3wtdobyjdvkw5yituvanp2ao \
  -H "Content-Type: application/json" \
  -d '{
  "id": "evt_test_pi_test_br9002",
  "object": "event",
  "type": "checkout.session.completed",
  "created": 1790138259,
  "livemode": false,
  "data": {
    "object": {
      "id": "cs_test_br9002",
      "object": "checkout.session",
      "created": 1790138259,
      "currency": "gbp",
      "status": "complete",
      "payment_status": "paid",
      "amount_total": 84900,
      "amount_subtotal": 84900,
      "payment_intent": "pi_test_br9002",
      "metadata": {
          "project_ref": "BR-Q-20260923-9002",
          "project_type": "Loft Conversion",
          "standard_price": "849",
          "final_price": "849"
          
        },
      "customer_details": {
        "name": "Timmy Afolly",
        "email": "timmyafolly@gmail.com",
        "phone": null
      }
    }
  }
}'
echo
