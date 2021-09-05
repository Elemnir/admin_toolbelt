"""
    admin_toolbelt.storage.mounts
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module primarily provides a mechanism for getting information on the
    filesystem on which a given path resides. 
"""
import collections
import os

Mount = collections.namedtuple("Mount", "spec file vfstype mntops freq passno")
mount_info = [Mount(*line.split()) for line in open("/proc/mounts").readlines()]


def get_mount_info(path):
    """Returns the mount info of the filesystem on which the given path exists."""
    path = os.path.realpath(os.path.abspath(path))
    while True:
        for mnt in mount_info:
            if path == mnt.file:
                return mnt
        next = os.path.abspath(os.path.join(path, os.pardir))
        if next == path:
            break
        path = next

    raise OSError("Invalid path")
