"""
Dictionary utilities for SmartSeeds.

Provides utilities for dict manipulation used by decorators.
"""

from typing import Any, Dict


def dictExtract(mydict, prefix, pop=False, slice_prefix=True, is_list=False):
    """Return a dict of the items with keys starting with prefix.

    :param mydict: sourcedict
    :param prefix: the prefix of the items you need to extract
    :param pop: removes the items from the sourcedict
    :param slice_prefix: shortens the keys of the output dict removing the prefix
    :param is_list: reserved for future use (currently not used)
    :returns: a dict of the items with keys starting with prefix"""

    # FIXME: the is_list parameter is never used.

    lprefix = len(prefix) if slice_prefix else 0

    cb = mydict.pop if pop else mydict.get
    reserved_names = ['class']
    return dict([(k[lprefix:] if not k[lprefix:] in reserved_names else '_%s' % k[lprefix:], cb(k)) for k in list(mydict.keys()) if k.startswith(prefix)])
