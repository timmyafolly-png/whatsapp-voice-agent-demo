# Client walkthrough video

`buildregs-walkthrough.webm` — 68 seconds, silent with on-screen captions, 1280x720.

## How it was made

Rendered in headless Chromium and captured with Playwright's video recorder.
`walkthrough-template.html` holds the layout and `slides.json` the content; the build
substitutes one into the other to produce `walkthrough-source.html`, which `record.js`
then records. Editing content means editing `slides.json`, not the rendered page. The
video can therefore be rebuilt after the system changes rather than re-recorded by
hand.

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
| 0:06 | Customer submits plans |
| 0:13 | Branded acknowledgement to the customer |
| 0:22 | Team enquiry email with the folder link |
| 0:30 | Files in a folder named by reference |
| 0:38 | CRM record created |
| 0:46 | Paid job handed to the team |
| 0:55 | Failure alert — nothing fails quietly |
| 1:03 | Close |

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


## Captions

Every slide carries a caption across the bottom in a navy bar, so the video reads
without sound. The wording lives in `slides.json` under each slide's `caption` key,
and the hold times in `record.js` were lengthened to give each one time to be read —
roughly reading speed plus a beat. Editing a caption means editing that key and
re-running the recorder; changing its length means revisiting the matching entry in
`HOLD`.

## Audio

The video is silent and cannot be given a soundtrack here. The only ffmpeg available
is the one Playwright bundles, which has no audio encoders at all and can encode video
only as VP8. Supplying a voice recording would not help, because there is nothing in
this environment able to combine it with the picture.

The captions above make the file usable as it stands. If narration is still wanted,
play it in a browser and record over it in Loom, which produces a voiceover and an MP4
in one step and solves the format limitation at the same time.
