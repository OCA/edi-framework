# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.edi_component_oca.tests.common import EDIBackendCommonComponentTestCase


class PartyDataCommonTestCase(EDIBackendCommonComponentTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = cls.env.ref("edi_core_oca.demo_edi_backend")
        cls.cat_model = cls.env["res.partner.id_category"]
        cls.all_cat = cls.cat_model.browse()
        for i in range(1, 4):
            rec = cls.cat_model.create({"code": f"cat{i}", "name": f"Cat {i}"})
            cls.all_cat += rec
            setattr(cls, f"category{i}", rec)

        parent = cls.env["res.partner"].create(
            {
                "name": "ACME inc",
                "is_company": True,
            }
        )

        for i in range(1, 4):
            rec = cls.env["res.partner"].create(
                {
                    "name": f"Test Partner {i}",
                    "parent_id": parent.id,
                    "id_numbers": [
                        (
                            0,
                            0,
                            {
                                "name": f"{cat.code}-p{i}",
                                "category_id": cat.id,
                            },
                        )
                        for cat in cls.all_cat[i - 1 :]
                    ],
                }
            )
            setattr(cls, f"partner{i}", rec)

        # No need for special file name gen
        cls.exc_type = cls._create_exchange_type(
            name="ID output test",
            code="id_out_test",
            direction="output",
        )
        cls.exc_record = cls.backend.create_record("id_out_test", {})

    def _expected_lang(self, partner):
        if not partner.lang:
            return False
        lang = self.env["res.lang"]._get_data(code=partner.lang)
        if not lang:
            return False
        return {"name": lang.name, "code": lang.code, "short": lang.code.split("_")[0]}

    def _make_expected_data(
        self, partner, number, allowed_codes=None, name_field="name", **kw
    ):
        data = {
            "name": partner[name_field],
            "identifiers": [
                {"attrs": {"schemeID": "cat1"}, "value": f"cat1-p{number}"},
                {"attrs": {"schemeID": "cat2"}, "value": f"cat2-p{number}"},
                {"attrs": {"schemeID": "cat3"}, "value": f"cat3-p{number}"},
            ],
            "endpoint": {},
            "lang": self._expected_lang(partner),
            "partner": partner,
        }
        data.update(kw)
        if allowed_codes:
            data["identifiers"] = [
                x
                for x in data["identifiers"]
                if x["attrs"]["schemeID"] in allowed_codes
            ]
        return data
