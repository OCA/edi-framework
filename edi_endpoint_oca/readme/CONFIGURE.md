Go to "EDI -\> Config -\> Endpoints".

## Exec modes

Each endpoint must pick an "Exec mode" that decides how the incoming
request is turned into work for the EDI framework:

- **Create exchange record** (default): persists the raw HTTP body as a
  new exchange record on the configured backend / exchange type and
  returns `{"status": "queued", "id": <identifier>}` with HTTP 200. Use
  this for "receive and queue" endpoints — no per-endpoint code snippet
  is required, and request validation (e.g. JSON Schema) is handled by
  the endpoint mixin before the handler runs.
- **Execute code**: runs the user-provided code snippet, giving full
  control over how the request is processed and what is returned.
