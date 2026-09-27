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
| 4 Download | `url` is now `{{trim(40.value)}}` — this iteration's URL, whitespace stripped (Forminator can emit `", "` between URLs). Error handler changed `Resume` -> `Ignore`. |
| 5 Upload | `filename` is now `{{ifempty(last(split(trim(40.value); "/")); 4.fileName)}}`. Error handler changed `Resume` -> `Ignore`. |
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
