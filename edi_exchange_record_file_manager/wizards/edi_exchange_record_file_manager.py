# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json
import os
from itertools import product

from lxml import etree

from odoo import api, fields, models
from odoo.exceptions import UserError


class EDIExchangeRecordFileManager(models.TransientModel):
    _name = "edi.exchange.record.file.manager"
    _description = "EDI Exchange Record File Manager"

    # Exchange record data
    exchange_record_id = fields.Many2one(
        "edi.exchange.record",
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    exchange_record_file = fields.Binary(
        related="exchange_record_id.exchange_file",
        readonly=True,
        attachment=False,
    )
    exchange_record_filename = fields.Char(
        related="exchange_record_id.exchange_filename",
        readonly=True,
    )
    exchange_record_retryable = fields.Boolean(
        related="exchange_record_id.retryable",
        readonly=True,
    )

    # Wizard setup
    state = fields.Selection(
        selection=[
            ("setup", "Setup"),
            ("replace", "Replace file"),
            ("edit", "Edit file"),
            ("done", "Done"),
        ],
        default="setup",
        required=True,
        readonly=True,
    )
    mode = fields.Selection(selection=lambda self: self._get_mode_selection())

    # ``mode == "replace"``
    new_file = fields.Binary(attachment=False)
    new_filename = fields.Char()

    # ``mode == "edit"``
    file_content = fields.Text()
    ace_mode = fields.Selection(
        selection=lambda self: self._get_ace_mode_selection(),
        default=lambda self: self._get_ace_mode_default(),
    )

    # UI
    button_proceed_invisible = fields.Boolean(
        compute="_compute_button_proceed_invisible"
    )
    button_retry_invisible = fields.Boolean(compute="_compute_button_retry_invisible")
    button_cancel_invisible = fields.Boolean(compute="_compute_button_cancel_invisible")
    button_close_invisible = fields.Boolean(compute="_compute_button_close_invisible")

    # ------------------------------------------------------------------
    # Model setup and view updates
    # ------------------------------------------------------------------

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        # OVERRIDE: create N copies of the ``<field name="file_content"/>`` node in
        # the form view, one for each ``ace_mode`` selection value
        # NB: we override ``_get_view()`` instead of ``get_view()`` for 2 main reasons:
        #   1- its result is passed to ``_get_view_cache()``: no need to reapply the
        #      modifications everytime the user opens a new wizard
        #   2- ``_get_view_cache()`` takes care of calling ``_get_view_postprocessed()``
        #      and ``_get_view_fields()`` after ``_get_view()`` is called, allowing the
        #      returned object to contain already all the info about the model and its
        #      fields that the webclient needs to properly render the form view; if we
        #      had overridden ``get_view()`` instead we would've needed to do it by
        #      ourselves manually
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "form":
            arch = self._add_file_content_fields(arch)
        return arch, view

    @api.model
    def _add_file_content_fields(self, arch: etree._Element) -> etree._Element:
        """Parses ``arch`` to add ``file_content`` field nodes"""
        nodes = arch.xpath("//div[@name='state_edit']")
        ace_modes = [m for m, s in self._get_ace_mode_selection()]
        base_attrib = {"name": "file_content", "nolabel": "1", "widget": "ace"}
        for node, mode in product(nodes, ace_modes):
            options = {}
            if mode != "txt":
                options = {"mode": mode}
            node.append(
                etree.Element(
                    "field",
                    attrib=dict(
                        base_attrib,
                        invisible=f"ace_mode != '{mode}'",
                        options=str(options),
                    ),
                )
            )
        return arch

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def open(self):
        """Opens the wizard in a dialog"""
        return {
            "type": "ir.actions.act_window",
            "name": self._description,
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
            "context": dict(self.env.context or {}, dialog_size="extra-large"),
        }

    def _read_record_file_content(
        self, binary=True, as_bytes=False, raise_exc: bool = True
    ) -> str | bytes:
        """Wrapper around the EDI exchange record's ``_get_file_content()`` method

        Params ``binary`` and ``as_bytes`` are passed down to the EDI exchange record's
        ``_get_file_content()`` method.
        If ``raise_exc`` is True and an error occurs while reading the EDI exchange
        record's file, the error is raised; else, an empty ``str`` or ``bytes`` object
        is returned.
        """
        record = self.exchange_record_id
        try:
            return record._get_file_content(binary=binary, as_bytes=as_bytes)
        except Exception as exc:
            if raise_exc:
                raise UserError(self.env._("The file cannot be read")) from exc
            return b"" if as_bytes else ""

    # ------------------------------------------------------------------
    # Ace mode tools and file content management
    # ------------------------------------------------------------------

    @api.model
    def _get_ace_mode_selection(self) -> list[tuple[str, str]]:
        """Returns field ``ace_mode`` selection

        The returned selection might be incomplete, can be extended by inheriting
        modules
        """
        return [
            # These values are defined here:
            # https://github.com/odoo/odoo/blob/625eb316/addons/web/static/src/core/code_editor/code_editor.js#L65
            ("javascript", "JavaScript/JSON"),
            ("xml", "XML/HTML"),
            ("qweb", "QWeb"),
            ("scss", "SCSS"),
            ("python", "Python"),
            ("txt", self.env._("Plain text")),
        ]

    @api.model
    def _get_ace_mode_default(self) -> str:
        """Returns the default value for ``ace_mode``"""
        return "txt"

    @api.model
    def _get_extension_to_ace_mode_map(self) -> dict[str, str]:
        """Return a mapping of file extensions to ace modes

        The returned mapping is incomplete, can be extended by inheriting modules
        """
        return {
            # file extension -> ace mode
            "py": "python",
            "pyc": "python",
            "pyi": "python",
            "pyx": "python",
            "json": "javascript",
            "js": "javascript",
            "xml": "xml",
            "xsd": "xml",
            "xsl": "xml",
            "xslt": "xml",
            "xhtml": "xml",
            "html": "xml",
            "htm": "xml",
            "css": "scss",
            "scss": "scss",
        }

    def _guess_ace_mode(self) -> str:
        """Return the ace mode (one of `ace_mode` values) best fitting the file

        First, we try to retrieve the extension from the original EDI Exchange Record
        filename or its EDI Exchange Type, and map it to the proper ace mode.
        If no match is found, we guess by looking at EDI Exchange Record content.
        """
        self.ensure_one()
        # Try guessing from the Exc Rec filename extension or its Exc Type extension
        exc_rec = self.exchange_record_id
        exc_type = exc_rec.type_id
        ext2am_map = self._get_extension_to_ace_mode_map()
        for ext in (
            os.path.splitext(exc_rec.exchange_filename or "")[1],
            exc_type.exchange_file_ext or "",
        ):
            if mode := ext2am_map.get(ext.lstrip(".").lower()):
                return mode
        # Unknown extension: guess by looking at the Exc Rec file content
        content = self._read_record_file_content()
        if first_char := content.lstrip()[:1]:
            if first_char == "<":
                return "xml"
            elif first_char in ("{", "["):
                try:
                    json.loads(content)
                    return "javascript"
                except ValueError:
                    return "txt"
        return "txt"

    # ------------------------------------------------------------------
    # Modes
    # ------------------------------------------------------------------

    @api.model
    def _get_mode_selection(self) -> list[tuple[str, str]]:
        return [
            ("replace", self.env._("Replace file")),
            ("edit", self.env._("Edit file")),
        ]

    # ------------------------------------------------------------------
    # States
    # ------------------------------------------------------------------

    def button_proceed(self):
        """Proceeds to the next state"""
        self.ensure_one()
        if self.state == "done":
            raise UserError(self.env._("Nothing left to do, please close the dialog."))
        getattr(self, f"_proceed_from_{self.state}")()
        return self.open()

    def _proceed_from_setup(self):
        """Proceeds from ``setup`` to the next state"""
        if not self.mode:
            raise UserError(self.env._("Please select an option to proceed."))
        self.exchange_record_id._check_can_use_file_manager()
        if self.mode == "replace":
            self.state = "replace"
        else:
            self.write(
                {
                    "state": "edit",
                    "file_content": self._read_record_file_content(),
                    "ace_mode": self._guess_ace_mode(),
                }
            )

    def _proceed_from_replace(self):
        """Proceeds from ``replace`` to the next state"""
        if not self.new_file:
            raise UserError(self.env._("Please upload the new file."))
        record = self.exchange_record_id
        record._check_can_use_file_manager()
        # The filename of the exchange record is intentionally left untouched
        record.exchange_file = self.new_file
        record.message_post(body=self.env._("File replaced through file manager."))
        self.state = "done"

    def _proceed_from_edit(self):
        """Proceeds from ``edit`` to the next state"""
        record = self.exchange_record_id
        record._check_can_use_file_manager()
        encoding = record.type_id.encoding or "UTF-8"
        try:
            record._set_file_content(self.file_content, encoding=encoding)
        except (UnicodeError, LookupError) as exc:
            raise UserError(
                self.env._(
                    "The content cannot be encoded with the exchange type "
                    "encoding (%(encoding)s): %(error)s",
                    encoding=encoding,
                    error=exc,
                )
            ) from exc
        record.message_post(body=self.env._("File edited through file manager."))
        self.state = "done"

    # ------------------------------------------------------------------
    # Other buttons and UI stuff
    # ------------------------------------------------------------------

    def button_retry(self):
        """Calls the "Retry" button on the Exc Rec and refreshes the page"""
        self.ensure_one()
        if self.state != "done":
            raise UserError(
                self.env._("The exchange can be retried only after the file update.")
            )
        self.exchange_record_id.action_retry()
        return {"type": "ir.actions.client", "tag": "soft_reload"}

    @api.depends("state", "mode")
    def _compute_button_proceed_invisible(self):
        """Computes whether the "Proceed" button is invisible"""
        for wiz in self:
            wiz.button_proceed_invisible = wiz.state == "done" or (
                wiz.state == "setup" and not wiz.mode
            )

    @api.depends("state", "exchange_record_retryable")
    def _compute_button_retry_invisible(self):
        """Computes whether the "Retry" button is invisible"""
        for wiz in self:
            wiz.button_retry_invisible = (
                wiz.state != "done" or not wiz.exchange_record_retryable
            )

    @api.depends("state")
    def _compute_button_cancel_invisible(self):
        """Computes whether the "Cancel" button is invisible"""
        for wiz in self:
            wiz.button_cancel_invisible = wiz.state == "done"

    @api.depends("state")
    def _compute_button_close_invisible(self):
        """Computes whether the "Close" button is invisible"""
        for wiz in self:
            wiz.button_close_invisible = wiz.state != "done"
