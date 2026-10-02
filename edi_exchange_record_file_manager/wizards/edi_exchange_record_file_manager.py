# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import base64
import binascii
import collections
import json
import os

from odoo import api, fields, models
from odoo.exceptions import UserError


class EDIExchangeRecordFileManager(models.TransientModel):
    """A wizard to manage the file of an EDI Exchange Record.

    Consists of 3 steps:
        1)   setup: the user can choose whether they want to edit the file in-place, or
             download it and replace it with a new file
        2.a) edit: if the user selected the "Edit" option during the setup, 2 fields are
             displayed:
                * a text field containing the file content that the user can modify
                * a selection field that changes how the file content is rendered
                  (as a Python text, XML text, etc.);
             once the user clicks on the "Proceed" button, the new file content will be
             overwritten into the existing file
        2.b) replace: if the user selected the "Replace" option during the setup, they
             will be allowed to download the current file, and they will need to add a
             new file before proceeding (else, an error is raised); once the user clicks
             on the "Proceed" button, the new file will replace the existing file
        3)   done: the user will be notified that the file has been updated, and they
             can safely close the dialog

    NB: an error is raised if the Exchange Record state changes while the wizard is
    open as soon as the user clicks the "Proceed" button (which is, before the Exchange
    Record file is replaced or its content updated).

    To override and customize the wizard behavior:
    - add new modes and states
    - override ``_get_next_state_values_from_setup()`` to handle your new mode
    - add methods ``_execute_{state}()`` and ``_get_next_state_values_from_{state}()``
    - update the wizard form view accordingly
    """

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
            ("replace", "Replace"),
            ("edit", "Edit"),
            ("done", "Done"),
        ],
        default="setup",
        required=True,
        readonly=True,
    )
    mode = fields.Selection(
        selection=[
            ("edit_in_place", "Edit file"),
            ("download_and_replace", "Replace file"),
        ],
        default="edit_in_place",
    )

    # ``mode == "replace"``
    new_file = fields.Binary(attachment=False)
    new_filename = fields.Char()

    # ``mode == "edit"``
    file_content = fields.Text()
    ace_mode = fields.Selection(
        selection=[
            # These values are defined here:
            # https://github.com/odoo/odoo/blob/625eb316/addons/web/static/src/core/code_editor/code_editor.js#L65
            ("javascript", "JavaScript/JSON"),
            ("xml", "XML/HTML"),
            ("qweb", "QWeb"),
            ("scss", "SCSS"),
            ("python", "Python"),
            # "txt" is added to allow plain text updates if needed
            ("txt", "Plain text"),
        ],
        default="txt",
    )

    # UI
    button_proceed_invisible = fields.Boolean(
        compute="_compute_button_proceed_invisible"
    )
    button_cancel_invisible = fields.Boolean(compute="_compute_button_cancel_invisible")
    button_close_invisible = fields.Boolean(compute="_compute_button_close_invisible")

    # ----------------------------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------------------------

    def open_file_manager_wizard(self):
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
        is returned (depending on ``as_bytes``).
        """
        record = self.exchange_record_id
        try:
            return record._get_file_content(binary=binary, as_bytes=as_bytes)
        except Exception as exc:
            if raise_exc:
                raise UserError(self.env._("The file cannot be read")) from exc
            return b"" if as_bytes else ""

    # ----------------------------------------------------------------------------------
    # Ace mode tools
    # ----------------------------------------------------------------------------------

    @api.model
    def _get_extension_to_ace_mode_map(self) -> collections.defaultdict[str, str]:
        """Return a mapping of file extensions to ace modes

        The returned mapping is incomplete, can be extended by inheriting modules
        """
        return collections.defaultdict(
            str,
            {
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
            },
        )

    def _guess_ace_mode(self) -> str:
        """Return the ace mode (one of `ace_mode` values) best fitting the file

        First, we try to retrieve the extension from the original EDI Exchange Record
        filename or its EDI Exchange Type, and map it to the proper ace mode.
        If no match is found, we guess by looking at EDI Exchange Record content.
        """
        self.ensure_one()
        return (
            self._guess_ace_mode_from_exchange_record()
            or self._guess_ace_mode_from_exchange_type()
            or self._guess_ace_mode_from_exc_record_file_content()
            or "txt"  # default fallback
        )

    def _guess_ace_mode_from_exchange_record(self) -> str:
        """Try guessing from the Exchange Record filename extension"""
        extension = os.path.splitext(str(self.exchange_record_filename or ""))[1]
        return self._guess_ace_mode_from_extension(extension)

    def _guess_ace_mode_from_exchange_type(self) -> str:
        """Try guessing from the Exchange Type extension"""
        extension = str(self.exchange_record_id.type_id.exchange_file_ext or "")
        return self._guess_ace_mode_from_extension(extension)

    def _guess_ace_mode_from_extension(self, extension: str) -> str:
        """Try guessing from the provided extension"""
        return self._get_extension_to_ace_mode_map()[extension.lstrip(".").lower()]

    def _guess_ace_mode_from_exc_record_file_content(self) -> str:
        """Try guessing from the Exchange Record content"""
        content = self._read_record_file_content()
        mode = ""
        if first_char := content.lstrip()[:1]:
            if first_char == "<":
                mode = "xml"
            elif first_char in ("{", "["):
                try:
                    json.loads(content)
                    mode = "javascript"
                except ValueError:  # pylint: disable=except-pass
                    pass
        return mode

    # ----------------------------------------------------------------------------------
    # File encoding config (from Exchange Record's Type)
    # ----------------------------------------------------------------------------------

    def _get_record_type_encoding(self) -> str:
        """Retrieves the Exc Type expected text encoding"""
        return self.exchange_record_id.type_id.encoding or "UTF-8"

    def _get_record_type_encoding_error_handler(self) -> str:
        """Retrieves the Exc Type expected text encoding error handler

        NB: the handler depends on the exchange direction
        """
        exc_type = self.exchange_record_id.type_id
        if exc_type.direction == "input":
            handler = exc_type.encoding_in_error_handler
        else:
            handler = exc_type.encoding_out_error_handler
        return handler or "strict"

    # ----------------------------------------------------------------------------------
    # States/workflow
    # ----------------------------------------------------------------------------------

    def button_proceed(self):
        """Proceeds to the next state"""
        self._proceed()
        return self.open_file_manager_wizard()

    def _proceed(self):
        """Executes actions related to wizard current state and moves to the next"""
        self.ensure_one()
        state = self.state
        if state == "done":
            raise UserError(self.env._("Nothing left to do, please close the dialog"))
        self.exchange_record_id._check_can_use_file_manager()
        getattr(self, f"_execute_{state}")()
        if vals := getattr(self, f"_get_next_state_values_from_{state}")():
            self.write(vals)

    def _execute_setup(self):
        """Executes actions related to the wizard ``setup`` state"""
        pass  # Nothing to do, kept as hook

    def _get_next_state_values_from_setup(self) -> api.ValuesType:
        """Proceeds from ``setup`` state to the next one according to ``mode``"""
        if not self.mode:
            raise UserError(self.env._("Please select a 'Mode' option to proceed"))
        elif self.mode == "edit_in_place":
            return {
                "state": "edit",
                "file_content": self._read_record_file_content(),
                "ace_mode": self._guess_ace_mode(),
            }
        elif self.mode == "download_and_replace":
            return {"state": "replace"}
        else:
            raise NotImplementedError(f"Mode '{self.mode}' not supported at setup")

    def _execute_edit(self):
        """Edits the file content of the Exchange Record"""
        record = self.exchange_record_id
        encoding = self._get_record_type_encoding()
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

    def _get_next_state_values_from_edit(self) -> api.ValuesType:
        """Proceeds from ``edit`` state to ``done``"""
        # Clear the ``file_content`` after the Exc Rec file has been updated
        return {"state": "done", "file_content": ""}

    def _execute_replace(self):
        """Replaces the file content of the Exchange Record"""
        if not self.new_file:
            raise UserError(self.env._("Please upload a new file"))
        record = self.exchange_record_id
        record._check_can_use_file_manager()
        # Check whether the new file is consistent w/ the exchange record encoding
        # NB: a successful ``decode`` does not prove that a file was originally encoded
        # using a particular encoding. For example, ``ASCII`` bytes are valid ``UTF-8``
        # and ``ISO-8859-1``. In general, encoding cannot be reliably inferred from
        # arbitrary bytes alone. This check enforces the practical invariant that
        # matters here: the replacement file must be strictly decodable using the
        # encoding configured on the exchange type. It cannot detect every case where a
        # file was technically encoded using a different but compatible encoding.
        encoding = self._get_record_type_encoding()
        encoding_error_handler = self._get_record_type_encoding_error_handler()
        try:
            content = base64.b64decode(self.new_file, validate=True)
            content.decode(encoding, errors=encoding_error_handler)
        except (binascii.Error, UnicodeError, LookupError) as exc:
            raise UserError(
                self.env._(
                    "The file is not consistent with the exchange type encoding"
                    " %(encoding)s and error handler %(handler)s: %(error)s",
                    encoding=encoding,
                    handler=encoding_error_handler,
                    error=exc,
                )
            ) from exc
        # The filename of the exchange record is intentionally left untouched
        record.exchange_file = self.new_file
        record.message_post(body=self.env._("File replaced through file manager."))

    def _get_next_state_values_from_replace(self) -> api.ValuesType:
        """Proceeds from ``replace`` state to ``done``"""
        # Clear the ``new_file`` after the Exc Rec file has been replaced
        return {"state": "done", "new_file": False}

    # ----------------------------------------------------------------------------------
    # Other buttons and UI stuff
    # ----------------------------------------------------------------------------------

    @api.depends("state", "mode")
    def _compute_button_proceed_invisible(self):
        """Computes whether the "Proceed" button is invisible"""
        for wiz in self:
            wiz.button_proceed_invisible = wiz.state == "done" or (
                wiz.state == "setup" and not wiz.mode
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
