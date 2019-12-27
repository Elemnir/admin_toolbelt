"""
    admin_toolbelt.utils
    ~~~~~~~~~~~~~~~~~~~

    This module provides a space for small functions built on top of the 
    standard library. Includes things like accurately getting the user's
    username and providing an equivalent to ``sort -h``.
"""
import os
import pwd
import re

__all__ = [
    'first_existing',
    'get_username',
    'human_numeric_sort',
]


def first_existing(d, keys):
    """Returns the value of the first key in keys which exists in d."""
    for key in keys:
        if key in d:
            return d[key]
    return None


def get_username():
    """Returns the current user's username based on uid."""
    return pwd.getpwuid(os.getuid()).pw_name


def human_numeric_sort(lines, column=0):
    """Sorts the given lines numerically on the chosen column, supports suffixes 
    such as '15k' or '1G'. 
    """
    def key_func(line):
        items = line.split()
        try:
            item = items[column]
        except:
            return -1
        
        if re.search(r'^\d+$', item):
            return int(item)
            
        m = re.search(r'(\d+)([kmgtpKMGTP])', item)
        if m:
            v, s = int(m.group(1)), m.group(2)
            if s in 'kK':
                v *= 1000
            if s in 'mM':
                v *= 1000000
            if s in 'gG':
                v *= 1000000000
            if s in 'tT':
                v *= 1000000000000
            if s in 'pP':
                v *= 1000000000000000
            return v
        return -1
        
    return sorted(lines, key=key_func)

