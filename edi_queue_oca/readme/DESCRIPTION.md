This module integrates EDI exchange records with
[Queue Job](https://github.com/OCA/queue), so that the four core exchange
actions — **generate**, **send**, **receive**, and **process** — are dispatched
as background jobs instead of running synchronously.

Each exchange type can optionally route its jobs to a specific channel, set a
priority, or **hold all jobs until a fixed time of day** — useful when a
trading partner's receiving system has a nightly processing window or when the
operator wants to concentrate resource-intensive EDI work in off-peak hours.
