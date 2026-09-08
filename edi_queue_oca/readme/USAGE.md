## Automatic job dispatch

All exchange actions on `edi.exchange.record` are dispatched as background
jobs automatically. No per-record configuration is required; the integration
is active for every exchange type as soon as the module is installed.

## Per-type job configuration

Each **Exchange Type** gains a *Queue* tab with optional settings:

| Field | Purpose |
|---|---|
| **Job channel** | Route jobs to a specific channel (e.g. `root.edi.high`). |
| **Job priority** | Integer priority passed to the queue job (lower = higher priority). |
| **Enable ETA Scheduling** | Toggle to activate daily job accumulation (see below). |
| **Execution time** | Hour, minute, and timezone at which accumulated jobs are released. Visible only when ETA Scheduling is enabled. |

## Accumulating jobs until a fixed daily time

Enabling **ETA Scheduling** on an exchange type causes every job created for
that type to be **held in the queue** until the configured time of day, rather
than being processed immediately. All jobs that arrive during the day
accumulate and are released together at that moment.

**Typical use cases:**

- A trading partner's receiving system only processes incoming files at a
  specific nightly window (e.g. 22:00).
- Resource-intensive EDI operations (large exports, heavy transformations)
  should be deferred to off-peak hours to avoid competing with daytime
  workloads.
- Operational preference to send a batch of documents at a predictable daily
  time instead of dispatching them one by one in real time.

The execution time is configured with three fields:

- **Hour** — hour of the day (00–23).
- **Minute** — minute of the hour (00–59).
- **Timezone** — the timezone in which the hour and minute are interpreted.
  Defaults to the current user's timezone.

At runtime the configured time is converted to the next matching UTC datetime
and set as the queue job ETA. If the target time for today has already passed,
the job is automatically scheduled for the same time tomorrow.

When **Enable ETA Scheduling** is off, jobs are dispatched immediately as
usual.

## Duplicate-job prevention

An identity key is attached to every queued job, so re-triggering an action
for a record that already has a pending job does not enqueue a duplicate.

## Garbage collection of stranded jobs

`queue_job` cancels dependent jobs only when a parent is explicitly cancelled,
so a dependent of a *failed* parent stays in *Wait Dependencies* forever. The
cron *EDI exchange garbage collect stale jobs* cancels those jobs once no
parent can still bring them to execution, and only after a grace period (24
hours by default, set by the system parameter
`edi_queue_oca.gc_stale_jobs_grace_hours`) that leaves time to requeue the
failed parent by hand. The cron is disabled by default.
