## ID numbers selection

See `edi_party_helper_oca`'s configuration.

## Name field

On the exchange type form, modify the advanced settings so that the work
context of the component that is used (eg: generate) contains
party_data_name_field. For instance:

    components:
        generate:
            usage: my.generate
            work_ctx:
                party_data_name_field: name
