# Client walkthrough video

`buildregs-walkthrough.mp4` — 70 seconds, silent with on-screen captions, 1280x720, H.264.
`buildregs-walkthrough.webm` — the raw capture the MP4 is encoded from.

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

**Representational.** Only the Drive folder listing is still built rather than captured.
It is drawn in Drive's own visual language — the same chrome, column headings and row
styling — but populated solely with BuildRegs content.

A real screenshot was offered and deliberately not used. It was a personal My Drive
and listed a dozen unrelated client folders by name, along with a storage quota. Putting
that in front of this client would have exposed the freelancer's other engagements. If a
genuine capture is ever wanted, it should be taken inside the Projects folder alone, with
no sidebar and no other client visible.

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

Deliver the MP4. It is H.264 in an MP4 container with `faststart`, so it plays
everywhere — Loom, QuickTime, email clients, phones — and is 2.7 MB against the
WebM's 4.9 MB.

Playwright captures only WebM (VP8), and the ffmpeg it bundles can encode nothing
else, which is why the first few versions of this were WebM only. The `imageio-ffmpeg`
pip package ships a full static ffmpeg 7.0.2 with libx264, and `make-mp4.sh` uses it to
re-encode. Run that after any re-record.

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

The video is silent, and the captions are there so that it does not need sound.

Narration is nonetheless possible now. The static ffmpeg used for the MP4 also carries
an AAC encoder, so a supplied voice recording can be muxed in:

```
ffmpeg -i buildregs-walkthrough.mp4 -i voiceover.m4a \
       -c:v copy -c:a aac -shortest buildregs-walkthrough-narrated.mp4
```

The catch is timing rather than tooling. Matching narration to the slide changes means
either recording against the running order in this README, or supplying one clip per
section so each can be laid over its own slide. Recording over the video live in Loom
avoids the problem entirely and remains the simpler route.
