===========
 Changelog
===========

Version 0.4.0
-------------

- Adding ``contrib`` subpackage for collecting optional components with their
  own dependencies.

- Adding ``contrib.login_records`` Django App for recording user login history.

Version 0.3.0
-------------

- Adding ``utils.run_cmd`` to streamline subprocess calls

- Replacing ``storage.get_mount_point`` with ``storage.get_mount_info`` which 
  elides several bugs and provides more information on the mount point.

- Removing ``fstype`` from the parameters of ``storage.create_path`` because
  this can be inferred using the new information provided by 
  ``storage.get_mount_info``.
 
Version 0.2.0
-------------

- Lots of bug fixes and testing for the LdapClient and some restructuring of 
  the dramatiq components into a separate module.

Version 0.1.0
-------------

- First public release.
