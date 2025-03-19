# Copyright 2024 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

import base64
import os
import re


def add_file(storage, path, filedata, binary=False):
    data = filedata
    if not binary:
        data = base64.b64decode(filedata)
    relative_path = path
    fs = storage.fs
    path = relative_path.split(fs.sep)[:-1]
    if not fs.exists(fs.sep.join(path)):
        fs.makedirs(fs.sep.join(path))
    with fs.open(relative_path, "wb") as f:
        f.write(data)


def find_files(storage, pattern, relative_path="", **kw) -> list[str]:
    result = []
    fs = storage.fs
    relative_path = relative_path or fs.root_marker
    if not fs.exists(relative_path):
        return []
    regex = re.compile(pattern)
    for file_path in fs.ls(relative_path, detail=False):
        # fs.ls returns a relative path
        if regex.match(os.path.basename(file_path)):
            result.append(file_path)
    return result


def get_file(storage, path, binary=False):
    data = storage.fs.read_bytes(path)
    if not binary and data:
        data = base64.b64encode(data)
    return data


def list_files(storage, relative_path="", pattern=False):
    fs = storage.fs
    relative_path = relative_path or fs.root_marker
    if not fs.exists(relative_path):
        return []
    if pattern:
        relative_path = fs.sep.join([relative_path, pattern])
        return fs.glob(relative_path)
    return fs.ls(relative_path, detail=False)


def move_files(storage, files, destination_path, **kw):
    for file_path in files:
        storage.fs.move(
            file_path,
            storage.fs.sep.join([destination_path, os.path.basename(file_path)]),
            **kw,
        )
