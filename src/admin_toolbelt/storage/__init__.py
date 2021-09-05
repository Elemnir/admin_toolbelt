"""
    admin_toolbelt.storage
    ~~~~~~~~~~~~~~~~~~~~~

    This module provides functions for working with filesystems, including
    functions for generating set-quota commands for various filesystems and
    creating user directories.
"""

import collections
import datetime
import os
import shutil
import logging

from ..utils import run_cmd

from .mounts import get_mount_info
from .quotas import FilesystemQuota, LustreQuota, XfsQuota, ZfsQuota

__all__ = [
    'FilesystemQuota',
    'LustreQuota',
    'XfsQuota',
    'ZfsQuota',
    'get_mount_info',
    'create_path',
    'UnusedPeriodPolicy',
    'visit_dirs'
]

def create_path(path, owner, group, mode=0o700, copy_files=[], usage_quota=None, inode_quota=None):
    """Creates a directory with the given attributes if it doesn't exist."""
    logging.info(('create_path(' + 
        'path={}, owner={}, group={}, mode={}, copy_files={}, usage_quota={}, inode_quota={}' + 
        ')').format(path, owner, group, mode, copy_files, usage_quota, inode_quota)
    )
    if not os.path.exists(path):
        logging.info('%s: Path does not exist, creating...', path)
        mnt = get_mount_info(path)
        os.mkdir(path)

        for src, dest in copy_files:
            shutil.copyfile(src, os.path.join(path, dest))

        run_cmd('chown -R {0}:{1} {2}'.format(owner, group, path))
        os.chmod(path, mode)
        
        if usage_quota or inode_quota:
            run_cmd(set_quota_cmd(
                owner, mnt.file, fstype=mnt.vfstype, usage=usage_quota, inode=inode_quota
            ))

        logging.info('... done.')


class UnusedPeriodPolicy(object):
    """Instances of this policy return True if the file at the given path
    hasn't been accessed or modified within the given time period, which 
    should be an instance of ``datetime.timedelta``.
    """
    def __init__(self, period=datetime.timedelta(days=30)):
        self.period = period

    def __call__(self, path):
        cutoff = datetime.datetime.now() - self.period
        st = os.lstat(path)
        return (
            cutoff < datetime.datetime.fromtimestamp(st.st_atime) and
            cutoff < datetime.datetime.fromtimestamp(st.st_mtime)
        )


def visit_dirs(dirs, policy=UnusedPeriodPolicy(), action=print):
    """Provided a list of directories, ``dirs``, recursively searches for files 
    for which the provided policy returns True, and execute the given action on
    them. ``policy`` and ``action`` should be callable objects accepting a file 
    path as their only argument. By default, prints the path of all files that 
    haven't been accessed or modified in over 30 days.
    
    For example, to institute a purge of any files in the directories over 30 
    days old, you could set ``action=os.remove``.
    """
    for dname in dirs:
        for path, subdirs, files in os.walk(dname):
            for fname in files:
                if policy(os.path.join(path,fname)):
                    action(os.path.join(path,fname))
