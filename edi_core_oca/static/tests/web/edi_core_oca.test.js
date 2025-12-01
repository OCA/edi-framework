/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
import {defineMailModels, startServer} from "@mail/../tests/mail_test_helpers";
import {defineModels, fields, models, mountView} from "@web/../tests/web_test_helpers";
import {expect, test} from "@odoo/hoot";
import {click} from "@odoo/hoot-dom";
class Partner extends models.Model {
    _name = "partner";
    name = fields.Char({});
    edi_config = fields.Json({default: {}});

    edi_create_exchange_record(exchange_type_id) {
        expect.step("EDI Launched for " + exchange_type_id);
        return {type: "ir.actions.act_window_close"};
    }
}

defineMailModels();
defineModels([Partner]);

test("EDI OCA Test widget", async () => {
    const pyEnv = await startServer();
    const partner = pyEnv.partner.create({
        name: "Awesome partner",
        edi_config: {
            1: {
                form: {btn: {label: "EDI Task 01", tooltip: "EDI Task Tooltip"}},
                type: {
                    id: 1,
                    name: "EDI Type 01",
                },
            },
            2: {
                form: {btn: {label: "EDI Task 02", tooltip: "EDI Task Tooltip"}},
                type: {
                    id: 2,
                    name: "EDI Type 02",
                },
            },
            3: {
                form: {},
                type: {
                    id: 1,
                    name: "EDI Type 03",
                },
            },
        },
    });
    await mountView({
        type: "form",
        resId: partner,
        resIds: [partner],
        resModel: "partner",
        arch: `<form>
                <div
                    class="alert alert-warning"
                    role="alert"
                    style="margin-bottom:0px;"
                >
                    <div>
                        <span class="pe-4"><i class="fa fa-retweet" /> EDI actions</span>
                        <field name="edi_config" widget="edi_configuration" />
                    </div>
                </div>
                <sheet />
            </form>`,
    });
    expect(".o_field_edi_configuration").toHaveCount(1);
    expect(".o_field_edi_configuration .o_edi_action").toHaveCount(2);
    // The one without form, shouldn't be shown
    await click(".o_field_edi_configuration .o_edi_action");
    await expect.waitForSteps(["EDI Launched for 1"]);
    expect.assertions(3);
});
