#!/usr/bin/env bash
# Phase 1 (Intake) remaining tests. Run from your own machine.
# Scenario 7129360 must be ACTIVE (so switch Phase 3 OFF first).
# Everything here is verifiable inside Make alone.

URL="https://hook.eu1.make.com/au2y1gg4ki8u41w1zl6faw84is8mixuf"

echo "=== TEST A: guard filter. Payload has NO email. Must be BLOCKED. ==="
echo "Expect: run appears in history, stops at module 2 on the guard,"
echo "        1 operation, and NO new folder in Drive."
curl -X POST "$URL" -H "Content-Type: application/json" -d '{
  "names": { "first_name": "Guard", "last_name": "Test" },
  "phone": "07700 900123",
  "dropdown": "Loft Conversion",
  "description": "GUARD TEST - this should be blocked before any folder is created.",
  "__submission": { "id": "9101", "form_id": "4", "serial_number": "9101" }
}'
echo; echo
echo "Check Make history, then press Enter for TEST B."
read -r _

echo "=== TEST B: valid enquiry with NO file. Must SUCCEED. ==="
echo "Expect: folder BR-<date>-9102 created, no file inside,"
echo "        acknowledgement email saying 'Not received'."
curl -X POST "$URL" -H "Content-Type: application/json" -d '{
  "names": { "first_name": "Timmy", "last_name": "Afolly" },
  "email": "timmyafolly@gmail.com",
  "phone": "07700 900123",
  "dropdown": "Loft Conversion",
  "description": "NO FILE TEST - valid enquiry, nothing attached.",
  "file-upload": [],
  "__submission": { "id": "9102", "form_id": "4", "serial_number": "9102" }
}'
echo
