Adds a "Manage File" button on EDI exchange records that contain a file and are in
an error state (`output_sent_and_error` or `input_processed_error`).

The button opens a wizard that lets the user either replace the exchange file with
a new one, or edit its content directly (with a code editor). At the end the user
can safely close the wizard.
