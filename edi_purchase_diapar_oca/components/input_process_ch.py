import datetime
import logging

from odoo import models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class EDIInputProcessDiaparPurchasePrice(models.AbstractModel):
    """
    INPUT PROCESSOR CH
    """

    _name = "input.process.diapar.purchase.price"
    _inherit = ["edi.oca.handler.process"]
    _description = "Input process purchase price from Diapar"

    def process(self, exchange_record):
        _logger.info(">>>>>>>>>>>>>>>>>> Reading CH file >>>>>>>>>>>>>>>>>>>>>")
        SupplierPriceList = self.env["supplier.price.list"]

        self.create_supplier_price_list(exchange_record)
        args = [
            ("product_tmpl_id", "!=", False),
            ("price_updated", "=", False),
            ("supplier_id", "!=", False),
        ]
        recs = self.env["supplier.price.list"].search(args)
        products = recs.mapped("product_tmpl_id")
        for product in products:
            splists = recs.filtered(
                lambda rec, product=product: rec.product_tmpl_id == product
            )
            try:
                SupplierPriceList.update_product_price_list(product, splists)
            except Exception as e:
                _logger.error(
                    "Could not update price list for the product %s: %s",
                    product,
                    str(e),
                )

        return self.env._("Process update purchase price from Diapar done!")

    def _parse_file_content_ch(self, exchange_record):
        datas = exchange_record._get_file_content()
        return datas.split("\n")

    def _get_mapping_field_position(self, exchange_type, field_name):
        mapping = exchange_type.field_mapping_ids.filtered(
            lambda rec: rec.mapping_field_id.name == field_name
        )
        pos_from = mapping.sequence_start
        pos_to = mapping.sequence_end
        return pos_from, pos_to

    def _prepare_supplier_price_list_values(self, exchange_record):
        lines = self._parse_file_content_ch(exchange_record)
        if not lines:
            raise ValidationError(
                self.env._(
                    "Please configure fields mapping for prices interface on your \
                EDI Exchange Type!"
                )
            )

        edi_exchange_type = exchange_record.type_id

        EDIConfig = self.env["edi.configuration"]
        ProductSupplierInfo = self.env["product.supplierinfo"]

        prices = []
        product_codes = []
        today = datetime.date.today()
        for line in lines:
            if not line or not isinstance(line, str):
                continue
            line = line.lstrip()
            # check if this line is already imported.
            pos_from, pos_to = self._get_mapping_field_position(
                edi_exchange_type, "supplier_code"
            )
            product_code = line[pos_from:pos_to]
            if product_code in product_codes:
                continue
            else:
                product_codes.append(product_code)
            key = ["supplier_id", "import_date"]
            value = [edi_exchange_type.partner_ids.ids[0], today]
            for mapping in edi_exchange_type.field_mapping_ids:
                slice_from = mapping.sequence_start
                slice_to = mapping.sequence_end
                # construct dictionary
                key.append(mapping.mapping_field_id.name)
                data = line[slice_from:slice_to]
                # Product test
                if mapping.mapping_field_id.name == "supplier_code":
                    # appending supplier_code data
                    value.append(data)
                    # appending product_id data
                    supp_info = ProductSupplierInfo.search(
                        [("product_code", "=", data)], limit=1
                    )
                    product_id = supp_info.product_tmpl_id.id
                    key.append("product_tmpl_id")
                    value.append(product_id)
                # Date test
                elif mapping.is_date:
                    # slice dates
                    apply_date = EDIConfig.get_date_format_yyyymmdd(data)
                    value.append(apply_date)
                # numeric test
                elif mapping.is_numeric:
                    decimal_precision = mapping.decimal_precision
                    price = EDIConfig.insert_separator(data, -decimal_precision, ".")
                    value.append(float(price))
                elif mapping.mapping_field_id.name == "product_name":
                    value.append(data)
            prices_dict = {k: v for k, v in zip(key, value, strict=False)}
            prices.append(prices_dict)
        return prices

    def create_supplier_price_list(self, exchange_record):
        prices = self._prepare_supplier_price_list_values(exchange_record)
        return self.env["supplier.price.list"].create(prices)
