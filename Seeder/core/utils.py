"""
    Shared utilities
"""

def merge_dicts(x, y):
    """
    Given two dicts, merge them into a new dict as a shallow copy.
    """
    z = x.copy()
    z.update(y)
    return z


def percentage(part, whole):
    """
    Simple utility for calculating percentages
    """
    return 100 * float(part) / float(whole)


def dict_diff(first, second):
    """
    >>> dict_diff({'a':'b', 'c':1}, {'a':'c', 'c':1})
    {'a': {'original':'b', 'changed': 'c'}

    :type first: dict
    :type second: dict
    :rtype dict
    """
    diff = {}
    keys = set(first.keys() + second.keys())
    for key in keys:
        first_value = first.get(key)
        second_value = second.get(key)
        if first_value != second_value:
            diff[key] = {
                'original': first_value,
                'changed': second_value
            }
    return diff
