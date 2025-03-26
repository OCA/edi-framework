# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from .. import utils


class EDIStorageSend:
    def _send(self, exchange_record):
        filedata = exchange_record.exchange_file
        path = self._get_remote_file_path(exchange_record, "pending")
        utils.add_file(exchange_record.backend_id.storage_id, path.as_posix(), filedata)
        # TODO: delegate this to generic storage backend
        # except paramiko.ssh_exception.AuthenticationException:
        #     # TODO this exc handling should be moved to sftp backend IMO
        #     error = _("Authentication error")
        #     state = "error_on_send"
        # TODO: catch other specific exceptions
        # this will swallow all the exceptions!
        return True
