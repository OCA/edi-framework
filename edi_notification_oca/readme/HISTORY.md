## 18.0.2.0.0

### Features

- Notifications are configured by **notification rules** on the exchange
  type (`edi.notification.rule`). A rule reacts to exchange statuses, and
  either posts the status note on the related records or schedules
  activities for users and groups.
- Every exchange type gets a default *Notes on related records* rule with
  every non-error status, matching the behaviour without this module.
  Error notes are always posted. Exchange types created with the
  `edi_notification_skip_default_rule` context key get no default rule.

### Breaking changes

- The *Notify On Process Error* fields of the exchange type and the
  `edi.notification.component.listener` component are removed. The migration creates the default rule
  of every exchange type, and replaces each configured process error
  notification with an activity rule on the same error statuses, with the
  same activity type, groups and users.
