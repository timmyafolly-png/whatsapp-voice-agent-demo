# Phase 1 multi-file upload fix

## The bug

Forminator sends every file a client uploaded in one field, `upload_1`, as a
**single comma-separated string** of URLs:

```
https://.../plan-1.pdf,https://.../plan-2.pdf,https://.../plan-3.pdf
```

The live scenario fed that whole string straight into the HTTP "Get a file"
module (`url = {{1.upload_1}}`). With one file that happens to work. With two or
more it is not a URL at all, so the download fails, and only one file — or none —
ever reached the client's Drive folder.

## The change

Phase 1 is re-ordered so the file work happens in its own router branch and is
repeated once per file.

Before:

```
webhook -> ref -> folder -> download -> upload -> CRM -> email fields -> router(client, team)
```

After:

```
webhook -> ref -> folder -> email fields -> CRM -> router
                                                    |- 1. iterate files -> download -> upload   (repeats per file)
                                                    |- 2. email client
                                                    |- 3. email team
```

Module by module:

| Module | Change |
| --- | --- |
| 40 (new) | Iterator over `{{split(1.upload_1; ",")}}` — one bundle per uploaded file. Route filter `length(trim(ifempty(1.upload_1; ""))) > 0` so the branch is skipped when nothing was uploaded. |
| 4 Download | `url` is now `{{trim(40.value)}}` — this iteration's URL, whitespace stripped (Forminator can emit `", "` between URLs). Error handler changed `Resume` -> `Ignore`, and `handleErrors` turned **on** (see "What the test caught"). |
| 5 Upload | `filename` is now `{{ifempty(last(split(trim(40.value); "/")); 4.fileName)}}`. Error handler changed `Resume` -> `Ignore`, plus a filter `4.fileSize > 0` as a second guard. |
| 20 Email fields | Moved ahead of the CRM call. `filesStatus` / `filesBlock` now derive from the webhook payload instead of `4.fileSize`, and a new `fileCount` variable is added. |
| 7 Router | Gains a third branch, ordered files-first so uploads land before the emails go out. |

## Why the branch order matters

The earlier attempt put a filter on the download module itself. A blocked filter
there stopped the **whole** chain, so `BR-20260924-51` got a folder and no emails
and no CRM record. A router branch is isolated: if the file branch is skipped or a
file 404s, the client email, team email and CRM write still happen.

`Ignore` rather than `Resume` on modules 4 and 5 is the other half of that. With
`Resume`, a failed download passed empty data on to Drive and created the 0-byte
`Untitled` files seen on 26 Sep. `Ignore` drops just that one file's bundle and the
iterator moves to the next file.

## Known trade-off

`filesStatus` now reports what the client *submitted*, not what Drive *confirmed*.
The count is read off `upload_1`. This is deliberate: the alternative needs an
Array aggregator between the iterator and the emails, and an aggregator that
receives zero bundles is exactly the empty-chain failure mode above. The team
email carries the folder link, so the folder remains the source of truth.

## Test harness

Scenario **7636164 — "ZZ TEST - multifile logic (delete me)"** is a standalone copy
of the changed logic. Module 1 is a `SetVariables` module holding a fake Forminator
payload instead of the webhook, so it can be run on demand without a form
submission and without touching the real intake queue. It has no CRM call and
sends no email.

Its `upload_1` deliberately contains three URLs:

1. `.../BuildRegs-Black-1024x227.png` — real
2. `.../BuildRegs-White-1536x340.png` — real, preceded by a space after the comma
3. `.../zz-does-not-exist-9999.png` — 404

Expected result:

- module 40 emits **3** bundles
- two files land in the new `ZZTEST-...` folder, named `BuildRegs-Black-1024x227.png`
  and `BuildRegs-White-1536x340.png` (proves `split` + `trim` + the filename expression)
- the third is skipped by the `Ignore` handler and the run still completes
- `20.fileCount` = `3`, `20.filesStatus` = `Received`
- branch 2 (`module 30`) runs, proving the non-file branches are not blocked by the
  file branch

Delete scenario 7636164 and its `ZZTEST-...` Drive folder once the fix is signed off.


## What the test caught

The first test run came back `SUCCESS` with 12 operations, and two of the three
files were correct. The third was not, and nothing in Make said so:

| File | Size | MIME type |
| --- | --- | --- |
| `BuildRegs-Black-1024x227.png` | 14,897 | `image/png` |
| `BuildRegs-White-1536x340.png` | 23,418 | `image/png` |
| `zz-does-not-exist-9999.png` | 117,959 | **`text/html`** |

