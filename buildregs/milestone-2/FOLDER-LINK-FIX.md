# Phase 3 folder link — diagnosis

## Symptom

The "NEW PAID JOB" email to the team carries a button that opens the Projects
root folder instead of the individual client's project folder. The client
reported it twice.

## What module 21 was doing

```
jobFolderUrl = ifempty(30.data.subscribers.data[1].custom_values.drive_folder_url;
                       "https://drive.google.com/drive/folders/1XQGce...")
```

Module 30 is an HTTP GET to
`/wp-json/fluent-crm/v2/subscribers?search=<email>&with[]=custom_values`.
The `ifempty` fallback is the Projects root, so whenever the path resolves to
nothing the email silently points at the root. That is the observed behaviour,
so the path resolves to nothing on every run.

## Why the path was never trustworthy

It was written without ever looking at a real response. Outbound requests to
buildregs.co.uk are blocked from this environment, so the response could not be
inspected directly. Make can reach the site, so the response was captured by
running a throwaway scenario that writes the raw body to a Drive file, which can
then be read back.

## What the API actually returns

With `parseResponse` off, the raw body of the original lookup is:

```
{ "subscribers": { "current_page": 1,
                   "data": [ { ...subscriber... } ],
                   ... pagination ... },
  "custom": null }
```

and the subscriber object contains:

```
address_line_1, address_line_2, avatar, city, company_id, contact_owner,
contact_type, country, created_at, date_of_birth, email, first_name, full_name,
hash, id, ip, last_activity, last_name, latitude, life_time_value, lists,
longitude, phone, photo, postal_code, prefix, source, state, status, tags,
timezone, total_points, updated_at, user_id
```

There is no `custom_values` key. The contact is found — `total` is 1 — but the
custom field values are simply not in the payload, so no amount of correcting the
path would have helped. The array index was never the problem.

## Variants tested

| # | Request | Result |
| --- | --- | --- |
| A | `/subscribers/{id}?with[]=custom_values` | 831 bytes, no values |
| B | `/subscribers/{id}` plain | 831 bytes, no values |
| C | `/subscribers/{id}?with%5B%5D=custom_values` | 831 bytes, no values |
| D | `/subscribers/{id}?with%5B%5D=custom_fields` | 2,452 bytes — field **definitions** only |
| E | `with[]` sent as a proper query-string field | 831 bytes, no values |
| F | `custom_fields` + `custom_values` together | 2,452 bytes — definitions only |
| G | `with%5B%5D=custom_field_values` | 831 bytes, no values |
| H | `with%5B%5D=meta` / `subscriber_meta` | 831 bytes, no values |

D and F prove the `with[]` parameter is parsed and honoured — they return the
custom field schema, including `{"label": "drive folder url", "slug":
"drive_folder_url", "type": "text"}`. What this FluentCRM build will not return
over REST is the per-contact **values**. Writing them works (Phase 1 does it on
every enquiry); reading them back does not.

## Conclusion

This cannot be fixed by correcting the mapping. The lookup has to stop depending
on the CRM.

## Chosen replacement: a Make data store

The Free plan allows one data store of 1 MB (`dslimit: 1`, `dsslimit: 1048576`),
which is ample for a key/value table of project folders.

- Data structure `603902` "Project folder record": folderUrl, folderId,
  projectRef, clientName, createdAt
- Data store `199758` "BuildRegs project folders", keyed by client email
- Phase 1 writes a record when it creates the folder
- Phase 3 reads it instead of calling the CRM

Operations cost: Phase 1 gains one, Phase 3 stays level because the data store
read replaces the HTTP call it already spends.

Rejected alternatives:

- **Correct the CRM path** — impossible, the data is not served.
- **Store the URL in a standard field the API does return**, such as
  `address_line_2` — works, but puts a Drive URL in a contact's address in the
  client's own CRM UI. Poor to hand over.
