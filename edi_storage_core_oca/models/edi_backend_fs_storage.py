# Copyright 2025 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models

from ..abstracts.base import EDIStorageMixin
from ..abstracts.check import EDIStorageCheckMixin
from ..abstracts.listener import (
    EdiStorageListenerAbstract,
)
from ..abstracts.receive import EDIStorageReceive
from ..abstracts.send import EDIStorageSend


class EdiBackendFsStorage(
    EDIStorageMixin,
    EDIStorageCheckMixin,
    EdiStorageListenerAbstract,
    EDIStorageReceive,
    EDIStorageSend,
    models.AbstractModel,
):
    """
    Abstract to manage fs storage operations on EDI backend
    """

    _name = "edi.backend.fs.storage"
    _description = "EDI Backend storage"