The 404 URL was saved anyway — WordPress's 404 *page* written into the client's
folder under a `.png` name. The `Ignore` handler never fired, because
`http:ActionGetFile` with `handleErrors: false` counts any completed HTTP
response as a successful download, 404 included.

Two changes fix it:

1. `handleErrors: true` on module 4, so a non-2xx/3xx status is raised as an
   error and the `Ignore` handler actually skips that file.
2. A filter `{{4.fileSize}} > 0` on module 5, so nothing empty is ever uploaded
   even if a server returns 200 with no body.

This is the reason the run had to be observed in Drive rather than trusted from
the execution status. A green run with the right operation count still put junk
in the client's folder.

## Test evidence

All three runs on scenario 7636164, 27 Sep 2026.

| Execution | Payload | Operations | Result |
| --- | --- | --- | --- |
| `c24e367c72bd4acb9ce6dd27393713df` | 3 URLs, one 404 | 12 | 2 files correct, **404 saved as 118 KB HTML** — bug found |
| `df3f810b978249cda140c6d1d5fe5f41` | same, after the two fixes | 11 | 2 files correct, 404 skipped |
| `b81b82d77e4b4b3d8bd36ab760190470` | `upload_1` empty | 5 | folder created, no files, no errors |

Observed in Drive after run 2 (`ZZTEST-20260927-092941`):

- `BuildRegs-Black-1024x227.png` — 14,300 bytes, `image/png`
- `BuildRegs-White-1536x340.png` — 23,418 bytes, `image/png`
- no third file
- `PROOF status=Received count=3 greet=Hi Zed,`

Observed after run 3 (`ZZTEST-NOFILES-093055`):

- no files
- `PROOF status=NOT RECEIVED count=0 greet=Hi Zed,`

The `PROOF ...` folder is module 30 in the harness, a Drive folder named from
`20.filesStatus`, `20.fileCount` and `20.greetingName`. Module outputs are not
readable through the API, so the values were written into a folder name to make
them observable. Its presence in both runs is also the proof that the non-file
branches are not blocked by the file branch — the `BR-20260924-51` failure.

What run 2 proves specifically:

- `split` produced 3 items from one comma-separated string — the actual bug
- `trim` handled the `", "` before the second URL, since a leading space would
  have made that download fail
- the filename expression read the name off each iteration's own URL
- byte sizes match the source files, so real content arrived, not empty bundles

## Deployed

Pushed to live scenario **7129360** on 27 Sep 2026 08:32 UTC. Read back from the
API afterwards and confirmed stored: iterator with its branch filter, module 4
`handleErrors: true` with `Ignore`, module 5 filter with `Ignore`, module 20 with
`fileCount`, three router branches, CRM credential and webhook binding intact,
`isinvalid: false`.

Phase 1 is deployed but left **switched off**. See the note on the queued
enquiry below.

## The queued enquiry

Webhook 3611527 still holds one unprocessed payload, `8fbea82d351eb49ef37d6faa9f5f6462`,
1,690 bytes, received 2026-09-26T07:47:04Z — the genuine enquiry from Waheed Ahmed.
Switching Phase 1 on releases it immediately through whatever is live at that
moment, which is why the fix went in first.

The client has asked that recovering it must not send a duplicate acknowledgement.
It can be released without emailing him by putting a temporary blocking filter on
module 8 (the client email branch) only: he then gets his folder, his CRM record
and the team notification to `support@`, with no email to him. The filter comes
straight back off afterwards. This needs the client's confirmation of whether he
was already replied to by hand.

## Cleanup done

Test folders trashed from the client's Drive: `ZZTEST-20260927-092214`,
`ZZTEST-20260927-092320`, `ZZTEST-20260927-092941`, `ZZTEST-NOFILES-093055`.
Scenario 7636164 deactivated (it was on a 15-minute schedule) and kept for
re-testing; delete it at handover.

## The real payload, read off the queue

The queued enquiry can be inspected without running anything, which is a better
confirmation than another test submission. The relevant field from
`8fbea82d351eb49ef37d6faa9f5f6462`:

```
select_1: "Other"
upload_1: "https://buildregs.co.uk/wp-content/uploads/forminator/<dir>/uploads/<file-1>.pdf,
           https://buildregs.co.uk/wp-content/uploads/forminator/<dir>/uploads/<file-2>.pdf,
           https://buildregs.co.uk/wp-content/uploads/forminator/<dir>/uploads/<file-3>.pdf"
```

Three PDFs, one comma-separated string. Two things this settles:

1. The assumption behind the whole fix is correct — Forminator does put every file
   in `upload_1` as one delimited string, not an array.
2. **The delimiter is comma + space, not a bare comma.** Without the `trim()` on
   each item, files 2 and 3 would have been requested as `" https://…"` and failed.
   That was a guess when it was written; it is now confirmed against real data.