- **Find the folder by name in Drive** — the natural fix, and the one the client
  is really asking for with "link by reference rather than email". It cannot be
  done yet because the intake reference (`BR-20260927-184851`) and the quote
  reference (`BR-Q-20260910-34`) are different values. Unifying them is quote
  builder work, which belongs to the separate order.

The data store keeps the current email-based matching, so it is a like-for-like
replacement that makes the existing design work rather than a redesign. When the
references are unified later, the same store can be re-keyed by reference.

## State of the backfill

`wahmed_2000@yahoo.co.uk` was written into the store by hand, pointing at
`BR-20260927-184851`, so the recovered enquiry resolves correctly once Phase 3 is
switched over.

## Deployed

### Phase 1 (7129360) — writes

New module **3b, "Remember folder for later phases"** (`datastore:AddRecord`),
placed in the main chain immediately after the folder is created and before the
CRM call and the emails, so the record exists before anything downstream could
need it.

```
key  = {{1.email_1}}
data = { folderUrl  : {{3.webViewLink}}
         folderId   : {{3.id}}
         projectRef : {{2.projectRef}}
         clientName : {{1.name_1_first_name}} {{1.name_1_last_name}}
         createdAt  : now, Europe/London }
overwrite = true
```

`overwrite: true` means a returning client's record is refreshed to their newest
enquiry rather than erroring on a duplicate key. A `Resume` error handler keeps
the rest of the enquiry running if the write ever fails, so a data store problem
can never cost a client their folder, CRM record or acknowledgement.

Cost: one extra operation per enquiry, 13 to 14.

### Phase 3 (7248863) — reads

Module 30 changes from `http:ActionSendData` (the CRM GET) to
`datastore:GetRecord` keyed on `{{8.payerEmail}}`. Module 21 now reads
`{{30.folderUrl}}` instead of the CRM path, keeping the same `ifempty` fallback
to the Projects root so an unknown payer still produces a working button.

Module 21 also gains `intakeRef` from `{{30.projectRef}}`, and the team email now
shows an "Enquiry ref" line. That is the first time the payment side can display
the intake reference, because until now it had no way to reach it — the two
references being different values is the open scope question, and this at least
puts both in front of the team.

Cost: unchanged. The data store read replaces the HTTP call it already spent.

## Tested before activation

**Read**, executed live against the store (scenario 7636164, proof written into a
Drive folder name because module outputs are not readable through the API):

```
ZZPROOF hit=BR-20260927-184851 miss=FELLBACK
```

A known key resolves to the right project reference; an unknown key falls back
without erroring, so a payment from someone with no matching enquiry cannot break
the scenario.

**Write**, the same mapping Phase 1 uses, run against a fake payload and then read
back out of the store:

```
key: zz-writetest@example.com
  folderUrl  : https://drive.google.com/drive/folders/FAKEFOLDERID123
  folderId   : FAKEFOLDERID123
  projectRef : BR-WRITETEST-054015
  clientName : Write Test
  createdAt  : 2026-09-28 05:40:15
```

All five fields populated, including the concatenated name and the formatted
timestamp. The test record was deleted afterwards; the store holds only the real
backfilled record for the recovered enquiry.

One snag worth noting: `datastore:GetRecord` rejected a configuration that looked
complete, reporting only "Validation failed for 1 parameter(s)" without naming it.
Make's own module validator identified the missing field as `returnWrapped`.

## State

| Scenario | State |
| --- | --- |
| 7129360 Phase 1 Intake | active, writes the record |
| 7248863 Phase 3 Payment | active, reads the record |
| 7229882 Phase 2 Quote Builder | off, per the client's instruction on quote safeguards |
| 7636164 ZZ TEST harness | off, scheduling set to on-demand so it cannot self-fire |

## Not yet proven end to end

Neither scenario has been exercised by real traffic since the change. The write
is proven in isolation and the read is proven against a real stored record, but
no enquiry has yet gone through Phase 1 and out of Phase 3 in one pass. The
recovered enquiry's record was backfilled by hand, so the team email for that
client would already resolve correctly if a payment arrived now.
