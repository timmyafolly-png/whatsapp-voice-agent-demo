# Failure alerts

## The problem behind the client's request

The client asked to be told when a scenario stops. That is real, but it is the
less likely of two failure modes, and the other one was completely silent.

Every risky step in both scenarios carries a `Resume` or `Ignore` error handler.
Several were added deliberately during this milestone, because one bad file
should not cost a client their folder, their CRM record and their
acknowledgement. The cost of that choice is that a failure leaves no trace a
person would notice: the run still reports success, the operation count still
looks right, and the only evidence is a missing record nobody is looking for.

That is exactly how the CRM write failed on every enquiry for weeks without being
noticed.

So there are two things, and they need different fixes:

| | Failure | Fix |
| --- | --- | --- |
| A | A step fails, the handler swallows it, the run still looks fine | Code — done, below |
| B | Three consecutive errors, Make deactivates the scenario | Configuration, and who owns the account |

## A. Alerts on swallowed failures — implemented

An error handler in Make can run modules of its own before the `Resume` or
`Ignore` directive. Each handler now sends an email to `support@buildregs.co.uk`
before letting the run continue.

These modules only execute when something fails, so they cost nothing on a normal
run.

### Phase 1 (7129360)

| Failing step | Subject | What the email says |
| --- | --- | --- |
| 3b data store write | `BuildRegs automation - folder not recorded` | Enquiry is fine; the folder link may be wrong if this client later pays. No action now. |
| 6 CRM write | `ACTION NEEDED - enquiry not saved to CRM` | Carries every field needed to add the contact by hand. |
| 4 file download | `ACTION NEEDED - client file missing` | Names the file, links it, and says to save it to the folder or ask the client to resend. |
| 5 Drive upload | `ACTION NEEDED - client file not saved to Drive` | Same, and notes that repeats usually mean the Drive connection needs reconnecting. |

### Phase 3 (7248863)

| Failing step | Subject | What the email says |
| --- | --- | --- |
| 5 CRM update | `ACTION NEEDED - payment received, CRM not updated` | States plainly that the money is safe and only the CRM record failed, with the amount, Stripe reference and instructions to set Quote Status to Paid by hand. |

Each alert states what still worked, so the reader is not left guessing whether a
customer was served. The file alerts sit inside the iterator, so a submission with
three bad files produces three emails — one per lost file, which is the right
granularity for acting on them.

### Tested before deployment

A harness was built with a deliberately failing HTTP module whose error handler
wrote a marker record to the data store, then sent an alert, then resumed. The
alert was addressed to the freelancer's own inbox rather than the client's, so
the mechanism could be proven without confusing the client.

Execution `d887fe2666a64fd69462a7b00fcba5f6`, status SUCCESS. The marker record
appeared in the store:

```
key: ZZ-ALERT-TEST
  folderUrl  : handler-branch-executed
  projectRef : BR-ALERTTEST-054631
  createdAt  : 2026-09-28 05:46:32
```

That proves the handler branch ran its extra modules and that the scenario still
completed afterwards rather than failing. The marker was deleted after the test.

## B. Scenario deactivation — not code

`maxErrors` is 3 on both scenarios. After three consecutive errors Make
deactivates the scenario and emails the account owner.

That email currently goes to the freelancer's address, not the client's, because
the Make account is the freelancer's. The API exposes no notification settings,
so this cannot be verified or changed from here — it is part of the account
handover, not something to build.

Until the account is in the client's name, the client will not receive this
notification. Worth being explicit about that with them rather than implying the
alerting is complete.

Note that the alerts in part A make deactivation much less likely to arrive
unannounced: the individual failures that would accumulate towards three
consecutive errors now each send an email of their own.

## Not done, and why

- **A watchdog scenario** that checks the others are alive. This is the obvious
  design and it is blocked: the Free plan allows two active scenarios and the
  system already needs three. It becomes available on a paid plan.
- **Enabling the dead letter queue** (`dlq` is false). It would retain failed
  executions for retry rather than losing them, and the Free plan allows 1 MB of
  it. Left alone deliberately: it changes how errors behave, and changing it in
  the same pass as the alerts would make any resulting problem hard to attribute.
  Worth doing on its own afterwards.
