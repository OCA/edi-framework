## Component definition

The component used on edi must inherit from:

- `edi.component.input.mixin` for processing and implement the process function
- `edi.component.receive.mixin` for reception and implement the receive function
- `edi.component.output.mixin` for generation and implement the generate function
- `edi.component.send.mixin` for sending and implement the send function
- `edi.component.check.mixin` for checking and implement the check function
- `edi.component.validate.mixin` for validation and implement the validate function

Also, the components may have the following elements that will be used to use the right component:

- `_backend_type`: code of the backend type
- `_exchange_type`: code of the exchange type
- `_usage`: Automatically set by the inherited component
