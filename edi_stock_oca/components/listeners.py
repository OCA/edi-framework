from odoo.addons.component.core import Component


class EDIConfigSPListener(Component):
    _name = "edi.listener.config.stock.picking"
    _inherit = "base.event.listener"
    _apply_on = ["stock.picking"]

    def on_record_create(self, record, fields=None):
        trigger = "on_record_create"
        return self._exec_conf(record, trigger)

    def on_record_write(self, record, fields=None):
        trigger = "on_record_write"
        return self._exec_conf(record, trigger)

    def on_edi_stock_picking_state_change(self, record, state=None):
        trigger = "on_edi_stock_picking_state_change"
        return self._exec_conf(record, trigger)

    def _exec_conf(self, record, trigger, conf_field="edi_stock_picking_conf_ids"):
        confs = record.partner_id[conf_field].edi_get_conf(trigger)
        for conf in confs:
            conf.edi_exec_snippet_do(record)
