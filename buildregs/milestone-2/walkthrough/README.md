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

**Representational.** The form page, the Drive folder listing and the CRM record are
clean illustrations built for the video. They show the right fields with the right
values, but they are not screenshots of the real interfaces. Anyone presenting this
should describe it as a walkthrough of what the system produces, not as screen
capture.

**Substituted.** The header logo is a text wordmark rather than the hosted image,
because this environment cannot reach buildregs.co.uk to fetch it. Real emails show
the proper logo. Replacing the `<span>` with the original `<img>` tag in
`walkthrough-source.html` restores it if the video is rebuilt somewhere with access.

**Invented.** The customer is fictional — Sarah Whitfield, 14 Oakfield Road,
reference `BR-20260928-091245`. No real client's details appear, deliberately: the
genuine recovered enquiry belongs to a real person and should not be in a
promotional video.

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
