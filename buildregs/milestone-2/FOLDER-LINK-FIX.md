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
