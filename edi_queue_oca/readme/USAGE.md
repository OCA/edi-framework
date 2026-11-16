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
| **Job description pattern** | Description of the queue jobs of the exchange records (see below). |
| **Enable ETA Scheduling** | Toggle to activate daily job accumulation (see below). |
| **Execution time** | Hour, minute, and timezone at which accumulated jobs are released. Visible only when ETA Scheduling is enabled. |

## Job description

By default, a queue job is described by the docstring of the delayed method.
Set a **Job description pattern** on the exchange type to give the jobs of its
exchange records a meaningful description, e.g.:

    Process WMS inventory report exchange {identifier}

The pattern uses Python `str.format` syntax with named placeholders only:

- `{identifier}`: identifier of the exchange record;
- `{external_identifier}`: external identifier of the exchange record;
- `{type}`: name of the exchange type;
- `{type_code}`: code of the exchange type;
- `{backend}`: name of the backend;
- `{record}`: name of the related record.

Missing values are rendered as empty strings. Attribute or index access
(e.g. `{identifier.__class__}`), positional fields and unknown placeholders are
rejected when saving the exchange type.

The description applies to all the jobs of the exchange record (generate, send,
receive, process). A description returned by an override of the
`action_exchange_<action>_job_options` methods takes precedence. Developers can
add placeholders by extending `_job_description_placeholders` and
`_job_description_values` on `edi.exchange.record`.

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
