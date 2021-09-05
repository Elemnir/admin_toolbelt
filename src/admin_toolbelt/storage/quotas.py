"""
    admin_toolbelt.storage.quotas
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module provides an interface for working with quotas on various
    filesystems. The classes in this module implement the interface for
    both setting quotas and gathering current usage information.
"""

from ..utils import run_cmd

class FilesystemQuota(object):
    """The base class for filesystem quota management. Supports ext
    filesystems and defines the interface that subclasses should use to
    support other filesystems.
    """
    supported_filesystems = ['ext3', 'ext4']
    idtype_flags = {
        'user': '-u',
        'group': '-g',
    }

    def __init__(self, filesystem, identity, idtype='user', 
            block_soft='0', block_hard='0', inode_soft='0', inode_hard='0'):
        if idtype not in self.idtype_flags:
            raise ValueError('Invalid idtype "{0}". Valid values are "{1}"'.format(
                idtype, ', '.join(idtype_flags.keys())
            ))

        self._queried = False
        self.fsname, self.identity, self.idtype = filesystem, identity, idtype
        self._bsoft, self._bhard, self._bused = block_soft, block_hard, None
        self._isoft, self._ihard, self._iused = inode_soft, inode_hard, None

    def _query_if_needed(self):
        if not self._queried:
            self.query()
            self._queried = True

    @property
    def bused(self):
        self._query_if_needed()
        return self._bused

    @property
    def bsoft(self):
        self._query_if_needed()
        return self._bsoft

    @property
    def bhard(self):
        self._query_if_needed()
        return self._bhard

    @property
    def iused(self):
        self._query_if_needed()
        return self._iused

    @property
    def isoft(self):
        self._query_if_needed()
        return self._isoft

    @property
    def ihard(self):
        self._query_if_needed()
        return self._ihard

    def get_command(self):
        return '/sbin/quota {1} {2}'.format(self.idtype_flags[self.idtype], self.identity)

    def set_command(self):
        return ' '.join([
            '/sbin/setquota', self.idtype_flags[self.idtype], self.identity, 
            self._bsoft, self._bhard, self._isoft, self._ihard, self.fsname
        ])

    def parse(self, stdout):
        bused, bsoft, bhard, iused, isoft, ihard = None, '0', '0', None, '0', '0'
        return bused, bsoft, bhard, iused, isoft, ihard

    def query(self):
        self._bused, self._bsoft, self._bhard, self._iused, self._isoft, self._ihard = self.parse(
            run_cmd(self.get_command())
        )

    def apply(self):
        run_cmd(self.set_command())


class LustreQuota(FilesystemQuota):
    supported_filesystems = ['lustre']
    idtype_flags = {
        'user': '-u',
        'group': '-g',
        'project': '-p',
    }

    def get_command(self):
        return '/bin/lfs quota -q {0} {1} {2}'.format(
            self.idtype_flags[self.idtype], self.identity, self.fsname
        )
    
    def parse(self, stdout):
        fsname, bused, bsoft, bhard, btime, iused, isoft, ihard, itime = stdout.split()
        return bused, bsoft, bhard, iused, isoft, ihard

    def set_command(self):
        return (
            '/bin/lfs setquota {0} {1}' +
            ' --block-softlimit {2} --block-hardlimit {3}' +
            ' --inode-softlimit {4} --inode-hardlimit {5}' +
            ' {6}'
        ).format(
            self.idtype_flags[self.idtype], self.identity,
            self._bsoft, self._bhard, self._isoft, self._ihard,
            self.fsname
        )

    
class XfsQuota(FilesystemQuota):
    supported_filesystems = ['xfs']
    idtype_flags = {
        'user': '-u',
        'group': '-g',
        'project': '-p',
    }

    def set_command(self):
        return (
            "/usr/sbin/xfs_quota -x -c" +
            " 'limit {0} bsoft={1} bhard={2} isoft={3} ihard={4} {5}' {6}"
        ).format(
            self.idtype_flags[self.idtype],
            self._bsoft if str(self._bsoft) != '0' else 'unlimited', 
            self._bhard if str(self._bhard) != '0' else 'unlimited', 
            self._isoft if str(self._isoft) != '0' else 'unlimited', 
            self._ihard if str(self._ihard) != '0' else 'unlimited',
            self.identity, self.fsname
        )


class ZfsQuota(FilesystemQuota):
    supported_filesystems = ['zfs']
    idtype_flags = {
        'user': 'user',
        'group': 'group',
    }
    
    def get_command(self):
        return (
            '/sbin/zfs get -H -p -o value' +
            ' {0}quota@{1},{0}used@{1},{0}objquota@{1},{0}objused@{1} {2}'
        ).format(self.idtype, self.identity, self.fsname)

    def parse(self, stdout):
        bused, bhard, iused, ihard = stdout.split()
        return bused, bhard, bhard, iused, ihard, ihard

    def set_command(self):
        return '/sbin/zfs set {0}quota@{1}={3} {0}objquota@{1}={4} {2}'.format(
            self.idtype, self.identity, self.fsname,
            self._bhard if str(self._bhard) != '0' else 'none', 
            self._ihard if str(self._ihard) != '0' else 'none',
        )
