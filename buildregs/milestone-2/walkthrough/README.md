# Client walkthrough video

`buildregs-walkthrough.webm` — 60 seconds, silent, 1280x720.

## How it was made

Rendered in headless Chromium and captured with Playwright's video recorder, from
`walkthrough-source.html` in this folder. Re-running `record.js` against that page
regenerates it, so the video can be rebuilt after the system changes rather than
re-recorded by hand.

## What is real and what is not

**Real.** The customer acknowledgement email is the exact HTML deployed in Phase 1,
lifted from the live blueprint with the Make placeholders filled in. The team
enquiry email, the paid-job email and the failure alert are likewise the deployed
wording.

The real BuildRegs logo is embedded as a data URI, since this environment cannot
reach buildregs.co.uk to fetch it at render time. The Upload Plans form and the
FluentCRM record are real screenshots supplied by the freelancer.

**Representational.** Only the Drive folder listing is still an illustration. It shows
the right filenames and sizes in the right layout, but it is not a screenshot. Replace
it with a real one when convenient — the folder for the recovered enquiry would do.

**Known inconsistency.** The CRM screenshot is a genuine record and carries the
reference `BR-20260927-184851` with project type `Other`, while the rest of the video
follows a fictional customer with reference `BR-20260928-091245` and a single-storey
extension. A viewer comparing the two slides closely would notice. Left as is because
the alternative — relabelling the whole video `Other` to match — reads worse. Swapping
the CRM slide for an illustrated record with matching data is a small change if the
client ever raises it.

**Invented.** The customer is fictional — Sarah Whitfield, 14 Oakfield Road,
reference `BR-20260928-091245`. No real client's name, email or address appears
anywhere, deliberately: the genuine recovered enquiry belongs to a real person and
should not be in a promotional video. The CRM screenshot shows only a reference and a
folder URL, no personal details.

## Running order

| Time | Section |
| --- | --- |
| 0:00 | Title |
| 0:03 | Customer submits plans, three files |
| 0:09 | Branded acknowledgement to the customer |
| 0:18 | Team enquiry email with the folder link |
| 0:26 | Files in a folder named by reference |
| 0:33 | CRM record created |
| 0:40 | Paid job handed to the team |
| 0:47 | Failure alert — nothing fails quietly |
| 0:55 | Close |

## Format

WebM (VP8). Plays in Chrome, Firefox and Edge. Safari and QuickTime may not open it,
and the container has no H.264 encoder, so an MP4 could not be produced here. Two
straightforward routes: play it in a browser and record over it in Loom with a
voiceover, which also solves the lack of narration, or convert it with any desktop
tool or an online converter.

## Not covered

The video shows outcomes, not the Make canvas. Screen-recording Make itself was not
possible from here: it needs a logged-in browser session, and the account has
two-factor authentication.


## Audio

The video is silent and cannot be given a soundtrack here. The only ffmpeg available
is the one Playwright bundles, which has no audio encoders at all and can encode video
only as VP8. Supplying a voice recording would not help, because there is nothing in
this environment able to combine it with the picture.

The practical route is to play the file in a browser and record over it in Loom with a
live voiceover. That produces narration and an MP4 in one step, and solves the format
limitation at the same time. The alternative, if a silent file is wanted, is on-screen
captions, which can be added to the source page and re-rendered.
