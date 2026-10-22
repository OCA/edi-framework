import logging

from odoo import Command, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class EDIInputProcessDiaparDespatchAdvice(models.AbstractModel):
    """
    INPUT PROCESSOR BLE
    """

    _name = "input.process.diapar.despatch.advice"
    _inherit = ["edi.oca.handler.process"]
    _description = "Input process despatch advice from Diapar"

    def process(self, exchange_record):
        _logger.info(">>>>>>>>>>>>>>>>>> Reading BLE file >>>>>>>>>>>>>>>>>>>>>")
        picking_update, purchase_order = self._handle_create_picking_update(
            exchange_record
        )
        if picking_update:
            picking_update.button_update_picking_order()
            if not exchange_record.related_record_ids.filtered(
                lambda r: r.model == "purchase.order" and r.res_id == purchase_order.id
            ):
                self.env["edi.exchange.related.record"].create(
                    {
                        "exchange_record_id": exchange_record.id,
                        "res_id": purchase_order.id,
                        "model": "purchase.order",
                    }
                )
            return self.env._(
                "Stock Picking %s updated. Related Order: %s",
                picking_update.name.name,
                purchase_order.name,
            )
        return self.env._("No picking update created for this file.")

    def _parse_file_content_ble(self, exchange_record):
        datas = exchange_record._get_file_content()
        return datas.split("\n")

    def _get_mapping_field_position(self, exchange_type, field_name):
        mapping = exchange_type.field_mapping_ids.filtered(
            lambda rec: rec.mapping_field_id.name == field_name
        )
        pos_from = mapping.sequence_start
        pos_to = mapping.sequence_end
        return pos_from, pos_to

    def _get_picking_order_and_supplier_info(
        self, line, edi_exchange_type, picking_order, supplier_info, delivery_date
    ):
        pos_from, pos_to = self._get_mapping_field_position(
            edi_exchange_type, "product_code"
        )
        product_code = line[pos_from:pos_to]
        purchase_order = self.env["purchase.order"]
        supplier_info = self.env["product.supplierinfo"].search(
            [("product_code", "=", product_code)],
            limit=1,
        )
        supplier_ids = supplier_info.mapped("partner_id").ids
        # Look for corresponding purchase order, normally it
        # should be just one even if there is more than one
        # supplier associated to product
        if supplier_ids:
            sdate = f"{delivery_date} 00:00:00"
            edate = f"{delivery_date} 23:59:59"
            purchase_order = self.env["purchase.order"].search(
                [
                    ("partner_id", "in", supplier_ids),
                    ("state", "in", ["purchase", "done"]),
                    ("date_planned", ">=", sdate),
                    ("date_planned", "<=", edate),
                ],
                limit=1,
            )
            # Assuming purchase order has only one picking order associated.
            if purchase_order.exists():
                picking_order = purchase_order.picking_ids[0]
        return picking_order, supplier_info, purchase_order

    def _get_updated_quantity_values(
        self, line, edi_exchange_type, picking_order, supplier_info
    ):
        # Look for updated quantity
        pos_from, pos_to = self._get_mapping_field_position(
            edi_exchange_type, "product_qty"
        )
        new_quantity = line[pos_from:pos_to]
        # Look for ordered quantity
        product_tmpl = self.env["product.template"]
        if supplier_info:
            product_tmpl = supplier_info[0].product_tmpl_id
        ordered_product = self.env["product.product"].search(
            [("product_tmpl_id", "=", product_tmpl.id)],
            limit=1,
        )
        ordered_operation = self.env["stock.move"].search(
            [
                ("picking_id", "=", picking_order.id),
                ("product_id", "=", ordered_product.id),
            ]
        )
        ordered_quantity = ordered_operation.quantity
        # Construct one2many values
        vals = dict()
        if ordered_quantity != float(new_quantity):
            vals.update(
                {
                    "line_to_update_id": ordered_operation.id,
                    "product_id": ordered_product.id,
                    "ordered_quantity": ordered_quantity,
                    "product_qty": float(new_quantity),
                }
            )
        return vals

    def _reprepare_delivery_date(self, line, edi_exchange_type):
        pos_from, pos_to = self._get_mapping_field_position(
            edi_exchange_type, "date_planned"
        )
        data = line[pos_from:pos_to]
        return self.env["edi.configuration"].get_date_format_ble_yyyymmdd(data)

    def _prepare_picking_update_values(self, exchange_record):
        lines = self._parse_file_content_ble(exchange_record)
        edi_exchange_type = exchange_record.type_id

        if not lines:
            raise ValidationError(
                self.env._(
                    "Please configure fields mapping for BLE interface on your"
                    " EDI system!"
                )
            )

        delivery_date = delivery_sign = ""
        picking_order = self.env["stock.picking"]
        supplier_info = self.env["product.supplierinfo"]
        purchase_order = self.env["purchase.order"]
        proposition_vals = dict()
        values_list = []
        for line in lines:
            if not line or not isinstance(line, str):
                continue
            # This condition ensures that this job
            # consider only one picking per EDI File
            line = line.lstrip()
            if line.startswith(edi_exchange_type.header_code) and not delivery_date:
                # Header processing
                delivery_date = self._reprepare_delivery_date(line, edi_exchange_type)
            elif line.startswith(edi_exchange_type.lines_code):
                # Look if it's a first delivery
                delivery_sign = edi_exchange_type.delivery_sign
                if delivery_sign == "-":
                    break

                # Look for picking_order, supplier_info
                picking_order, supplier_info, purchase_order = (
                    self._get_picking_order_and_supplier_info(
                        line,
                        edi_exchange_type,
                        picking_order,
                        supplier_info,
                        delivery_date,
                    )
                )
                # Look for updated quantity
                updated_values = self._get_updated_quantity_values(
                    line, edi_exchange_type, picking_order, supplier_info
                )
                if updated_values:
                    values_list += [Command.create(updated_values)]
        if delivery_sign == "+":
            proposition_vals.update(
                {
                    "name": picking_order.id,
                    "values_proposed_ids": values_list,
                }
            )
        return proposition_vals, purchase_order

    def _handle_create_picking_update(self, exchange_record):
        picking_update = self.env["picking.update"]
        proposition_vals, purchase_order = self._prepare_picking_update_values(
            exchange_record
        )
        if proposition_vals:
            picking_update = picking_update.create(proposition_vals)
        return picking_update, purchase_order