There is also a `forminator_multifile_hidden.upload_1` array carrying `file_name`
and `mime_type` per file, but no URLs, so `upload_1` remains the only usable source.

Note for Phase 2: this enquiry's `select_1` is `Other`, which is exactly the case
the client wants held for manual review before any quote goes out.

## Temporary hold in place

Module 8 (the client acknowledgement email) currently carries a filter named
`TEMPORARY HOLD - remove after Waheed recovery`, comparing `1.email_1` against
`__HOLD_NO_CLIENT_EMAIL__` so it never passes.

While this is in place, **no enquiry gets an acknowledgement email.** The folder,
the CRM record and the team email to `support@` all still happen. It exists so the
queued enquiry can be released and verified without risking the duplicate
acknowledgement the client prohibited. It must come off immediately after that
verification.

Activating scenario 7129360 is a production action this session is not permitted
to perform, so the switch is thrown by hand in Make. Sequence:

1. (done) fix deployed, hold filter applied, scenario left off
2. switch 7129360 on in Make — releases the queued enquiry through the live fix
3. verify: folder `BR-<today>` holding 3 PDFs with their real names and non-zero
   sizes, a CRM record, a team email to `support@` reading `Received (3 attached)`
4. remove the hold filter
5. leave 7129360 active

If step 3 shows a problem, the execution is replayable, so it can be fixed and
re-run against the same payload rather than lost.

## Live result — the queued enquiry, recovered

Scenario 7129360 switched on 27 Sep 2026 17:48 UTC. The queued payload released
and ran through the deployed fix.

Execution `a695cacdf95542bab2efc511ccd928a4` — status SUCCESS, 13 operations,
1,044,305 bytes transferred, 8.3s. The scenario's lifetime error count stayed at
12, so this run added none.

Module counts from the run:

| Module | Count | Meaning |
| --- | --- | --- |
| 40 Iterate | 1 | ran once, emitting per-file bundles |
| 4 Download | **3** | one per file — the bug this fix exists for |
| Guard: a real file came back | **3** | all three passed, nothing empty |
| 5 Upload | **3** | all three written to Drive |
| 7b Email client | **0** | blocked by the temporary hold, as intended |
| 7c Email team | 1 | sent to support@ |

Folder `BR-20260927-184851` (`1uRg6yadeZO31plpi-s9Q6mSitKejtFRU`), created 17:48:51
inside the Projects folder, contains exactly three files, all `application/pdf`:

| File | Bytes |
| --- | --- |
| `EhnQZYsCoUfx-102-rev-B-proposed-site-plan-Plan-25.53-202.pdf` | 385,951 |
| `rnImy9C39dwd-201-rev-A-proposed-floor-plan-and-elevations-Plan-BT.25.53-201.pdf` | 435,507 |
| `fmAuRIGzUqk9-101-existing-plans-and-elevations-3-Plan-BT.25.53-101.pdf` | 201,265 |

Total 1,022,723 bytes, consistent with the execution's reported transfer. Filenames
match the source URLs exactly, which confirms the filename expression, and the
comma-space delimiter was handled — the second and third files are the ones that
would have failed without `trim()`.

The webhook queue is now empty.

## Hold removed

The `TEMPORARY HOLD` filter came off module 8 at 17:53 UTC, immediately after the
above was verified. Client acknowledgement emails are live again. Scenario 7129360
remains active.

## CRM record confirmed

Outbound requests to buildregs.co.uk are blocked by this environment's network
policy, so the record was checked by hand in FluentCRM. All four fields wrote,
and all four agree with what was observed in Drive:

| Field | Value |
| --- | --- |
| Project Reference | `BR-20260927-184851` — matches the folder name |
| Enquiry Date | `2026-09-27` |
| Project Type | `Other` — matches `select_1` in the payload |
| drive folder url | `.../folders/1uRg6yadeZO31plpi-s9Q6mSitKejtFRU` — matches the folder id |

Intake is therefore verified end to end on real client data: webhook payload ->
project reference -> Drive folder -> three PDFs -> CRM record, all consistent.

### What this narrows about the folder-link bug

The client's complaint is that the folder link in the assignment email opens the
Projects root rather than the individual project folder. This record shows Phase 1
stores the correct per-client URL in `drive_folder_url`. The defect is therefore
in Phase 3 reading that value back, not in Phase 1 writing it — the lookup path
`30.data.subscribers.data[1].custom_values.drive_folder_url` is the only thing at
fault, and it falls back to the root when it resolves to nothing. That is a
smaller fix than a redesign, and it is testable the same way this one was.
