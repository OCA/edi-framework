/** @odoo-module **/

import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

const {Component} = owl;

export class EdiConfigurationWidget extends Component {
    async setup() {
        super.setup();
        this.orm = useService("orm");
        this.action = useService("action");
    }
    async onClick(ev, rule) {
        ev.preventDefault();
        ev.stopPropagation();
        var typeId = rule.type.id;
        const action = await this.orm.call(
            this.props.record.resModel,
            "edi_create_exchange_record",
            [[this.props.record.resId], typeId],
            {context: this.props.record.context}
        );
        this.action.doAction(action);
    }
}

EdiConfigurationWidget.template = "edi_oca.EdiConfigurationWidget";

registry.category("fields").add("edi_configuration", EdiConfigurationWidget);
