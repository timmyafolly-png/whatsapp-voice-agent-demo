# Phase 1 webhook queue — archived payloads, 15 October 2026

Hook 3611527 (BuildRegs Phase 1 - Intake). Five items were queued while the
scenario was inactive. Every payload is saved here verbatim before any
deletion, so a misclassified item can be re-posted to the webhook and
processed normally.

| File | Queued | Name | Email | Payload shape | Verdict |
|---|---|---|---|---|---|
| `01-naikoo-suhaib-TEST.json` | 9 Oct 07:42 | Naikoo Suhaib | cluesarena@gmail.com | old | test — "Testing the form", Sandeep's test address |
| `02-jack-broadway-GENUINE.json` | 9 Oct 20:33 | Jack Broadway | jack@studiopcm.co.uk | old | GENUINE customer — process, suppress all customer email |
| `03-shivani-mann-TEST.json` | 11 Oct 09:36 | Shivani Mann | shivanimann@hotmail.co.uk | new | test — message body "Tati" |
| `04-shivani-mann-TEST.json` | 11 Oct 09:37 | Shivani Mann | Shivani_Mann@statestreet.com | new | test — duplicate, empty message |
| `05-clues-arena-TEST.json` | 14 Oct 12:42 | Clues Arena | cluesarena@gmail.com | new | test — Sandeep's own entry #31, message body "test" |

To replay one:

    curl -X POST https://hook.eu1.make.com/au2y1gg4ki8u41w1zl6faw84is8mixuf \
      -H 'Content-Type: application/json' --data @02-jack-broadway-GENUINE.json
