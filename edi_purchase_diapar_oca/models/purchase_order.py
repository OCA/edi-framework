from odoo import models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _edi_config_field_relation(self):
        return self.partner_id.edi_purchase_conf_ids

    def _should_apply_receipt_qty_policy(self):
        """Condition to apply the policy of using the quantity from
        the EDI file instead of the one in the order line."""
        self.ensure_one()
        exchange_types = self.env["edi.exchange.type"].search(
            [
                ("partner_ids", "in", self.partner_id.ids),
                ("direction", "=", "input"),
            ]
        )
        return (
            not self.edi_disable_auto
            and self.partner_id.is_edi
            and self.partner_id.edi_purchase_conf_ids
            and exchange_types
        )

    def _consolidate_product_qty(self, order_line):
        return order_line.product_qty

    def _consolidate_products(self):
        self.ensure_one()
        if not self.order_line:
            raise ValidationError(
                self.env._("No lines in this order %s!", self.name)
            ) from None
        lines = {}
        for line in self.order_line:
            quantity = self._consolidate_product_qty(line)
            if line.product_id in lines:
                if line.taxes_id != lines[line.product_id]["taxes_id"]:
                    raise ValidationError(
                        self.env._(
                            "Check taxes for lines with product %s!",
                            line.product_id.name,
                        )
                    )
                if line.price_unit != lines[line.product_id]["price_unit"]:
                    raise ValidationError(
                        self.env._(
                            "Check price for lines with product %s!",
                            line.product_id.name,
                        )
                    )
                lines[line.product_id]["quantity"] += quantity
            else:
                code, origin_code = line.product_id._get_supplier_code_or_ean(
                    line.partner_id.id
                )
                values = {
                    "code": code,
                    "origin_code": origin_code,
                    "quantity": quantity,
                    "price_unit": line.price_unit,
                    "taxes_id": line.taxes_id,
                }
                lines.update({line.product_id: values})
        return lines

    def generate_template_output_diapar(self, output_template, exchange_record):
        self.ensure_one()
        return output_template.exchange_generate(
            exchange_record,
            order_lines=self._consolidate_products(),
            env=self.env,
        )


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _create_stock_moves(self, picking):
        if self.order_id._should_apply_receipt_qty_policy():
            if self.company_id.edi_receipt_qty_policy == "received_file":
                self = self.with_context(qty_from_file_policy=True)
        return super()._create_stock_moves(picking)
