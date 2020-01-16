"""
    admin_toolbelt.storage
    ~~~~~~~~~~~~~~~~~~~~~

    This module provides functions for working with filesystems, including
    functions for generating set-quota commands for various filesystems and
    creating user directories.
"""

import datetime
import os
import shutil
import logging

import dramatiq

__all__ = [
    'get_mount_point',
    'get_quota_cmd',
    'set_quota_cmd',
    'create_path',
    'UnusedPeriodPolicy',
    'visit_dirs'
]


def get_mount_point(path):
    """Returns the path of the filesystem on which the given path exists."""
    path = os.path.realpath(os.path.abspath(path))
    while path != os.path.sep:
        if os.path.ismount(path):
            return path
        path = os.path.abspath(os.path.join(path, os.pardir))
    return path


def get_quota_cmd(username, filesystem, fstype='xfs'):
    """Returns a shell command for getting a user's quota."""
    if fstype in ['xfs', 'ext']:
        return 'quota -u {0}'.format(username)
    if fstype == 'lustre':
        return 'lfs quota -q -h -u {0} {1}'.format(username, filesystem)
    if fstype == 'zfs':
        return 'zfs get userquota@{0} {1}'.format(username, filesystem)


def set_quota_cmd(username, filesystem, fstype='xfs', usage=None, inode=None):
    """Returns a shell command for setting a user's quota."""
    if fstype == 'ext':
        return 'setquota -u {0} {1} {1} {2} {2} {3}'.format(
            username, inode if inode else 0, usage if usage else 0, filesystem
        )

    if fstype == 'lustre':
        cmd = 'lfs setquota --user {0}'.format(username)
        if usage:
            cmd += ' --block-softlimit {0} --block-hardlimit {0}'.format(usage)
        if inode:
            cmd += ' --inode-softlimit {0} --inode-hardlimit {0}'.format(inode)
        return cmd + ' {0}'.format(filesystem)

    if fstype == 'xfs':
        cmd = "xfs_quota -x -c 'limit"
        if usage:
            cmd += ' bsoft={0} bhard={0}'.format(usage)
        if inode:
            cmd += ' isoft={0} ihard={0}'.format(inode)
        return cmd + " {0}' {1}".format(username, filesystem)

    if fstype == 'zfs':
        return 'zfs set userquota@{0}={1} {2}'.format(
            username, usage if usage else 'none', filesystem
        )


@dramatiq.actor
def create_path(path, owner, group, fstype, mode=0o700, copy_files=[], usage_quota=None, inode_quota=None):
    """Creates a directory with the given attributes if it doesn't exist."""
    if not os.path.exists(path):
        logging.debug('%s: Path does not exist, creating...', path)
        os.mkdir(path)

        for src, dest in copy_files:
            shutil.copyfile(src, os.path.join(path, dest))

        cmd = 'chown -R {0}:{1} {2}'.format(owner, group, path)
        logging.debug('\tRunning: %s', cmd)
        os.system(cmd)
        os.chmod(path, mode)
        
        if usage_quota or inode_quota:
            cmd = set_quota_cmd(
                owner, get_mount_point(path), fstype=fstype, usage=usage_quota, inode=inode_quota
            )
            logging.debug('\tRunning: %s', cmd)
            os.system(cmd)

        logging.debug('... done.')


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
